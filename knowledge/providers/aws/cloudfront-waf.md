# AWS CloudFront and WAF

## Checklist

- [ ] Is CloudFront configured as the entry point for all public-facing content, with the origin (ALB, S3, API Gateway) not directly accessible?
- [ ] Is Origin Access Control (OAC) used for S3 origins to replace legacy Origin Access Identity (OAI)?
- [ ] Are cache behaviors configured per path pattern with appropriate TTLs, and are cache policies and origin request policies used instead of legacy forwarding settings?
- [ ] Is a custom cache policy defined that only forwards the minimum necessary headers, cookies, and query strings to maximize cache hit ratio?
- [ ] Is origin failover configured with an origin group for automatic failover to a secondary origin on 5xx errors?
- [ ] Are response headers policies configured to set security headers (HSTS, X-Content-Type-Options, X-Frame-Options, CSP)?
- [ ] Is AWS WAF associated with the CloudFront distribution with at least the AWS Managed Rules core rule set (AWSManagedRulesCommonRuleSet)?
- [ ] Are WAF rate-based rules configured to prevent DDoS and brute-force attacks at the edge?
- [ ] Is AWS Shield Advanced enabled for high-value applications needing DDoS cost protection and SRT support?
- [ ] Are geographic restrictions (geo-blocking) or geo-match conditions applied where required by licensing or regulation?
- [ ] Is real-time logging enabled to S3 or Kinesis Data Firehose for traffic analysis and incident investigation?
- [ ] Are CloudFront Functions or Lambda@Edge used for header manipulation, URL rewrites, A/B testing, or authentication at the edge?
- [ ] Is TLS 1.2 minimum enforced on the viewer-side, and is the origin connection using a custom SSL certificate with SNI?
- [ ] Is field-level encryption configured for sensitive form fields that must remain encrypted through to the application?

## Why This Matters

CloudFront misconfiguration exposes origins directly to the internet, bypassing WAF and caching. Missing cache optimization increases origin load and latency. Without WAF, applications are vulnerable to OWASP Top 10 attacks, bots, and DDoS. Over-forwarding headers and cookies destroys cache hit ratios, effectively making CloudFront an expensive proxy.

## Common Decisions (ADR Triggers)

- **CDN architecture** -- CloudFront vs third-party CDN (Cloudflare, Akamai), multi-CDN strategy
- **WAF rule management** -- AWS Managed Rules vs third-party managed rules (F5, Fortinet) vs custom rules
- **Edge compute** -- CloudFront Functions (lightweight, <1ms) vs Lambda@Edge (full Node.js/Python, origin-facing)
- **Cache invalidation strategy** -- path-based invalidation vs versioned URLs/filenames
- **Origin architecture** -- ALB origin vs API Gateway origin vs S3 static origin, custom origin headers for validation
- **Shield Advanced** -- cost ($3K/mo) vs DDoS cost protection and response team access
- **Logging and observability** -- real-time logs vs standard logs, log analysis with Athena vs third-party SIEM
