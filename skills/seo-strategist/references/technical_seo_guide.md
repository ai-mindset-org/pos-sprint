# Technical SEO Guide

Comprehensive technical SEO best practices covering crawlability, indexation, performance, and site architecture.

## Crawlability

### robots.txt Best Practices

```txt
# Example robots.txt
User-agent: *
Allow: /

# Block non-content directories
Disallow: /admin/
Disallow: /api/
Disallow: /tmp/

# Block query parameters
Disallow: /*?*sort=
Disallow: /*?*filter=

# Reference sitemap
Sitemap: https://example.com/sitemap.xml
```

**Guidelines:**
- Always include sitemap reference
- Don't block CSS/JS files (breaks rendering)
- Use `Allow:` to override parent `Disallow:`
- Test with Google's robots.txt Tester
- Remember: robots.txt is public and cacheable

### XML Sitemap Requirements

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/page</loc>
    <lastmod>2025-01-15</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
```

**Best Practices:**
- Maximum 50,000 URLs per sitemap
- Maximum 50MB uncompressed file size
- Use sitemap index for large sites
- Include only canonical, indexable URLs
- Update `lastmod` only when content changes
- Submit to Google Search Console

### Crawl Budget Optimization

**Factors Affecting Crawl Budget:**
- Site speed (faster = more crawling)
- Server errors (reduce 5xx responses)
- Redirect chains (eliminate)
- Duplicate content (consolidate)
- URL parameters (control via GSC)

**Optimization Tactics:**
1. Fix or remove broken pages (404s)
2. Eliminate redirect chains (max 1 hop)
3. Implement proper canonicalization
4. Block low-value pages from crawling
5. Improve server response time
6. Use internal linking strategically

## Indexation

### Canonical Tags

```html
<!-- Self-referencing canonical (recommended) -->
<link rel="canonical" href="https://example.com/page" />

<!-- Cross-domain canonical -->
<link rel="canonical" href="https://original-source.com/page" />
```

**Canonical Guidelines:**
- Every page should have a canonical tag
- Use absolute URLs (include protocol and domain)
- Self-referencing canonicals prevent issues
- Canonical should point to preferred version
- Google treats as hint, not directive

### Index Control

**Meta Robots:**
```html
<!-- Default (index, follow) -->
<meta name="robots" content="index, follow">

<!-- No index -->
<meta name="robots" content="noindex, follow">

<!-- No follow -->
<meta name="robots" content="index, nofollow">

<!-- No snippet -->
<meta name="robots" content="nosnippet">

<!-- Max snippet length -->
<meta name="robots" content="max-snippet:150">
```

**X-Robots-Tag (HTTP Header):**
```
X-Robots-Tag: noindex, nofollow
```

**When to Use noindex:**
- Thank you/confirmation pages
- Internal search results
- User-specific pages
- Thin content pages
- Duplicate filter/sort pages

### Pagination

**Preferred Method: View All Page**
- Single page with all content
- Best for UX and SEO
- Use lazy loading for performance

**Alternative: rel="next/prev" (Deprecated)**
- Google no longer uses these signals
- Implement self-referencing canonicals on each page
- Consider infinite scroll with accessible URLs

**Parameter Handling:**
- Configure in GSC URL Parameters tool
- Use canonical tags to consolidate
- Consider using hashbangs or JavaScript

## Core Web Vitals

### Largest Contentful Paint (LCP)
**Target:** < 2.5 seconds

**Optimization:**
- Optimize server response time
- Use CDN for static assets
- Preload critical resources
- Optimize images (WebP, lazy load)
- Remove render-blocking resources

### First Input Delay (FID) / Interaction to Next Paint (INP)
**Target:** < 100ms (FID) / < 200ms (INP)

**Optimization:**
- Minimize JavaScript execution time
- Break up long tasks
- Use web workers for heavy processing
- Optimize event handlers
- Reduce third-party script impact

### Cumulative Layout Shift (CLS)
**Target:** < 0.1

**Optimization:**
- Set explicit dimensions for images/videos
- Reserve space for ad slots
- Avoid inserting content above existing content
- Use `font-display: swap` for web fonts
- Preload critical fonts

### Measurement Tools
- Google PageSpeed Insights
- Chrome DevTools Lighthouse
- Web Vitals Chrome Extension
- Google Search Console CWV report
- CrUX Dashboard

## Site Architecture

### URL Structure

**Best Practices:**
```
Good:  https://example.com/category/product-name
Bad:   https://example.com/p?id=12345&cat=7
Bad:   https://example.com/2025/01/15/this-is-a-very-long-url-that-goes-on
```

**Guidelines:**
- Keep URLs short (under 60 characters ideal)
- Use hyphens, not underscores
- Lowercase only
- Include target keyword
- Logical hierarchy reflects site structure
- Avoid unnecessary parameters
- Use HTTPS

### Internal Linking Strategy

**Link Distribution:**
- Homepage: Highest authority, link to key sections
- Category pages: Link to subcategories and top products
- Content pages: Cross-link related content
- Footer: Site-wide links to important pages

**Anchor Text:**
- Use descriptive, keyword-rich anchor text
- Vary anchor text naturally
- Avoid "click here" or generic anchors
- Don't over-optimize (avoid exact match abuse)

**Link Depth:**
- Important pages: 3 clicks or fewer from homepage
- Audit orphan pages (no internal links)
- Use breadcrumbs for hierarchy signals

### Information Architecture

**Flat vs. Deep Structure:**
```
Flat (Recommended):
Homepage → Category → Product (3 levels)

