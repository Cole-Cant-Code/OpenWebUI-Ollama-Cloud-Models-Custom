"""
title: Sovereign Reader
author: Cole
author_url: https://github.com/Cole-Cant-Code
description: Deep web page reader. Fetches, cleans, and extracts article content from URLs.
required_open_webui_version: 0.4.0
requirements: requests, beautifulsoup4
version: 1.0.0
licence: MIT
"""

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

NOISE_TAGS = ["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript", "svg"]
NOISE_CLASSES = ["sidebar", "menu", "cookie", "banner", "popup", "modal", "advertisement", "social-share", "related-posts", "comment"]


class Tools:
    class Valves(BaseModel):
        timeout: int = Field(default=15, ge=5, le=60, description="Request timeout in seconds")
        max_chars: int = Field(default=8000, ge=1000, le=50000, description="Max characters to extract")
        user_agent: str = Field(
            default="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            description="User-Agent header for requests",
        )

    def __init__(self):
        self.valves = self.Valves()
        self.citation = False

    async def read_webpage(self, url: str, __event_emitter__=None) -> str:
        """
        Fetch a web page and extract its readable content. Use this for deep reading of articles, documentation, blog posts, technical references, or any URL where you need the full text beyond what a search snippet provides.
        :param url: The full URL to read (must start with http:// or https://).
        :return: Clean extracted text with title, description, and source citation.
        """
        if not url.startswith(("http://", "https://")):
            return f"Invalid URL: {url}. Must start with http:// or https://."

        try:
            if __event_emitter__:
                short = url[:60] + ("..." if len(url) > 60 else "")
                await __event_emitter__(
                    {"type": "status", "data": {"description": f"Fetching {short}", "done": False}}
                )

            r = requests.get(
                url,
                timeout=self.valves.timeout,
                headers={"User-Agent": self.valves.user_agent, "Accept": "text/html,application/xhtml+xml,*/*"},
                allow_redirects=True,
            )
            r.raise_for_status()

            content_type = r.headers.get("content-type", "")
            if "html" not in content_type and "xhtml" not in content_type:
                if __event_emitter__:
                    await __event_emitter__(
                        {"type": "status", "data": {"description": f"Non-HTML: {content_type}", "done": True}}
                    )
                return f"Non-HTML content ({content_type}). Raw preview:\n\n```\n{r.text[:self.valves.max_chars]}\n```"

            soup = BeautifulSoup(r.text, "html.parser")

            title = (soup.title.string.strip() if soup.title and soup.title.string else "Untitled")
            meta_desc = ""
            meta_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
            if meta_tag:
                meta_desc = meta_tag.get("content", "")

            for tag in soup(NOISE_TAGS):
                tag.decompose()
            for tag in soup.find_all(
                attrs={
                    "class": lambda c: c
                    and any(noise in str(c).lower() for noise in NOISE_CLASSES)
                }
            ):
                tag.decompose()
            for tag in soup.find_all(
                attrs={
                    "id": lambda i: i
                    and any(noise in str(i).lower() for noise in NOISE_CLASSES)
                }
            ):
                tag.decompose()

            main = soup.find("article") or soup.find("main") or soup.find(role="main") or soup.find("body")
            if not main:
                main = soup

            text = main.get_text(separator="\n", strip=True)
            lines = [line for line in text.split("\n") if line.strip()]
            text = "\n".join(lines)

            truncated = False
            if len(text) > self.valves.max_chars:
                text = text[: self.valves.max_chars]
                truncated = True

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "source",
                        "data": {
                            "document": [text[:2000]],
                            "metadata": [{"source": title, "url": r.url}],
                            "source": {"name": title, "url": r.url},
                        },
                    }
                )
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"Read {len(text):,} chars from {title[:40]}",
                            "done": True,
                        },
                    }
                )

            result = f"# {title}\n"
            if meta_desc:
                result += f"*{meta_desc}*\n"
            result += f"Source: {r.url}\n\n---\n\n{text}"
            if truncated:
                result += f"\n\n---\n*Truncated at {self.valves.max_chars:,} chars. Full page was larger.*"

            return result

        except requests.exceptions.Timeout:
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": "Timed out", "done": True}}
                )
            return f"Timeout after {self.valves.timeout}s fetching {url}."

        except requests.exceptions.HTTPError as e:
            code = e.response.status_code if e.response else "unknown"
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": f"HTTP {code}", "done": True}}
                )
            return f"HTTP {code} fetching {url}."

        except Exception as e:
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": f"Error: {type(e).__name__}", "done": True}}
                )
            return f"Failed to read {url}: {type(e).__name__}: {e}"
