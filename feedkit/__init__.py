"""FeedKit — RSS/Atom feed collection with curated catalog."""

from feedkit.core import fetch_feed
from feedkit.catalog import search_catalog, get_catalog_stats
from feedkit.storage import FeedStore

__all__ = ["fetch_feed", "search_catalog", "get_catalog_stats", "FeedStore"]
__version__ = "0.1.0"
