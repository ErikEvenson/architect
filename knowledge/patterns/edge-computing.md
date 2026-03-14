# Edge Computing Architecture

## Overview

Edge computing moves computation and data storage closer to the sources of data and end users, reducing latency and bandwidth consumption. This spans CDN edge workers (Cloudflare Workers, Lambda@Edge, Cloud Run), IoT edge platforms (AWS Greengrass, Azure IoT Edge), and emerging 5G/MEC deployments. Edge architectures require careful consideration of consistency, deployment, security, and offline operation.

## Checklist

- [ ] What is the latency requirement driving edge deployment? (sub-50ms response, real-time processing, regulatory data locality)
- [ ] Which edge compute platform is used? (Cloudflare Workers, Lambda@Edge, CloudFront Functions, Fastly Compute, Deno Deploy, Cloud Run)
- [ ] Is IoT edge processing required? (AWS Greengrass, Azure IoT Edge, Google Coral — local inference, data filtering, protocol translation)
- [ ] What runs at the edge vs the origin? (static content, personalization, A/B testing, authentication, data aggregation, ML inference)
- [ ] How is code deployed to edge locations? (global deployment pipelines, canary rollouts across regions, rollback strategy)
- [ ] Is offline capability required? (local data storage, conflict resolution on reconnect, queue-and-sync patterns)
- [ ] How is edge-to-cloud data synchronization handled? (eventual consistency, batched uploads, real-time streaming, conflict resolution)
- [ ] What data is aggregated or filtered at the edge before sending to cloud? (reducing bandwidth costs, preprocessing sensor data, privacy filtering)
- [ ] How is content personalization implemented at the edge? (cookie/header-based routing, A/B testing at CDN, geo-based content)
- [ ] What is the edge security model? (TLS termination, DDoS mitigation, bot detection, WAF at edge, device attestation for IoT)
- [ ] How are edge devices/nodes monitored? (health checks, remote management, OTA updates, fleet management)
- [ ] What are the compute and memory constraints at edge locations? (worker memory limits, execution time limits, cold start impact)
- [ ] Is 5G/MEC (Multi-access Edge Computing) relevant? (carrier edge, ultra-low latency use cases, private 5G networks)

## Why This Matters

Users expect sub-100ms response times, which is physically impossible from a single-region deployment for global audiences. Edge computing solves latency problems but fragments state across hundreds of locations. CDN edge workers are ideal for stateless transformations (personalization, routing, authentication) but struggle with stateful workloads. IoT edge is critical when devices generate more data than can be economically transmitted to the cloud, or when real-time local decisions are required (industrial automation, autonomous vehicles). The biggest architectural mistake is putting too much logic at the edge, creating a distributed system that is difficult to debug, update, and keep consistent.

## Common Decisions (ADR Triggers)

- **Edge platform selection** — Cloudflare Workers vs Lambda@Edge vs Fastly Compute (execution model, language support, pricing, global coverage)
- **Edge vs origin split** — which logic executes at edge vs origin, state management implications
- **IoT edge gateway** — Greengrass vs Azure IoT Edge vs custom, protocol support, local ML inference capability
- **Offline strategy** — local storage approach, conflict resolution algorithm (last-write-wins, CRDTs, manual merge)
- **Data sync pattern** — real-time streaming vs batched sync, bandwidth budget, data retention at edge
- **Edge caching strategy** — cache invalidation approach, TTL policies, stale-while-revalidate, cache key design
- **Deployment topology** — all-edge-locations vs selected POPs, canary percentage, geographic rollout order
- **Edge security posture** — which security functions run at edge (WAF, bot detection, rate limiting) vs origin
- **5G/MEC adoption** — carrier partnership, latency requirements that justify MEC, private network deployment
