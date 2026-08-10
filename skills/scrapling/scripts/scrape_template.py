#!/usr/bin/env python3
"""
Scrapling 通用抓取模板 — 复制后按需修改即可使用。

运行方式:
    /Users/kane/.workbuddy/binaries/python/envs/scrapling/bin/python3 this_script.py
"""

import json
import sys
import asyncio
from scrapling import Fetcher
from scrapling.fetchers import StealthyFetcher, DynamicFetcher, FetcherSession
from scrapling.spiders import Spider, Response


# ============================================================
# 模式一：单页静态抓取 (Fetcher)
# ============================================================
def scrape_single_page(url: str, output_file: str | None = None):
    """抓取单个静态页面，提取内容并输出。"""
    page = Fetcher.get(url)

    # 提取标题
    title = page.css('title::text').get() or page.css('h1::text').get()

    # 提取所有链接
    links = page.css('a::attr(href)').getall()

    # 提取正文 markdown
    markdown_content = page.markdown()

    result = {
        "url": url,
        "title": title,
        "link_count": len(links),
        "links": links,
        "markdown": markdown_content,
    }

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到 {output_file}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    return result


# ============================================================
# 模式二：隐身模式抓取 (StealthyFetcher) — 绕过 Cloudflare
# ============================================================
def scrape_stealthy(url: str, output_file: str | None = None):
    """使用隐身模式抓取受保护页面。"""
    page = StealthyFetcher.fetch(url)
    
    title = page.css('title::text').get()
    content = page.markdown()

    result = {
        "url": url,
        "title": title,
        "markdown": content,
    }

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到 {output_file}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    return result


# ============================================================
# 模式三：多页列表爬取 (Spider)
# ============================================================
class ListSpider(Spider):
    """通用列表爬虫 — 逐页遍历，收集每页的条目。"""

    name = "list_spider"
    start_urls: list[str] = []
    concurrent_requests = 3
    download_delay = 1  # 秒
    obey_robots = True

    # --- 按目标站点修改以下选择器 ---
    item_selector = ".card"          # 每个条目的容器
    title_selector = "h2::text"       # 条目标题
    link_selector = "a::attr(href)"   # 条目链接
    next_page_selector = ".next a::attr(href)"  # 下一页链接
    # --------------------------------

    async def parse(self, response: Response):
        for item in response.css(self.item_selector):
            yield {
                "title": item.css(self.title_selector).get(),
                "link": item.css(self.link_selector).get(),
            }

        next_page = response.css(self.next_page_selector).get()
        if next_page:
            yield response.follow(next_page)


def scrape_list(start_urls: list[str], output_file: str = "output.json"):
    """多页列表爬取入口。"""
    spider = ListSpider()
    spider.start_urls = start_urls
    result = asyncio.run(spider.start_async())
    result.items.to_json(output_file)
    print(f"抓取完成，共 {len(result.items)} 条，已保存到 {output_file}")
    return result


# ============================================================
# 模式四：动态页面抓取 (DynamicFetcher) — JS 渲染
# ============================================================
def scrape_dynamic(url: str, wait_selector: str | None = None):
    """抓取需要 JS 渲染的动态页面。

    Args:
        url: 目标页面 URL
        wait_selector: 等待某个 CSS 选择器出现后再提取（如 '#app .loaded'）
    """
    page = DynamicFetcher.fetch(url, headless=True, wait_selector=wait_selector)

    title = page.css('title::text').get()
    body_text = page.css('body').markdown()

    print(f"标题: {title}")
    print(f"正文长度: {len(body_text)} 字符")
    return page


# ============================================================
# 主入口
# ============================================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 scrape_template.py single <url> [output.json]")
        print("  python3 scrape_template.py stealthy <url> [output.json]")
        print("  python3 scrape_template.py list <url1> <url2> ... [output.json]")
        print("  python3 scrape_template.py dynamic <url>")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "single":
        url = sys.argv[2]
        out = sys.argv[3] if len(sys.argv) > 3 else None
        scrape_single_page(url, out)

    elif mode == "stealthy":
        url = sys.argv[2]
        out = sys.argv[3] if len(sys.argv) > 3 else None
        scrape_stealthy(url, out)

    elif mode == "list":
        urls = sys.argv[2:-1]
        out = sys.argv[-1] if sys.argv[-1].endswith(".json") else "output.json"
        scrape_list(urls, out)

    elif mode == "dynamic":
        url = sys.argv[2]
        scrape_dynamic(url)

    else:
        print(f"未知模式: {mode}")
        sys.exit(1)
