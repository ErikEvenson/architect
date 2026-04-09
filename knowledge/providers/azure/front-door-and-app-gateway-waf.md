# Azure Front Door and Application Gateway WAF

## Scope

Azure has two L7 reverse proxy services that both support WAF: **Azure Front Door** (global, anycast, edge-distributed) and **Azure Application Gateway** (regional, in-VNet, deeply integrated with backend Azure resources). Covers the front-door-vs-app-gateway decision, the SKU tiers (Front Door Standard / Premium, App Gateway Standard_v2 / WAF_v2), the managed WAF rule sets (DRS 2.x, Bot Manager, custom rules), the WAF modes (Detection / Prevention), the integration with Private Link for backend access, the cross-component routing patterns (Front Door → App Gateway → backend), the audit characteristics of WAF in Detection mode that has been there "temporarily" for 18 months, and the cost/performance trade-offs.

## Checklist

- [ ] **[Critical]** Choose Front Door vs Application Gateway based on the actual requirement, not by what was deployed first. Front Door is global edge with anycast IP and works well for any workload that serves traffic across regions. Application Gateway is regional and works well for any workload that needs to terminate TLS at the VNet boundary or that needs deep integration with backend Azure resources via Private Link.
- [ ] **[Critical]** Use **Front Door Premium** or **Application Gateway WAF_v2** if WAF is required. The non-WAF tiers (Front Door Standard, App Gateway Standard_v2) do not have WAF support. The WAF tiers cost more but the cost is small relative to the security posture improvement.
- [ ] **[Critical]** WAF must be in **Prevention mode** for production workloads. Detection mode logs would-be blocks but does not actually block them, which means the WAF provides zero protection. Detection mode is appropriate as a temporary state during initial tuning (typically 1–4 weeks); a WAF that has been in Detection mode for 18 months is one of the most common Azure security findings.
- [ ] **[Critical]** Enable the **Microsoft Default Rule Set (DRS)** at the latest available version (currently 2.1). The DRS covers OWASP Top 10 protection and is updated by Microsoft as new attack patterns emerge. Custom rules supplement the DRS for application-specific patterns; they do not replace it.
- [ ] **[Critical]** Enable the **Bot Manager rule set** for any internet-facing workload. Bot Manager classifies traffic as good bot / bad bot / unknown, with managed rules to block known-bad bots while allowing known-good bots (search engines, monitoring tools). Custom bot management is much more effort for less coverage.
- [ ] **[Critical]** Lock down the backend so that it accepts traffic only from the Front Door / Application Gateway. For Front Door, use the `AzureFrontDoor.Backend` service tag in the backend NSG and the `X-Azure-FDID` header check on the backend (the header value is the unique Front Door instance ID; backends should reject traffic without the expected header). For Application Gateway, use the App Gateway subnet IP range or a dedicated NSG. Without backend lockdown, an attacker who discovers the backend hostname can bypass the WAF entirely.
- [ ] **[Recommended]** Configure **custom rules** for application-specific patterns the DRS does not cover: rate limiting per IP / per session, geo-fencing (block traffic from countries where the app has no users), known-bad source IPs from threat intelligence, application-specific URL patterns that should never be requested.
- [ ] **[Recommended]** Enable **WAF logs** and forward to Log Analytics or a SIEM. Default logging captures the WAF action (allow / block / log) and the matched rule. Without logs, the answer to "did the WAF stop this attack" is "we do not know".
- [ ] **[Recommended]** Use **WAF policies** (the new model) instead of inline WAF configuration. WAF policies are reusable across multiple Front Door endpoints or Application Gateways and are independently versionable. The legacy inline configuration is being phased out.
- [ ] **[Recommended]** For workloads with both Front Door (for global distribution) and Application Gateway (for regional VNet integration), apply WAF at the Front Door layer as the primary defense and use App Gateway as a transparent backend without duplicate WAF rules. Duplicate WAF at both layers wastes processing and confuses the audit story.
- [ ] **[Recommended]** Tune WAF rules to reduce false positives — but do it deliberately. Common false positives: legitimate JSON request bodies that look like SQL injection, XML-based APIs that trigger XML attacks rules, file uploads that look like PHP injection. Document each exclusion with the reason and the affected rule ID; review exclusions quarterly.
- [ ] **[Optional]** Use **Front Door Premium Private Link backends** for the highest security posture: backends are reached only via Private Link (no public IP, no public DNS), with Front Door as the only authorized client. Combined with the `X-Azure-FDID` check, this is the strongest practical lockdown of the backend.
- [ ] **[Optional]** Enable **TLS 1.2 minimum** on the frontend listener (Front Door defaults to 1.2 already; App Gateway needs explicit configuration). Enable **TLS 1.3** if supported by all expected clients. Disable older protocols and weak cipher suites explicitly.

## Why This Matters

The most common WAF audit finding in Azure is "WAF is enabled but in Detection mode". Detection mode is the right starting state during initial deployment because it surfaces false positives without breaking the application — but the transition to Prevention mode is the only state in which the WAF actually provides protection. Many organizations leave the WAF in Detection mode indefinitely because no one wants to be the person who flips the switch and breaks production. The audit consequence is that the organization has paid for a WAF and gets none of the protection.

