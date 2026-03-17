"""Built-in curated feed catalog — 449 verified RSS/Atom feeds."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

_CATALOG_PATH = Path(__file__).parent / "data" / "feeds.json"
_catalog: list[dict] | None = None


@dataclass
class CatalogFeed:
    """A feed from the built-in catalog."""

    url: str
    title: str
    category: str
    subcategory: str
    language: str
    domain: str


def _load_catalog() -> list[dict]:
    global _catalog
    if _catalog is None:
        with open(_CATALOG_PATH, encoding="utf-8") as f:
            _catalog = json.load(f)
    return _catalog


def search_catalog(
    query: str = "",
    *,
    category: str = "",
    language: str = "",
    limit: int = 50,
) -> list[CatalogFeed]:
    """Search the built-in feed catalog.

    Args:
        query: Search by title or domain (case-insensitive substring match).
        category: Filter by category (e.g., "technology", "science", "finance").
        language: Filter by language (e.g., "en", "ko").
        limit: Maximum results to return.
    """
    catalog = _load_catalog()
    results = []

    q = query.lower()
    for entry in catalog:
        if category and entry.get("category", "") != category:
            continue
        if language and entry.get("language", "") != language:
            continue
        if q:
            title = entry.get("title", "").lower()
            domain = entry.get("domain", "").lower()
            url = entry.get("url", "").lower()
            if q not in title and q not in domain and q not in url:
                continue

        results.append(CatalogFeed(
            url=entry["url"],
            title=entry.get("title", ""),
            category=entry.get("category", ""),
            subcategory=entry.get("subcategory", ""),
            language=entry.get("language", "en"),
            domain=entry.get("domain", ""),
        ))

        if len(results) >= limit:
            break

    return results


def get_catalog_stats() -> dict:
    """Get catalog statistics."""
    catalog = _load_catalog()
    categories: dict[str, int] = {}
    languages: dict[str, int] = {}

    for entry in catalog:
        cat = entry.get("category", "unknown")
        lang = entry.get("language", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
        languages[lang] = languages.get(lang, 0) + 1

    return {
        "total_feeds": len(catalog),
        "categories": dict(sorted(categories.items())),
        "languages": dict(sorted(languages.items())),
    }


def list_categories() -> list[str]:
    """List all available categories."""
    catalog = _load_catalog()
    return sorted({entry.get("category", "") for entry in catalog if entry.get("category")})