Deep (Avoid):
Homepage → Section → Category → Subcategory → Product (5+ levels)
```

**Siloing:**
- Group related content thematically
- Internal links primarily within silos
- Strategic cross-silo linking for authority flow

## Structured Data / Schema Markup

### Common Schema Types

**Organization:**
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Company Name",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "sameAs": [
    "https://twitter.com/company",
    "https://linkedin.com/company/company"
  ]
}
```

**Article:**
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Article Title",
  "author": {
    "@type": "Person",
    "name": "Author Name"
  },
  "datePublished": "2025-01-15",
  "dateModified": "2025-01-15"
}
```

**FAQ:**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "Question text?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Answer text."
    }
  }]
}
```

**Product:**
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Product Name",
  "offers": {
    "@type": "Offer",
    "price": "99.99",
    "priceCurrency": "USD"
  }
}
```

### Implementation
- Use JSON-LD format (Google preferred)
- Place in `<head>` or end of `<body>`
- Test with Google Rich Results Test
- Monitor in GSC Enhancements report

## Mobile-First Indexing

### Requirements
- Mobile version contains all important content
- Same meta tags on mobile and desktop
- Structured data on mobile version
- Images/videos accessible on mobile
- Proper mobile viewport configuration

### Mobile Optimization
```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

**Checklist:**
- [ ] Responsive design (preferred)
- [ ] Touch-friendly tap targets (48px minimum)
- [ ] Readable text without zooming
- [ ] No horizontal scrolling
- [ ] Fast mobile load time
- [ ] No intrusive interstitials

## Technical SEO Audit Checklist

### Crawlability
- [ ] robots.txt accessible and correct
- [ ] XML sitemap exists and submitted
- [ ] No critical pages blocked
- [ ] Redirect chains eliminated
- [ ] 404 errors addressed
- [ ] Server response time < 200ms

### Indexation
- [ ] Canonical tags on all pages
- [ ] noindex only on intended pages
- [ ] Duplicate content addressed
- [ ] Thin content improved or noindexed
- [ ] Pagination handled correctly

### On-Page
- [ ] Unique title tags (30-60 chars)
- [ ] Unique meta descriptions (120-160 chars)
- [ ] Single H1 per page
- [ ] Proper heading hierarchy
- [ ] Image alt text complete
- [ ] Internal links functional

### Performance
- [ ] Core Web Vitals passing
- [ ] Mobile-friendly
- [ ] HTTPS implemented
- [ ] Images optimized
- [ ] Critical CSS inlined
- [ ] JavaScript deferred

### Structured Data
- [ ] Organization schema
- [ ] Breadcrumb schema
- [ ] Relevant page-type schema
- [ ] No validation errors
