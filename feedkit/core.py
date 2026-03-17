"""Core feed fetching logic — async HTTP + feedparser."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime

import feedparser
import httpx

from feedkit.storage import Article, FeedStore

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 15.0
DEFAULT_CONCURRENCY = 20
USER_AGENT = "FeedKit/0.1.0 (+https://github.com/QuartzUnit/feedkit)"


@dataclass
class FeedEntry:
    """A single entry from a feed."""

    title: str = ""
    url: str = ""
    summary: str = ""
    published: str | None = None
    author: str = ""
    feed_url: str = ""
    feed_title: str = ""
    guid: str = ""


@dataclass
class CollectResult:
    """Result of a bulk feed collection."""

    feeds_total: int = 0
    feeds_ok: int = 0
    feeds_error: int = 0
    new_articles: int = 0
    duration_ms: float = 0.0
    errors: list[dict] = field(default_factory=list)


async def fetch_feed(
    url: str,
    *,
    count: int = 50,
    timeout: float = DEFAULT_TIMEOUT,
) -> list[FeedEntry]:
    """Fetch and parse a single RSS/Atom feed.

    Args:
        url: Feed URL.
        count: Maximum entries to return.
        timeout: HTTP timeout in seconds.
    """
    headers = {"User-Agent": USER_AGENT}

    async with httpx.AsyncClient(timeout=httpx.Timeout(timeout), headers=headers, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()

    parsed = feedparser.parse(response.text)
    feed_title = parsed.feed.get("title", "")
    entries = []

    for entry in parsed.entries[:count]:
        guid = entry.get("id") or entry.get("link") or entry.get("title", "")
        published = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                published = datetime(*entry.published_parsed[:6]).isoformat()
            except (ValueError, TypeError):
                pass

        entries.append(FeedEntry(
            title=entry.get("title", ""),
            url=entry.get("link", ""),
            summary=_clean_summary(entry.get("summary", "")),
            published=published,
            author=entry.get("author", ""),
            feed_url=url,
            feed_title=feed_title,
            guid=guid,
        ))

    return entries


async def collect(
    store: FeedStore,
    *,
    category: str = "",
    concurrency: int = DEFAULT_CONCURRENCY,
    timeout: float = DEFAULT_TIMEOUT,
    count_per_feed: int = 50,
) -> CollectResult:
    """Collect articles from all subscribed feeds.

    Args:
        store: FeedStore instance.
        category: Only collect from this category (empty = all).
        concurrency: Max concurrent HTTP requests.
        timeout: Per-feed HTTP timeout.
        count_per_feed: Max entries per feed.
    """
    start = time.monotonic()
    subs = store.list_subscriptions()

    if category:
        subs = [s for s in subs if s.category == category]

    result = CollectResult(feeds_total=len(subs))
    semaphore = asyncio.Semaphore(concurrency)

    async def _fetch_one(feed_url: str) -> tuple[str, list[FeedEntry] | None, str]:
        async with semaphore:
            try:
                entries = await fetch_feed(feed_url, count=count_per_feed, timeout=timeout)
                return feed_url, entries, ""
            except Exception as e:
                return feed_url, None, str(e)

    tasks = [_fetch_one(s.feed_url) for s in subs]
    outcomes = await asyncio.gather(*tasks)

    for feed_url, entries, error in outcomes:
        if entries is not None:
            result.feeds_ok += 1
            articles = [
                Article(
                    guid=e.guid,
                    feed_url=e.feed_url,
                    title=e.title,
                    url=e.url,
                    summary=e.summary,
                    author=e.author,
                    published=e.published,
                )
                for e in entries
            ]
            new = store.save_articles(articles)
            result.new_articles += new
            store.update_fetch_status(feed_url, success=True)
        else:
            result.feeds_error += 1
            result.errors.append({"feed_url": feed_url, "error": error})
            store.update_fetch_status(feed_url, success=False, error=error)

    result.duration_ms = (time.monotonic() - start) * 1000
    return result


def _clean_summary(text: str, max_len: int = 500) -> str:
    """Strip HTML tags and truncate summary."""
    import re

    clean = re.sub(r"<[^>]+>", "", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    if len(clean) > max_len:
        clean = clean[:max_len] + "..."
    return clean
