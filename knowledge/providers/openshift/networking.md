# OpenShift Networking

## Checklist

- [ ] Select CNI plugin: OVN-Kubernetes (default since OCP 4.12+) vs OpenShift SDN (legacy, deprecated)
- [ ] Design cluster network CIDR, service network CIDR, and host prefix (cannot be changed post-install)
- [ ] Configure NetworkPolicy resources for namespace isolation (default-deny ingress/egress per namespace)
- [ ] Set up ingress: OpenShift Routes (HAProxy-based IngressController) with TLS termination strategy (edge, passthrough, re-encrypt)
- [ ] Plan external load balancing: cloud LB (NLB/ALB on AWS, Azure LB), MetalLB (bare metal/vSphere), F5 BIG-IP
- [ ] Configure egress controls: EgressNetworkPolicy (OpenShift SDN), EgressFirewall (OVN-K), EgressIP for predictable source IPs
- [ ] Evaluate Multus CNI for workloads requiring multiple network interfaces (SR-IOV, MACVLAN, bridge)
- [ ] Deploy OpenShift Service Mesh (Istio-based, managed by `ServiceMeshControlPlane` CR) if mTLS or advanced traffic management is needed
- [ ] Install cert-manager operator for automated TLS certificate lifecycle (Let's Encrypt, Venafi, internal CA)
- [ ] Configure DNS operator: cluster DNS (CoreDNS), custom DNS forwarding for split-horizon or hybrid cloud DNS
- [ ] Enable network observability operator for eBPF-based flow collection and traffic visualization
- [ ] Plan for IPv4/IPv6 dual-stack or single-stack based on enterprise network requirements
- [ ] Define IngressController sharding for multi-tenant or multi-domain routing (route labels, namespace selectors)

## Why This Matters

Networking decisions in OpenShift are among the most consequential and least reversible. The CNI plugin, cluster CIDR, and service CIDR are set at install time and cannot be changed without rebuilding the cluster. OVN-Kubernetes is now the strategic direction -- it supports features that OpenShift SDN lacks (EgressFirewall CR, AdminNetworkPolicy, hardware offload, dual-stack). Migrating from OpenShift SDN to OVN-Kubernetes is supported but disruptive (requires node reboots and brief pod network interruption).

OpenShift Routes predate Kubernetes Ingress and remain the primary ingress mechanism. Routes support TLS passthrough (critical for end-to-end mTLS), re-encrypt (TLS termination at the router with a new TLS connection to the backend), and edge termination. The default HAProxy-based IngressController can be scaled horizontally, sharded by route labels or namespaces, and configured with custom timeouts, rate limits, and HSTS policies.

Egress control is critical for compliance. EgressFirewall CRDs allow namespace-level allow/deny rules for external destinations by IP or DNS. EgressIP assigns a predictable source IP to pods in a namespace, enabling firewall whitelisting by external partners. Without egress controls, any pod can reach any external endpoint.

Multus allows pods to have multiple network interfaces -- essential for telco workloads (data plane on SR-IOV, control plane on OVN), legacy application integration (direct VLAN attachment), and storage networks. The `NetworkAttachmentDefinition` CRD defines additional networks.

## Common Decisions (ADR Triggers)

- **OVN-Kubernetes vs OpenShift SDN**: OVN-K is the default and strategic choice. OpenShift SDN is deprecated. New clusters should use OVN-K. Migration from SDN to OVN-K is supported in-place but requires planning.
- **Route-based ingress vs Kubernetes Ingress vs Gateway API**: Routes are OpenShift-native and fully supported. Kubernetes Ingress is supported via an annotation bridge to Routes. Gateway API is tech preview. Routes are recommended unless portability to non-OpenShift clusters is required.
- **IngressController sharding**: Single default IngressController vs multiple sharded controllers. Sharding is needed for multi-domain TLS, workload isolation (internal vs external), or custom router sizing.
- **Service Mesh adoption**: Full mesh (sidecar per pod) vs partial mesh (selected namespaces) vs no mesh. Service mesh adds operational complexity (sidecar injection, control plane management) but provides mTLS, traffic shifting, and observability. Consider ambient mesh (sidecar-less) when available.
- **Network policy model**: Default-deny with explicit allow vs default-allow. Default-deny is recommended for production and required for many compliance frameworks (PCI-DSS, HIPAA).
- **MetalLB vs external load balancer**: MetalLB (L2 or BGP mode) is appropriate for bare metal and some virtualized environments. External LB (F5, HAProxy, cloud LB) is preferred when existing LB infrastructure exists.

## Version Notes

| Feature | OCP 4.12 | OCP 4.14 | OCP 4.16 |
|---|---|---|---|
| OpenShift SDN | Supported | Deprecated | Removed |
| OVN-Kubernetes | GA (default) | GA (default) | GA (default) |
| Gateway API | Tech Preview | Tech Preview | GA |
| Network Observability Operator | GA (1.0) | GA (1.4) | GA (1.6) |
| AdminNetworkPolicy | Not available | Tech Preview | GA |
| Egress QoS (OVN-K) | Not available | Tech Preview | GA |
| IPv4/IPv6 dual-stack | GA | GA | GA |
| Hardware offload (OVN-K) | Tech Preview | GA | GA |

**Key migration notes:**
- OCP 4.12 was the first release where OVN-Kubernetes became the default CNI for new installations. OpenShift SDN remained available but migration to OVN-K was recommended.
- OCP 4.14 formally deprecated OpenShift SDN. In-place migration from SDN to OVN-K was supported but required node reboots.
- OCP 4.16 removed OpenShift SDN entirely. Clusters must migrate to OVN-Kubernetes before upgrading to 4.16.
- Gateway API moved to GA in 4.16, providing a portable alternative to OpenShift Routes for ingress configuration.
- AdminNetworkPolicy (cluster-scoped network policy for platform teams) reached GA in 4.16, enabling platform-wide baseline rules without per-namespace NetworkPolicy objects.

## Reference Architectures

- **Enterprise multi-tenant**: OVN-Kubernetes, default-deny NetworkPolicy per namespace, EgressFirewall per namespace, sharded IngressControllers (internal + external), cert-manager with internal CA, DNS forwarding to corporate DNS.
- **Bare metal on-premises**: OVN-Kubernetes, MetalLB in BGP mode for ingress VIPs, Multus with MACVLAN for storage network, EgressIP per tenant namespace, F5 or HAProxy external LB for production ingress.
- **Telco / 5G Core**: OVN-Kubernetes with hardware offload, Multus with SR-IOV for user plane, DPDK-enabled pods, multiple IngressControllers for signaling vs management traffic, network observability for flow analysis.
- **Hybrid cloud (on-prem + AWS)**: Submariner or Skupper for cross-cluster service discovery, consistent NetworkPolicy across clusters, split-horizon DNS with external-dns operator, VPN or Direct Connect for cluster-to-cluster communication.
- **Zero-trust network**: Service mesh with strict mTLS enforcement, default-deny NetworkPolicy, EgressFirewall allowing only approved external endpoints, network observability for anomaly detection, AdminNetworkPolicy for platform-wide baseline rules.
