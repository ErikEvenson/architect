# Citrix ADC (NetScaler)

## Scope

This file covers **Citrix ADC** (formerly NetScaler) application delivery including virtual server configuration, service groups, content switching policies, SSL offloading and certificate management, Global Server Load Balancing (GSLB), web application firewall (WAF), platform variants (VPX virtual appliance, SDX hardware with multi-tenancy, CPX container-based, BLX bare-metal), migration between form factors and versions, and licensing models (Standard, Advanced, Premium, Pooled Capacity). For general on-premises load balancing patterns and comparison with other platforms, see `general/load-balancing-onprem.md`. For Citrix virtual desktop integration, see `providers/citrix/virtual-desktops.md`.

## Checklist

- [ ] **[Critical]** Are load balancing virtual servers configured with appropriate service types (HTTP, SSL, TCP, SSL_BRIDGE) and are service groups used (rather than individual services) for dynamic backend management with proper health monitors bound?
- [ ] **[Critical]** Are health monitors configured with appropriate types (HTTP-ECV for response validation, TCP for port checks) with custom send strings and receive expressions that verify application functionality, not just TCP connectivity?
- [ ] **[Critical]** Is SSL offloading configured with correct virtual server cipher bindings (disabling weak ciphers, enforcing TLS 1.2+), certificate-key pairs properly bound to virtual servers, and OCSP stapling or CRL checks enabled for certificate validation?
- [ ] **[Critical]** Is the HA pair configured with proper failover settings (INC mode for independent network configuration vs non-INC), heartbeat intervals, and dead interval tuned to prevent false failovers while maintaining acceptable recovery time?
- [ ] **[Recommended]** Are content switching policies used to route traffic to different load balancing virtual servers based on URL path, hostname, or HTTP headers -- separating traffic management logic from backend pool configuration for cleaner administration?
- [ ] **[Recommended]** Is the ADC platform variant (VPX, SDX, CPX, BLX) appropriate for the workload -- VPX for VM-based deployments (1-100 Gbps throughput tiers), SDX for multi-tenant hardware with isolated VPX instances, CPX for Kubernetes/container environments, BLX for bare-metal Linux?
- [ ] **[Recommended]** Are responder and rewrite policies used for HTTP redirections, header manipulation, and URL rewriting instead of embedding logic in multiple virtual server configurations, and are policy bindings ordered by priority correctly?
- [ ] **[Recommended]** Is GSLB configured with proper site definitions, GSLB services, DNS virtual servers, and monitoring (MEP for inter-site communication, health monitors for service verification) with appropriate GSLB methods (round-robin, least-connections, proximity) for multi-datacenter deployments?
- [ ] **[Recommended]** Is the licensing model evaluated -- Standard (basic LB), Advanced (content switching, GSLB, caching), Premium (WAF, bot management, API protection), or Pooled Capacity (shared bandwidth pool across instances) -- to avoid deploying features that require a higher license tier?
- [ ] **[Optional]** Is Citrix Application Delivery Management (ADM) deployed for centralized configuration management, analytics, and license management across multiple ADC instances?
- [ ] **[Optional]** Is the WAF (AppFirewall) profile configured with appropriate security checks (SQL injection, XSS, buffer overflow), learning mode enabled for initial tuning, and relaxation rules documented to prevent security bypasses?
- [ ] **[Optional]** Are rate limiting and connection surge protection configured using AppQoE policies or responder policies to protect backends from traffic spikes and DoS conditions?
- [ ] **[Recommended]** Are configuration backups automated (full config via `save ns config` and exported via SCP/SFTP), and is nsconfig compared between HA peers to detect configuration drift?

## Why This Matters

Citrix ADC is widely deployed in enterprise environments, particularly in organizations with existing Citrix Virtual Apps and Desktops infrastructure where the ADC provides optimized HDX proxy functionality, StoreFront load balancing, and Gateway services. The platform's content switching architecture -- where a content switching virtual server routes to multiple backend load balancing virtual servers -- is powerful but introduces complexity that can lead to misrouted traffic if policies are incorrectly prioritized. SSL configuration is critical because the ADC often terminates SSL for both web applications and Citrix ICA connections; a cipher misconfiguration can break desktop sessions across the entire organization.

