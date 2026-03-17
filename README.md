# FeedKit

> RSS/Atom feed collection with 421 curated, verified feeds. Python MCP server included.

```python
from feedkit import search_catalog, fetch_feed, FeedStore
from feedkit.core import collect

# Search the built-in catalog
feeds = search_catalog("cloudflare")

# Fetch a feed
entries = await fetch_feed("https://blog.cloudflare.com/rss/")
for entry in entries:
    print(entry.title, entry.url)

# Subscribe and collect
store = FeedStore()
store.subscribe("https://blog.cloudflare.com/rss/", category="tech")
result = await collect(store)  # async parallel fetch
print(f"{result.new_articles} new articles")
```

## Features

- **421 curated feeds** — tech blogs, academic, government, news, fact-check. All verified with 778K+ articles collected.
- **Async parallel collection** — fetch hundreds of feeds in under a minute
- **SQLite + FTS5** — local storage with full-text search, no server needed
- **OPML import/export** — interop with Feedly, Inoreader, NetNewsWire
- **MCP server** — 9 tools for Claude Code / MCP clients
- **Feed health monitoring** — track success rates and errors per feed

## Install

```bash
pip install feedkit
```

## CLI

```bash
feedkit search aws                        # search catalog
feedkit search --category technology      # by category
feedkit categories                        # list categories

feedkit subscribe https://example.com/rss # subscribe to a feed
feedkit subscribe-catalog -c technology   # subscribe to entire category
feedkit list                              # list subscriptions

feedkit collect                           # fetch all subscriptions
feedkit latest                            # show latest articles
feedkit find "kubernetes deployment"      # full-text search

feedkit import-opml subs.opml             # import OPML
feedkit export-opml backup.opml           # export OPML
feedkit stats                             # catalog + local stats
```

## MCP Server

```bash
pip install "feedkit[mcp]"
feedkit-mcp  # starts stdio MCP server
```

**9 tools:** fetch_single_feed, search_feed_catalog, catalog_stats, collect_feeds, search_articles, get_latest_articles, subscribe_feed, unsubscribe_feed, list_subscriptions

## Built-in Catalog

421 verified feeds across 5 categories. All audited — hard paywalls (Bloomberg, FT, WSJ) and broken URLs removed.

| Category | Feeds | Subcategories | Examples |
|----------|-------|---------------|---------|
| **technology** | 68 | ai/ml, developer, it_news, security, startup | AWS, Cloudflare, Stripe, Netflix, Spotify, Meta, Go Blog, Rust Blog, Hacker News |
| **science** | 128 | journal, preprint, news, government | Nature, Science, arXiv, bioRxiv, NASA, PLOS, Cambridge, BAIR |
| **finance** | 93 | markets, central_bank, regulatory, crypto | Fed, BOE, BOJ, SEC, CNBC, CoinDesk, Yahoo Finance |
| **society** | 119 | news_us, news_ko, news_intl, factcheck, government | BBC, NPR, NHK, JTBC, Al Jazeera, PolitiFact, Snopes |
| **academia** | 13 | ai_ml, research, institution | Google AI, DeepMind, Stanford HAI, Hugging Face |

### Why not just use awesome-rss-feeds?

| | [awesome-rss-feeds](https://github.com/plenaryapp/awesome-rss-feeds) (2.1K★) | [engineering-blogs](https://github.com/kilimchoi/engineering-blogs) (37.5K★) | **FeedKit** |
|--|---|---|---|
| Feeds | ~500 | ~600 | 421 |
| Scope | General | Tech blogs only | Tech + Science + Finance + News + Factcheck |
| Last content update | 2021 (stale) | 2022 (stale) | **Active (daily collection)** |
| Verified working | No | No | **Yes (778K+ articles collected)** |
| Legal audit | No | No | **Yes (paywall/ToS feeds removed)** |
| pip install | No | No | **Yes** |
| MCP server | No | No | **Yes (9 tools)** |
| OPML | No | No | **Yes** |
| Format | Markdown | Markdown | **JSON + OPML + Markdown** |

## Disclaimer

This package distributes a catalog of **publicly available RSS feed URLs**, not the feed content itself. RSS is a syndication standard — publishing an RSS feed is an explicit invitation for readers to subscribe. FeedKit fetches feeds on the user's behalf and does not store or redistribute copyrighted content.

Feeds behind hard paywalls (Bloomberg, FT, WSJ, Barron's) and feeds with aggressive terms of service have been removed from the catalog.

## License

[MIT](LICENSE)

<!-- mcp-name: io.github.ArkNill/feedkit -->
