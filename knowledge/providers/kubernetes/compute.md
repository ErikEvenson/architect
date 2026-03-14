# Kubernetes Compute

## Checklist

- [ ] Choose appropriate workload controller: Deployment (stateless), StatefulSet (stateful, ordered), DaemonSet (per-node), Job (run-to-completion), CronJob (scheduled)
- [ ] Set resource requests (scheduling guarantee) and limits (hard cap) for CPU and memory on every container; understand the relationship to QoS classes (Guaranteed, Burstable, BestEffort)
- [ ] Configure Horizontal Pod Autoscaler (HPA) with appropriate metrics: CPU/memory (metrics-server), custom metrics (Prometheus Adapter), or external metrics (cloud provider)
- [ ] Evaluate Vertical Pod Autoscaler (VPA) for right-sizing resource requests based on observed usage; note VPA and HPA on CPU/memory are mutually exclusive
- [ ] Assess KEDA for event-driven autoscaling (queue depth, HTTP request rate, cron schedules, custom scalers) as a complement to HPA
- [ ] Design pod topology spread constraints to distribute pods across zones, nodes, or custom topology domains for high availability
- [ ] Configure pod disruption budgets (PDBs) to ensure minimum availability during voluntary disruptions (node drains, cluster upgrades, rollouts)
- [ ] Plan node affinity/anti-affinity rules: requiredDuringScheduling for hard constraints, preferredDuringScheduling for soft preferences
- [ ] Set pod anti-affinity to prevent co-scheduling of replicas on the same node or zone (critical for HA of stateful workloads)
- [ ] Configure priority classes and preemption for workload tiering (system-critical > production > batch); set at least three priority levels
- [ ] Plan init containers for setup tasks (schema migration, config generation, dependency readiness checks) that must complete before app containers start
- [ ] Design liveness, readiness, and startup probes: liveness for deadlock detection, readiness for traffic routing, startup for slow-starting containers
- [ ] Evaluate ephemeral containers for debugging running pods without restarting (kubectl debug)

## Why This Matters

Kubernetes compute primitives determine how workloads are scheduled, scaled, and maintained. Misconfigured resource requests lead to either cluster underutilization (requests too high) or OOM kills and CPU throttling (requests too low). Missing pod disruption budgets cause outages during routine operations like node drains. Incorrect autoscaling configuration leads to either over-provisioning costs or under-provisioning latency. The choice between Deployment and StatefulSet has cascading implications for storage, networking, and upgrade procedures. QoS classes determine eviction order under memory pressure: BestEffort pods (no requests/limits) are killed first, making unset resource requests a reliability risk in shared clusters.

## Common Decisions (ADR Triggers)

- **Deployment vs StatefulSet**: Deployments are for stateless workloads with interchangeable pods. StatefulSets provide stable network identities (pod-0, pod-1), ordered deployment/scaling, and persistent volume claim templates. Use StatefulSets only when workloads require stable identity or per-pod storage (databases, message brokers, consensus systems). StatefulSets are harder to operate: rolling updates are sequential, and pod deletion requires manual PVC cleanup.
- **HPA vs KEDA**: HPA scales on metrics-server CPU/memory or custom metrics via the Kubernetes metrics API. KEDA extends this with 60+ scalers (Kafka lag, SQS queue depth, cron, Prometheus queries) and supports scale-to-zero. Use HPA for simple CPU/memory scaling; KEDA for event-driven workloads or when scale-to-zero is needed.
- **Resource limits: set or unset**: Setting CPU limits causes throttling (CFS quota) even when the node has spare capacity, which can increase latency for bursty workloads. Setting memory limits prevents OOM from affecting neighbors. Best practice: always set memory limits; set CPU limits only for batch/background workloads; omit CPU limits for latency-sensitive services and rely on requests for scheduling.
- **Node affinity vs node selectors**: Node selectors are simpler (exact label match) but only support `requiredDuringScheduling`. Node affinity supports both required and preferred, `In/NotIn/Exists/DoesNotExist` operators, and multiple match expressions. Use node selectors for simple cases; affinity for complex scheduling requirements.
- **Single large pod vs multiple small pods**: Fewer large pods reduce scheduling overhead and network hops but create larger blast radii and limit scaling granularity. More small pods improve HA and granular scaling but increase overhead (more probes, more sidecar instances, more network connections). Right-size based on workload characteristics and resource efficiency.

## Reference Architectures

### Production Stateless Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 3
  strategy:
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0      # Zero-downtime rollouts
  template:
    spec:
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            - labelSelector:
                matchLabels:
                  app: api-server
              topologyKey: kubernetes.io/hostname
      containers:
        - name: api
          resources:
            requests:
              cpu: 500m
              memory: 512Mi
            limits:
              memory: 1Gi       # No CPU limit for latency-sensitive
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8080
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /livez
              port: 8080
            initialDelaySeconds: 15
            periodSeconds: 10
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-server-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: api-server
```
Pods spread across zones with anti-affinity preventing co-location on the same node. Zero-downtime rolling updates with maxUnavailable: 0. Memory limits set but no CPU limits for latency-sensitive workload. PDB ensures at least 2 pods remain during disruptions.

### Autoscaling Stack
```
[metrics-server] --> [HPA: CPU/Memory based scaling]
                          |
                     [Deployment: 2-20 replicas]

[KEDA] --> [ScaledObject: Queue-depth based scaling]
               |
          [Deployment: 0-50 replicas (scale-to-zero capable)]

[VPA] --> [Recommendation Engine]
               |
          [Adjusts resource requests (updateMode: "Off" for review-only)]
```
Use metrics-server HPA for synchronous API workloads scaling on CPU. Use KEDA for async workers scaling on queue depth with scale-to-zero during off-hours. Run VPA in recommendation mode (`updateMode: "Off"`) to inform resource request tuning without automatic changes that could disrupt running pods.

### Workload Tiering with Priority Classes
```
PriorityClass: system-critical (1000000)    -- ingress controllers, monitoring
PriorityClass: production     (100000)      -- production application workloads
PriorityClass: batch          (10000)       -- CI runners, data processing
PriorityClass: preemptible    (1000)        -- dev environments, experiments

[Memory Pressure Event]
  -> Evicts: preemptible (BestEffort QoS first, then Burstable)
  -> Then: batch
  -> Last: production, system-critical
```
Priority classes determine preemption and eviction order. Higher-priority pods can preempt lower-priority pods when scheduling. During memory pressure, kubelet evicts in QoS order within each priority class. Set `preemptionPolicy: Never` on batch workloads if they should wait rather than evict others.
