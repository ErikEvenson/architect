# Kubernetes Networking

## Checklist

- [ ] Choose Service type for each workload: ClusterIP (internal), NodePort (development/legacy), LoadBalancer (external, cloud-integrated), ExternalName (DNS CNAME alias)
- [ ] Evaluate Ingress vs Gateway API: Ingress is stable but limited (HTTP/HTTPS only, no header-based routing); Gateway API is the successor with richer routing, multi-tenancy, and protocol support
- [ ] Select and deploy an ingress controller: NGINX Ingress, Traefik, HAProxy, Contour, Emissary, or cloud-provider native (AWS ALB, GCP GCLB)
- [ ] Design NetworkPolicy rules: default-deny all ingress/egress per namespace, then allow specific traffic flows; verify CNI supports NetworkPolicies
- [ ] Evaluate CNI plugin: Calico (policy + BGP), Cilium (eBPF, policy, observability, service mesh), Flannel (simple overlay), AWS VPC CNI, Azure CNI, GKE Dataplane v2
- [ ] Plan DNS architecture: CoreDNS configuration, ndots setting optimization, DNS caching (NodeLocal DNSCache for large clusters)
- [ ] Assess service mesh requirements: Istio (feature-rich, complex), Linkerd (lightweight, simple), Cilium service mesh (eBPF-based, no sidecars)
- [ ] Configure external DNS controller to automatically create DNS records for Services and Ingress resources
- [ ] Plan IP address management: pod CIDR sizing (plan for growth), service CIDR, avoiding conflicts with VPC/corporate networks
- [ ] Evaluate MetalLB for bare-metal LoadBalancer service support (L2 mode for simple setups, BGP mode for production)
- [ ] Design egress traffic strategy: egress gateways, NAT, or direct pod IP egress; consider implications for firewall rules at destination
- [ ] Configure appropriate session affinity settings for stateful client connections (service.spec.sessionAffinity, consistent hash in service mesh)
- [ ] Plan TLS termination: at ingress controller, at service mesh sidecar (mTLS), or at application; evaluate cert-manager for automated certificate lifecycle

## Why This Matters

Kubernetes networking is the most complex and consequential area of cluster architecture. Every pod gets a routable IP address, and the choice of CNI plugin determines network performance, security policy enforcement capabilities, and observability. Without NetworkPolicies, any pod can communicate with any other pod in the cluster, creating a flat network that violates least-privilege principles. The Ingress/Gateway API choice affects traffic routing flexibility, multi-team workflows, and protocol support. Service mesh adds mTLS, traffic management, and observability but introduces sidecar overhead and operational complexity. DNS misconfiguration (particularly the `ndots:5` default) causes unnecessary DNS lookups that can overwhelm CoreDNS in large clusters.

## Common Decisions (ADR Triggers)

- **Ingress vs Gateway API**: Ingress is mature and widely supported but limited to HTTP/HTTPS with basic path/host routing. Gateway API supports TCP/UDP/gRPC, header-based routing, traffic splitting, and role-oriented resource model (cluster operator manages Gateway, developers manage HTTPRoute). Prefer Gateway API for new deployments; maintain Ingress for existing workloads during migration.
- **CNI selection (Calico vs Cilium vs cloud-native)**: Calico is mature with strong NetworkPolicy support and BGP peering. Cilium uses eBPF for higher performance, richer observability (Hubble), and can replace kube-proxy. Cloud-native CNIs (AWS VPC CNI, Azure CNI) provide direct VPC integration but limited policy features. Choose Cilium for performance and observability; Calico for mature BGP networking; cloud-native for simplicity in single-cloud deployments.
- **Service mesh: yes/no, which one**: Service mesh adds mTLS, traffic management (canary, circuit breaking), and observability (distributed tracing). But it adds sidecar resource overhead (100-200MB per pod), latency (1-3ms per hop), and operational complexity. Istio is feature-rich but complex. Linkerd is simpler with lower overhead. Cilium service mesh eliminates sidecars using eBPF. Skip service mesh if mTLS and traffic management are not required.
- **NetworkPolicy enforcement**: Not all CNIs enforce NetworkPolicies (Flannel does not). Default-deny policies are recommended but break existing workloads if applied without audit. Use Cilium's policy audit mode or Calico's staged policies to preview enforcement before activating. Plan for egress policies (often overlooked) in addition to ingress.
- **MetalLB vs external load balancer (bare-metal)**: MetalLB provides LoadBalancer-type Services on bare-metal but has limitations (L2 mode has single-node failover, BGP mode requires upstream router configuration). External load balancers (F5, HAProxy, Kemp) provide richer features but require separate management. Use MetalLB BGP mode for production bare-metal; L2 mode for development.
- **NodeLocal DNSCache**: Default CoreDNS handles all cluster DNS, creating a bottleneck at scale. NodeLocal DNSCache runs a caching DNS agent on every node, reducing CoreDNS load and DNS latency. Enable for clusters with >100 nodes or DNS-heavy workloads.

## Reference Architectures

### Production Ingress Architecture
```
[External DNS] --> [Cloud Load Balancer (L4)]
                          |
                   [Ingress Controller (NGINX/Contour)]
                   - TLS termination (cert-manager)
                   - Rate limiting
                   - WAF rules (ModSecurity/Coraza)
                          |
                   [Gateway API HTTPRoute]
                   - Path-based routing
                   - Header-based routing
                   - Traffic splitting (canary)
                          |
               +----------+----------+
               |          |          |
          [Service A] [Service B] [Service C]
          (ClusterIP)  (ClusterIP)  (ClusterIP)
```
L4 cloud load balancer forwards to ingress controller pods (deployed as DaemonSet or Deployment with anti-affinity). Cert-manager provisions TLS certificates from Let's Encrypt or internal CA. Gateway API HTTPRoutes define routing rules owned by application teams. External DNS controller creates DNS records automatically.

### Network Security (Defense in Depth)
```
[Layer 1: NetworkPolicy (CNI)]
  - Default deny all ingress/egress per namespace
  - Allow specific pod-to-pod flows
  - Allow DNS egress to kube-system
  - Allow egress to specific external CIDRs

[Layer 2: Service Mesh mTLS (Istio/Linkerd)]
  - Mutual TLS between all pods
  - AuthorizationPolicy for L7 rules
  - Identity-based access (SPIFFE)

[Layer 3: Ingress Controller]
  - WAF rules
  - Rate limiting per client
  - TLS with minimum version 1.2

[Layer 4: Egress Gateway]
  - Controlled egress to external services
  - SNI-based filtering
  - Audit logging of outbound connections
```
Defense in depth with NetworkPolicies for L3/L4 isolation, service mesh for L7 identity-based authorization, ingress controller for external traffic filtering, and egress gateways for outbound traffic control. Each layer operates independently, so a failure in one still provides protection from others.

### DNS Architecture for Large Clusters
```
[Pod DNS Query (ndots:2 optimized)]
        |
  [NodeLocal DNSCache (per-node)]
  - Cache hits: <1ms response
  - Cache misses: forward to CoreDNS
        |
  [CoreDNS (cluster-level)]
  - Kubernetes plugin: service/pod DNS
  - Forward plugin: external DNS
  - Autopath plugin: reduce search domain lookups
        |
  [Upstream DNS (VPC/Corporate)]
```
Reduce ndots from default 5 to 2 in pod DNS config to minimize unnecessary search domain lookups. NodeLocal DNSCache on each node absorbs repetitive queries. CoreDNS with autopath plugin optimizes search domain resolution. This architecture reduces DNS latency from 5-10ms to <1ms for cached queries and eliminates CoreDNS as a scaling bottleneck.
