# Static Site Architecture

## Scope

Covers architectures for serving pre-built static files (HTML, CSS, JavaScript) including single-page applications (SPAs), using object storage, CDN delivery, serverless API backends, and platform hosting services. Applicable when the application does not require server-side rendering at request time.

## Overview

Static sites serve pre-built HTML, CSS, and JavaScript files. They can include client-side applications (SPAs) that call backend APIs. No server-side rendering at request time.

## Checklist

- [ ] **[Recommended]** What static site generator or build tool is used? (Next.js export, Gatsby, Hugo, Vite)
- [ ] **[Critical]** Where are built assets stored? (object storage — S3, Azure Blob, GCS)
- [ ] **[Critical]** Is a CDN configured for global delivery?
- [ ] **[Recommended]** Is the CDN configured with proper cache headers? (immutable hashed assets, no-cache for HTML)
- [ ] **[Recommended]** How are deployments handled? (upload to object storage, invalidate CDN cache)
- [ ] **[Recommended]** Is there a backend API? How is it hosted? (serverless functions, separate API service)
- [ ] **[Critical]** Is HTTPS enforced with proper TLS configuration?
- [ ] **[Recommended]** Is there a custom domain with DNS properly configured?
- [ ] **[Recommended]** Are redirects and rewrites configured? (SPA fallback to index.html)
- [ ] **[Optional]** Is there a preview/staging environment for pull requests?
- [ ] **[Recommended]** Is access control needed? (authentication, geo-restriction)
- [ ] **[Recommended]** Are security headers configured? (CSP, HSTS, X-Frame-Options)
- [ ] **[Optional]** Is there a form handling strategy? (third-party service, serverless function)

## Why This Matters

Static sites are the simplest and most cost-effective architecture, but common mistakes undermine their performance and reliability. Serving from origin without a CDN wastes bandwidth and increases latency. Missing or incorrect Cache-Control headers cause stale content or eliminate caching benefits entirely. Unconfigured SPA routing causes 404 errors on direct URL access. Missing HTTPS creates security vulnerabilities and SEO penalties. Unoptimized assets slow page loads and increase CDN transfer costs.

## Cost Benchmarks

> **Disclaimer:** Prices are rough estimates based on AWS us-east-1 pricing as of early 2025. Actual costs vary by region, reserved instance commitments, and usage patterns. Prices change over time — always verify with the provider's pricing calculator.

### Small (10K Pageviews/month)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Storage | S3 (1 GB, Standard) | $0.02 |
| CDN | CloudFront (1 GB transfer, 10K requests) | $0.10 |
| DNS | Route 53 (1 hosted zone, 10K queries) | $0.90 |
| TLS | ACM certificate | Free |
| Functions | Lambda@Edge (1K invocations, if used) | $0.01 |
| **Total** | | **~$1/mo** |

**Alternative:** Free tier on Netlify, Vercel, or Cloudflare Pages covers this entirely.

### Medium (1M Pageviews/month)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Storage | S3 (5 GB, Standard) | $0.12 |
| CDN | CloudFront (100 GB transfer, 2M requests) | $10 |
| DNS | Route 53 (1 hosted zone, 1M queries) | $1.40 |
| TLS | ACM certificate | Free |
| Functions | Lambda@Edge (100K invocations for SSR/auth) | $1 |
| API Backend | Lambda + API Gateway (500K API calls) | $5 |
| **Total** | | **~$18/mo** |

### Large (100M Pageviews/month)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Storage | S3 (20 GB, Standard) | $0.46 |
| CDN | CloudFront (10 TB transfer, 200M requests) | $850 |
| DNS | Route 53 (1 hosted zone, 100M queries) | $40 |
| TLS | ACM certificate | Free |
| Functions | Lambda@Edge (10M invocations) | $60 |
| API Backend | Lambda + API Gateway (50M API calls) | $200 |
| WAF | AWS WAF (200M requests, bot control) | $200 |
| Monitoring | CloudWatch + Real User Monitoring | $30 |
| **Total** | | **~$1,380/mo** |

### Azure Estimates

> **Disclaimer:** Azure prices are approximate, based on East US region pricing as of early 2025. Actual costs vary by region, commitment tier, and usage patterns. Always verify with the Azure Pricing Calculator.

#### Small (10K Pageviews/month)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Hosting | Azure Static Web Apps (Free tier) | Free |
| CDN | Azure CDN (1 GB transfer) | $0.08 |
| DNS | Azure DNS (1 zone, 10K queries) | $0.90 |
| TLS | Managed certificate (included) | Free |
| **Total** | | **~$1/mo** |

**Alternative:** Azure Static Web Apps Free tier covers this entirely with built-in CDN, SSL, and custom domains.

#### Medium (1M Pageviews/month)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Hosting | Azure Static Web Apps (Standard, $9/app) | $9 |
| CDN | Azure CDN (100 GB transfer, 2M requests) | $9 |
| DNS | Azure DNS (1 zone, 1M queries) | $1.30 |
| TLS | Managed certificate (included) | Free |
| Functions | Azure Functions (100K invocations for SSR/auth) | $1 |
| API Backend | Azure Functions + API Management (Consumption, 500K calls) | $5 |
| **Total** | | **~$25/mo** |

