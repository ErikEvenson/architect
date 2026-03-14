# Static Site Architecture

## Overview

Static sites serve pre-built HTML, CSS, and JavaScript files. They can include client-side applications (SPAs) that call backend APIs. No server-side rendering at request time.

## Checklist

- [ ] What static site generator or build tool is used? (Next.js export, Gatsby, Hugo, Vite)
- [ ] Where are built assets stored? (object storage — S3, Azure Blob, GCS)
- [ ] Is a CDN configured for global delivery?
- [ ] Is the CDN configured with proper cache headers? (immutable hashed assets, no-cache for HTML)
- [ ] How are deployments handled? (upload to object storage, invalidate CDN cache)
- [ ] Is there a backend API? How is it hosted? (serverless functions, separate API service)
- [ ] Is HTTPS enforced with proper TLS configuration?
- [ ] Is there a custom domain with DNS properly configured?
- [ ] Are redirects and rewrites configured? (SPA fallback to index.html)
- [ ] Is there a preview/staging environment for pull requests?
- [ ] Is access control needed? (authentication, geo-restriction)
- [ ] Are security headers configured? (CSP, HSTS, X-Frame-Options)
- [ ] Is there a form handling strategy? (third-party service, serverless function)

## Common Mistakes

- No CDN (serving from origin for every request)
- Cache-Control headers missing or wrong (stale content or no caching)
- SPA routing not configured (404 on direct URL access)
- No HTTPS (security and SEO penalty)
- Large unoptimized assets (slow page loads)
- No build optimization (no minification, no tree-shaking, no image optimization)

## Key Decisions

- **Hosting**: object storage + CDN vs specialized platform (Netlify, Vercel, Cloudflare Pages)
- **API strategy**: serverless functions (Lambda@Edge, Cloudflare Workers) vs separate API service
- **Build pipeline**: CI/CD with preview deployments per PR
