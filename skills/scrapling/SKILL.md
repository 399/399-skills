---
name: scrapling
description: "Use Scrapling (v0.4.13) for web scraping, content extraction, and crawling. This skill should be used when the user needs to fetch, parse, or extract data from any web page -- including static HTML, JavaScript-rendered pages, and Cloudflare-protected sites. Covers Fetcher, StealthyFetcher, DynamicFetcher, Spider crawling framework, CLI tools, and adaptive element tracking. Trigger keywords: scrape, crawling, fetch web page, extract content, web data, Scrapling, 抓取, 网页采集, 爬虫."
agent_created: true
---

# Scrapling Web Scraping Skill

## Pre-flight Check (MANDATORY -- run before ANY scraping task)

Before executing any scraping code, check whether Scrapling is installed. If not, guide the user through installation.

### Step 1: Detect Managed Python

Check for WorkBuddy's managed Python 3.13 (preferred):

```bash
ls $HOME/.workbuddy/binaries/python/versions/3.13.*/bin/python3 2>/dev/null
```

If found, use it as `MANAGED_PYTHON`. Otherwise, fall back to system Python and verify version >= 3.10:

```bash
python3 --version 2>/dev/null || python3 -c "import sys; assert sys.version_info >= (3,10), 'Need Python 3.10+'"
```

### Step 2: Check for Existing Scrapling Installation

```bash
$MANAGED_PYTHON -c "import scrapling; print(scrapling.__version__)" 2>/dev/null
```

If the above succeeds, Scrapling is ready. Skip to "Using Scrapling".

Also check if a dedicated venv already exists:

```bash
test -f $HOME/.workbuddy/binaries/python/envs/scrapling/bin/python3 && echo "VENV_EXISTS"
```

### Step 3: Install (if missing)

If Scrapling is NOT installed, **guide the user through these steps** -- never auto-install without asking:

**With managed Python (WorkBuddy environment):**

```bash
# Create venv
$MANAGED_PYTHON -m venv $HOME/.workbuddy/binaries/python/envs/scrapling

# Install Scrapling with all features
$HOME/.workbuddy/binaries/python/envs/scrapling/bin/pip install "scrapling[all]"

# Install browser dependencies (Playwright Chromium etc.)
$HOME/.workbuddy/binaries/python/envs/scrapling/bin/scrapling install
```

**Without managed Python (fallback -- system Python 3.10+):**

```bash
python3 -m venv $HOME/.scrapling-venv
$HOME/.scrapling-venv/bin/pip install "scrapling[all]"
$HOME/.scrapling-venv/bin/scrapling install
```

After installation, verify:

```bash
$PYTHON_PATH -c "from scrapling import Fetcher; from scrapling.fetchers import StealthyFetcher; print('OK')"
```

### Step 4: Determine Runtime Paths

Once installed, resolve the active paths:

| Component | Managed Python path | Fallback path |
|---|---|---|
| **Python** | `$HOME/.workbuddy/binaries/python/envs/scrapling/bin/python3` | `$HOME/.scrapling-venv/bin/python3` |
| **CLI** | `$HOME/.workbuddy/binaries/python/envs/scrapling/bin/scrapling` | `$HOME/.scrapling-venv/bin/scrapling` |

Store the resolved Python path in a variable (e.g., `SCRAPLING_PYTHON`) and use it for all subsequent commands.

**All scraping scripts must use this resolved Python path.** Never use bare `python3`.

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

In all CLI examples below, `$SCRAPLING_CLI` refers to the resolved CLI path from the pre-flight check.

```bash
# Interactive scraping shell
$SCRAPLING_CLI shell

# Extract page content to markdown
$SCRAPLING_CLI extract get 'https://example.com' output.md

# Extract with stealth mode
$SCRAPLING_CLI extract fetch 'https://example.com' output.md

# Dynamic page extraction (no headless = show browser)
$SCRAPLING_CLI extract fetch 'https://example.com' output.md --no-headless
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

A reusable scraping template is available at `scripts/scrape_template.py` within this skill. To use it:

1. Copy it to the working directory
2. Update the shebang line to `$SCRAPLING_PYTHON` (from the pre-flight check)
3. Run with `$SCRAPLING_PYTHON scrape_template.py single <url>`

The template supports four CLI modes: `single`, `stealthy`, `list`, `dynamic`.