The second most common finding is "WAF is in Prevention mode but the backend has a public IP". An attacker who discovers the backend hostname (from DNS records, from a deprecated subdomain, from a TLS certificate transparency log) can bypass the WAF entirely by hitting the backend directly. The fix is to lock down the backend so that traffic can only arrive via the WAF — service tag NSG rules, the `X-Azure-FDID` header check, or Private Link backends.

The third common finding is "WAF rules are tuned by exclusion list". Every exclusion is a hole in the WAF policy. Some exclusions are legitimate (the JSON body that looks like SQLi but is not). Most are workarounds for false positives that should have been fixed at the application layer instead. The audit posture of an exclusion list with documented reasons and quarterly review is dramatically better than an exclusion list that was added once and never revisited.

## Common Decisions (ADR Triggers)

- **Front Door vs Application Gateway** — Front Door for global distribution, anycast IPs, edge caching, and workloads with users in multiple regions. Application Gateway for regional workloads that need to terminate TLS at the VNet boundary, that need deep backend integration (e.g., session affinity to specific backends), or that need to be inside a customer's VNet for compliance. Both can be used together (Front Door → App Gateway → backend) for workloads that need both.
- **Front Door Standard vs Premium** — Standard for non-WAF workloads (global delivery, custom domains, basic routing). Premium for WAF + Bot Manager + Private Link backends + advanced security features. The Premium tier is the right answer for any internet-facing production workload.
- **App Gateway Standard_v2 vs WAF_v2** — Standard_v2 for internal-only workloads where the upstream is already WAF-protected (e.g., Front Door). WAF_v2 for direct internet exposure or when the architectural choice is "WAF at the App Gateway layer".
- **WAF Detection vs Prevention mode** — Detection only as a temporary state during initial tuning. Prevention as the steady state for production. Set a calendar reminder for the transition; do not let Detection mode become permanent.
- **Inline WAF vs WAF Policy** — WAF Policy is the new model and the right choice for new deployments. Inline configuration is acceptable for existing deployments that have not yet been migrated, but should be migrated when the next change is needed anyway.
- **Backend lockdown approach** — service tag NSG + header check is the simplest approach for most workloads. Private Link backends are the strongest but require Premium tier and add cost. Pick based on the security posture requirement.

## Reference Architectures

### Standard internet-facing web application (Front Door + backend)

- **Front Door Premium** with custom domain and ACM-equivalent managed certificate
- **WAF Policy** assigned to the Front Door endpoint, in Prevention mode, with DRS 2.1 + Bot Manager
- **Custom rules** for: rate limiting (1000 req/min per IP), geo-block (countries the app does not serve), known-bad-IP allowlist from threat intel
- **Backend** is App Service or AKS ingress, with `AzureFrontDoor.Backend` service tag in the NSG and `X-Azure-FDID` header check on the application
- **WAF logs** forwarded to Log Analytics in the management subscription

### Internal application with public exposure via App Gateway

- **Application Gateway WAF_v2** in the VNet's gateway subnet
- **WAF Policy** in Prevention mode with DRS 2.1
- **Backend pool** is internal load balancer or App Service Environment
- **Listener** on `:443` with TLS 1.2 minimum and the appropriate cert
- **Health probe** configured for the backend application path
- **Diagnostic settings** forwarded to Log Analytics; alert on high block rate

### Front Door + App Gateway (layered)

- **Front Door Premium** at the global edge with WAF in Prevention mode
- **Application Gateway** as the regional backend, in the workload VNet
- **App Gateway** is configured as a Front Door origin via Private Link (Premium feature)
- **Backend pool** in App Gateway is the actual workload (App Service, AKS, VMs)
- WAF rules at the Front Door layer only — App Gateway is in `Standard_v2` (no WAF) to avoid duplicate processing
- This shape is correct when global edge distribution and VNet integration are both required

---

## Reference Links

- [Azure Front Door documentation](https://learn.microsoft.com/azure/frontdoor/)
- [Application Gateway documentation](https://learn.microsoft.com/azure/application-gateway/)
- [Azure WAF documentation](https://learn.microsoft.com/azure/web-application-firewall/)
- [WAF managed rules — Default Rule Set 2.1](https://learn.microsoft.com/azure/web-application-firewall/afds/waf-front-door-drs)
- [Bot Manager rule set](https://learn.microsoft.com/azure/web-application-firewall/afds/afds-overview#bot-protection-rule-set)
- [Front Door Premium Private Link backends](https://learn.microsoft.com/azure/frontdoor/private-link)

## See Also

- `providers/azure/networking.md` — broader Azure networking, including Private Link details
- `providers/azure/security.md` — broader Azure security service set
- `providers/azure/network-security-groups.md` — backend NSG lockdown patterns
- `providers/aws/cloudfront-waf.md` — equivalent service in AWS
- `general/tls-certificates.md` — TLS certificate management