Migration scenarios are common as organizations move from MPX hardware to VPX virtual appliances or CPX containers. The configuration model is portable (CLI commands are largely identical across form factors), but throughput characteristics differ significantly -- MPX hardware provides dedicated SSL ASICs while VPX relies on CPU-based SSL processing. Licensing changes (from appliance-based to Pooled Capacity) can dramatically alter cost structures, especially for organizations with many small ADC instances.

## Common Decisions (ADR Triggers)

- **VPX vs SDX vs CPX** -- VPX runs as a virtual appliance on any hypervisor (VMware, Hyper-V, KVM, cloud) with throughput from 10 Mbps to 100 Gbps, suitable for most deployments. SDX provides hardware with multiple isolated VPX instances sharing dedicated SSL ASICs and throughput -- ideal for service providers or multi-tenant environments. CPX is a containerized ADC for Kubernetes environments (lightweight, ~200 MB image), typically deployed as an ingress controller. BLX runs directly on Linux without hypervisor overhead. Choose based on deployment model, isolation requirements, and SSL throughput needs.
- **Standard vs Advanced vs Premium licensing** -- Standard provides basic load balancing and SSL offloading. Advanced adds content switching, GSLB, caching, and compression -- required for most production deployments. Premium adds WAF, bot management, and API security. Pooled Capacity allows sharing bandwidth allocation across instances with flexible allocation. Most enterprises need Advanced at minimum; Premium only if replacing a standalone WAF.
- **Citrix ADC vs F5 BIG-IP** -- Citrix ADC excels in Citrix ecosystem integration (HDX proxy, Gateway, StoreFront), content switching architecture, and Pooled Capacity licensing flexibility. F5 BIG-IP offers stronger iRules programmability, broader ASM/AWAF security features, and a larger ecosystem of deployment guides. In environments with Citrix VDI, the ADC is nearly mandatory; in non-Citrix environments, the decision comes down to team expertise and specific feature requirements.
- **Gateway mode vs load balancing mode for VDI** -- Citrix Gateway (VPN/ICA proxy) provides secure remote access to virtual desktops with SSL VPN and micro-VPN capabilities. Standard load balancing mode handles internal StoreFront and Delivery Controller traffic. Both are often needed -- Gateway for external users, LB for internal. Architecture must clearly separate external-facing Gateway virtual servers (DMZ) from internal LB virtual servers (trusted network).
- **Integrated WAF vs dedicated WAF** -- Citrix ADC WAF (AppFirewall) eliminates an additional network hop and simplifies architecture when ADC is already in the traffic path. However, it consumes ADC CPU resources (reducing LB throughput), requires Premium licensing, and may lack the threat intelligence depth of dedicated WAF solutions. Use integrated WAF for applications already behind the ADC where budget is constrained; dedicated WAF for high-security environments requiring specialized detection capabilities.

## See Also

- `general/load-balancing-onprem.md` -- on-premises load balancing patterns and comparison matrix
- `providers/citrix/virtual-desktops.md` -- Citrix Virtual Apps and Desktops architecture where ADC provides Gateway and StoreFront load balancing

## Reference Links

- [Citrix ADC Documentation](https://docs.citrix.com/en-us/citrix-adc.html) -- virtual servers, content switching, SSL offloading, GSLB, and WAF configuration
- [Citrix ADC Deployment Guides](https://docs.citrix.com/en-us/tech-zone/build/deployment-guides.html) -- reference architectures for common deployment scenarios
- [Citrix ADC Pooled Capacity](https://docs.citrix.com/en-us/citrix-application-delivery-management-software/current-release/license-server/adc-pooled-capacity.html) -- flexible licensing across VPX, SDX, and CPX form factors