#### Large (100M Pageviews/month)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Hosting | Azure Static Web Apps (Standard, $9/app) | $9 |
| CDN | Azure Front Door Premium (10 TB transfer, 200M requests) | $900 |
| DNS | Azure DNS (1 zone, 100M queries) | $40 |
| TLS | Managed certificate (included) | Free |
| Functions | Azure Functions (10M invocations) | $50 |
| API Backend | Azure Functions + API Management (Standard) | $700 |
| WAF | Azure WAF on Front Door (200M requests) | $220 |
| Monitoring | Azure Monitor + Application Insights | $30 |
| **Total** | | **~$1,949/mo** |

### GCP Estimates

> **Disclaimer:** GCP prices are approximate, based on us-central1 region pricing as of early 2025. Actual costs vary by region, commitment tier, and usage patterns. Always verify with the GCP Pricing Calculator.

#### Small (10K Pageviews/month)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Storage | Cloud Storage (1 GB, Standard) | $0.02 |
| CDN | Cloud CDN (1 GB transfer, 10K requests) | $0.08 |
| DNS | Cloud DNS (1 zone, 10K queries) | $0.50 |
| TLS | Google-managed certificate | Free |
| **Total** | | **~$1/mo** |

**Alternative:** Firebase Hosting free tier (Spark plan) covers this with built-in CDN, SSL, and custom domains.

#### Medium (1M Pageviews/month)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Storage | Cloud Storage (5 GB, Standard) | $0.10 |
| CDN | Cloud CDN (100 GB transfer, 2M requests) | $9 |
| DNS | Cloud DNS (1 zone, 1M queries) | $1.00 |
| TLS | Google-managed certificate | Free |
| Functions | Cloud Functions (100K invocations for SSR/auth) | $1 |
| API Backend | Cloud Functions + API Gateway (500K calls) | $4 |
| **Total** | | **~$15/mo** |

#### Large (100M Pageviews/month)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Storage | Cloud Storage (20 GB, Standard) | $0.40 |
| CDN | Cloud CDN (10 TB transfer, 200M requests) | $750 |
| DNS | Cloud DNS (1 zone, 100M queries) | $35 |
| TLS | Google-managed certificate | Free |
| Functions | Cloud Functions (10M invocations) | $50 |
| API Backend | Cloud Functions + API Gateway (50M calls) | $175 |
| Cloud Armor | Cloud Armor WAF (200M requests) | $180 |
| Monitoring | Cloud Monitoring + Cloud Logging | $25 |
| **Total** | | **~$1,215/mo** |

### Provider Comparison

> **Disclaimer:** All prices are approximate monthly estimates as of early 2025. Actual costs vary significantly based on region, commitment discounts, negotiated contracts, and usage patterns. Always verify with each provider's pricing calculator.

| Scale | AWS | Azure | GCP |
|-------|-----|-------|-----|
| Small (10K PV/mo) | ~$1/mo | ~$1/mo | ~$1/mo |
| Medium (1M PV/mo) | ~$18/mo | ~$25/mo | ~$15/mo |
| Large (100M PV/mo) | ~$1,380/mo | ~$1,949/mo | ~$1,215/mo |

**Notes:**
- At small scale, all three providers (and platforms like Netlify/Vercel/Cloudflare Pages) are essentially free.
- Azure API Management at Standard tier ($700/mo) significantly inflates Azure large-scale costs; Azure Functions alone are competitive.
- GCP Cloud CDN egress pricing is generally the most competitive of the three providers.
- For static sites, platform services (Vercel, Netlify, Cloudflare Pages) often beat self-managed cloud infrastructure on both cost and developer experience up to medium scale.

### Biggest Cost Drivers

1. **CDN data transfer** — dominates at scale. CloudFront pricing decreases with committed use discounts above 10 TB/mo.
2. **Request volume** — CloudFront charges per HTTP/HTTPS request ($0.0075-$0.01 per 10K requests depending on region).
3. **API backend** — if the "static" site makes heavy API calls, Lambda + API Gateway costs grow with usage.

### Optimization Tips

- Static sites are **extremely cost-effective** compared to server-rendered alternatives.
- Use **CloudFront Security Savings Bundle** for 30% savings on committed CDN spend.
- Optimize assets — **image compression, code splitting, tree-shaking** reduce transfer costs.
- Set **long cache TTLs** on immutable hashed assets (CSS, JS bundles) to maximize CDN cache hit ratio.
- Consider **Cloudflare** (free tier generous) or **Vercel/Netlify** for small-to-medium sites — often cheaper than self-managed AWS.
- Use **S3 Intelligent-Tiering** if storing user-generated content alongside the site.

## Key Decisions

- **Hosting**: object storage + CDN vs specialized platform (Netlify, Vercel, Cloudflare Pages)
- **API strategy**: serverless functions (Lambda@Edge, Cloudflare Workers) vs separate API service
- **Build pipeline**: CI/CD with preview deployments per PR

## See Also

- `patterns/cdn-fronted-onprem.md` — CDN configuration patterns including caching and WAF
- `general/tls-certificates.md` — TLS certificate management for custom domains
- `general/ci-cd.md` — CI/CD pipeline design for automated deployments
- `general/security.md` — Security headers, HTTPS enforcement, and access control
