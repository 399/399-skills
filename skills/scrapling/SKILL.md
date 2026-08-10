---
name: scrapling
description: "Use Scrapling (v0.4.13) for web scraping, content extraction, and crawling. This skill should be used when the user needs to fetch, parse, or extract data from any web page -- including static HTML, JavaScript-rendered pages, and Cloudflare-protected sites. Covers Fetcher, StealthyFetcher, DynamicFetcher, Spider crawling framework, CLI tools, and adaptive element tracking. Trigger keywords: scrape, crawling, fetch web page, extract content, web data, Scrapling, 抓取, 网页采集, 爬虫."
agent_created: true
---

# Scrapling Web Scraping Skill

## Environment

Scrapling is installed in an isolated Python 3.13 venv. Always use these absolute paths:

| Component | Path |
|---|---|
| **Python** | `/Users/kane/.workbuddy/binaries/python/envs/scrapling/bin/python3` |
| **CLI** | `/Users/kane/.workbuddy/binaries/python/envs/scrapling/bin/scrapling` |

The `scrapling[all]` package is installed, which includes Fetchers, Spiders, MCP/AI integration, interactive shell, Playwright, patchright, curl_cffi, and all browser dependencies.

**All scraping scripts must be run with this Python path.** Do NOT use the system Python.

## When to Use Which Fetcher

| Fetcher | Use Case | Anti-Bot |
|---|---|---|
| `Fetcher` | Static HTML pages, simple API calls, fastest | ❌ No |
| `StealthyFetcher` | Pages with Cloudflare/WAF protection, TLS fingerprinting | ✅ Yes |
| `DynamicFetcher` | JavaScript-rendered SPA pages (React/Vue), needs browser | ⚠️ Partial |

**Decision flow:**
1. Try `Fetcher` first (fastest, lowest cost)
2. If blocked or content missing → try `StealthyFetcher`
3. If content needs JavaScript execution → use `DynamicFetcher`

## Quick Start Patterns

### Pattern 1: Basic Static Page Fetch

```python
from scrapling import Fetcher

page = Fetcher.get('https://example.com')

# Text extraction
title = page.css('h1::text').get()
all_links = page.css('a::attr(href)').getall()

# XPath
elements = page.xpath('//div[@class="content"]/p')

# Text search
results = page.search('keyword')

# Convert to markdown
md = page.markdown()
```

### Pattern 2: Stealthy Fetch (Cloudflare Bypass)

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch('https://protected-site.com')
data = page.css('.content').getall()
```

### Pattern 3: Dynamic JS-Rendered Page

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch('https://spa-site.com', headless=True)
content = page.css('#app .result').getall()
```

### Pattern 4: Persistent Session (Login/Multi-page)

```python
from scrapling.fetchers import FetcherSession

session = FetcherSession()
login_page = session.get('https://site.com/login')
# ... submit login form ...
dashboard = session.get('https://site.com/dashboard')
```

### Pattern 5: Multi-page Spider Crawling

```python
import asyncio
from scrapling.spiders import Spider, Response

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com/page/1"]
    concurrent_requests = 5

    async def parse(self, response: Response):
        for item in response.css('.card'):
            yield {
                "title": item.css('h2::text').get(),
                "link": item.css('a::attr(href)').get(),
            }
        # Follow pagination
        next_page = response.css('.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page)

result = asyncio.run(MySpider().start_async())
result.items.to_json("output.json")
```

## CLI Quick Reference

```bash
# Interactive scraping shell
/Users/kane/.workbuddy/binaries/python/envs/scrapling/bin/scrapling shell

# Extract page content to markdown
/Users/kane/.workbuddy/binaries/python/envs/scrapling/bin/scrapling extract get 'https://example.com' output.md

# Extract with stealth mode
/Users/kane/.workbuddy/binaries/python/envs/scrapling/bin/scrapling extract fetch 'https://example.com' output.md

# Dynamic page extraction (no headless = show browser)
/Users/kane/.workbuddy/binaries/python/envs/scrapling/bin/scrapling extract fetch 'https://example.com' output.md --no-headless
```

## Adaptive Selectors (Resilience)

Scrapling can auto-relocate elements when site structure changes:

```python
from scrapling import Fetcher

# First, capture the element's "fingerprint"
page1 = Fetcher.get('https://example.com/v1')
element = page1.css('.price-tag')
fingerprint = element.get_fingerprint()

# Later, when the site changes CSS classes
page2 = Fetcher.get('https://example.com/v2')  # .price-tag renamed to .cost-label
same_element = page2.find_similar(fingerprint)  # Automatically finds it!
```

## Common Selection Methods

| Method | Example | Returns |
|---|---|---|
| `css(selector)` | `page.css('.title::text')` | Element/Text list |
| `xpath(expr)` | `page.xpath('//h1')` | Element list |
| `search(text)` | `page.search('price')` | Elements containing text |
| `regex(pattern)` | `page.regex(r'\d+\.\d{2}')` | Matched text |
| `filter(func)` | `page.filter(lambda e: ...)` | Filtered elements |
| `find_similar(fp)` | `page.find_similar(fingerprint)` | Similar elements |

## Selection Result Methods

After selecting elements, use these to extract data:

```python
el.get()         # Get first match (text or element)
el.getall()      # Get all matches as list
el.attrib['href'] # Get attribute value
el.text          # Get inner text
el.markdown()    # Convert inner HTML to markdown
```

## Best Practices

1. **Always use the venv Python path** — never system Python
2. **Start with Fetcher, escalate to StealthyFetcher** only when needed
3. **Respect robots.txt** — Scrapling supports it via `Spider(obey_robots=True)`
4. **Use CSS selectors over XPath** when possible — faster and more readable
5. **Add delays between requests** in Spider mode: `download_delay=1`
6. **Save responses for development**: `Spider(dev_mode=True)` caches responses to disk
7. **Export results to structured formats**: `.to_json()`, `.to_csv()`, `.to_dicts()`

## Reference Script

A reusable scraping template is available at `scripts/scrape_template.py` within this skill. Use it as a starting point for custom scraping tasks by copying and modifying it.
