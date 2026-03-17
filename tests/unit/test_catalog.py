"""Tests for catalog.py — curated feed catalog."""

from feedkit.catalog import CatalogFeed, get_catalog_stats, list_categories, search_catalog


def test_catalog_loads():
    """Catalog loads without error."""
    stats = get_catalog_stats()
    assert stats["total_feeds"] > 400


def test_catalog_has_categories():
    categories = list_categories()
    assert len(categories) >= 3
    assert "technology" in categories


def test_catalog_stats_structure():
    stats = get_catalog_stats()
    assert "total_feeds" in stats
    assert "categories" in stats
    assert "languages" in stats
    assert isinstance(stats["categories"], dict)


def test_search_all():
    """Search with no query returns feeds."""
    results = search_catalog(limit=10)
    assert len(results) > 0
    assert len(results) <= 10


def test_search_by_query():
    results = search_catalog("cloud")
    assert len(results) > 0
    assert all(isinstance(f, CatalogFeed) for f in results)


def test_search_by_category():
    results = search_catalog(category="technology")
    assert len(results) > 0
    assert all(f.category == "technology" for f in results)


def test_search_by_language():
    results = search_catalog(language="ko")
    assert all(f.language == "ko" for f in results)


def test_search_no_results():
    results = search_catalog("zzzznonexistent999")
    assert len(results) == 0


def test_search_limit():
    results = search_catalog(limit=5)
    assert len(results) <= 5


def test_catalog_feed_fields():
    results = search_catalog(limit=1)
    f = results[0]
    assert f.url
    assert f.domain
    assert f.category
