# FeedKit

[![PyPI](https://img.shields.io/pypi/v/feedkit)](https://pypi.org/project/feedkit/)
[![Python](https://img.shields.io/pypi/pyversions/feedkit)](https://pypi.org/project/feedkit/)
[![License](https://img.shields.io/github/license/QuartzUnit/feedkit)](https://github.com/QuartzUnit/feedkit/blob/main/LICENSE)
[![Tests](https://img.shields.io/badge/tests-34%20passed-brightgreen)]()

> [English](README.md)

**444개 검증된 피드**를 내장한 RSS/Atom 피드 수집 도구. CLI + Python API + MCP 서버.

## 빠른 시작

```bash
pip install feedkit

feedkit search cloudflare           # 내장 카탈로그 검색
feedkit subscribe-catalog -c technology   # 기술 피드 68개 일괄 구독
feedkit collect                     # 전체 구독 수집 (비동기 병렬)
feedkit find "kubernetes"           # 수집된 기사 전문 검색
```

## 설치

```bash
pip install feedkit             # 코어 (CLI + Python API)
pip install "feedkit[mcp]"      # + MCP 서버
pip install "feedkit[all]"      # + MCP + OPML 가져오기/내보내기
```

**요구사항:** Python 3.11+

## CLI 레퍼런스

### 카탈로그 명령어

#### `feedkit search [QUERY]`

444개 검증 피드 카탈로그를 검색합니다.

```bash
feedkit search aws                    # 제목 또는 도메인으로 검색
feedkit search --category science     # 카테고리 필터
feedkit search --language ko          # 언어 필터
feedkit search -c finance -l en -n 50 # 필터 조합
feedkit search -j                     # JSON 출력 (파이프용)
```

| 옵션 | 축약 | 기본값 | 설명 |
|------|------|--------|------|
| `--category` | `-c` | | 카테고리 필터 |
| `--language` | `-l` | | 언어 코드 (`en`, `ko`, `ja`, `zh`) |
| `--limit` | `-n` | 20 | 최대 결과 수 |
| `--json-output` | `-j` | | JSON으로 출력 |

#### `feedkit categories`

카탈로그 카테고리 목록을 표시합니다.

#### `feedkit stats`

카탈로그 및 로컬 구독 통계를 표시합니다.

### 구독 명령어

#### `feedkit subscribe <URL>`

피드를 구독합니다.

```bash
feedkit subscribe https://blog.cloudflare.com/rss/
feedkit subscribe https://example.com/rss -c tech -t "My Feed"
```

#### `feedkit subscribe-catalog -c <CATEGORY>`

카테고리의 모든 피드를 일괄 구독합니다.

```bash
feedkit subscribe-catalog -c technology   # 기술 피드 68개 전체 구독
feedkit subscribe-catalog -c science      # 과학 피드 128개 전체 구독
```

#### `feedkit unsubscribe <URL>`

구독을 해제하고 수집된 기사를 삭제합니다.

#### `feedkit list`

현재 구독 목록을 수집/에러 횟수와 함께 표시합니다.

### 수집 명령어

#### `feedkit collect`

모든 구독 피드에서 새 기사를 수집합니다 (비동기 병렬).

```bash
feedkit collect                    # 전체 수집
feedkit collect -c technology      # 기술 피드만
feedkit collect -n 50              # 최대 50개 동시 요청
```

#### `feedkit latest`

최근 수집된 기사를 표시합니다.

```bash
feedkit latest                # 최근 20개
feedkit latest -n 50          # 최근 50개
feedkit latest -c finance     # 금융 카테고리만
```

#### `feedkit find <QUERY>`

수집된 기사에서 전문 검색 (SQLite FTS5).

```bash
feedkit find "kubernetes deployment"
feedkit find "large language model" -n 50
```

### OPML 명령어

#### `feedkit import-opml <PATH>`

OPML 파일에서 피드를 가져옵니다 (Feedly, Inoreader, NetNewsWire 등).

#### `feedkit export-opml <PATH>`

현재 구독을 OPML로 내보냅니다.

## Python API

```python
from feedkit import search_catalog, fetch_feed, get_catalog_stats, FeedStore
from feedkit.core import collect

# 내장 카탈로그 검색
feeds = search_catalog("cloudflare")
feeds = search_catalog(category="technology", language="en", limit=50)

# 단일 피드 가져오기 (async)
entries = await fetch_feed("https://blog.cloudflare.com/rss/")
for entry in entries:
    print(entry.title, entry.url, entry.published)

# 구독 + 수집
store = FeedStore()                              # SQLite: ~/.feedkit/feedkit.db
store.subscribe("https://blog.cloudflare.com/rss/", category="tech")
result = await collect(store, concurrency=20)    # 비동기 병렬 수집
print(f"{result.new_articles} new, {result.feeds_ok}/{result.feeds_total} OK")

# 수집된 기사 검색 (FTS5)
articles = store.search("kubernetes", count=10)

# 최근 기사
articles = store.get_latest(count=20, category="tech")

store.close()
```

## MCP 서버

```bash
pip install "feedkit[mcp]"
feedkit-mcp                    # stdio MCP 서버 시작
```

### 도구 레퍼런스

| # | 도구 | 파라미터 | 설명 |
|---|------|---------|------|
| 1 | `fetch_single_feed` | `url`, `count=10` | RSS/Atom URL에서 항목 가져오기 (구독 불필요) |
| 2 | `search_feed_catalog` | `query`, `category`, `language`, `count=20` | 444개 피드 카탈로그 검색 |
| 3 | `catalog_stats` | | 카탈로그 통계 (전체, 카테고리별, 언어별) |
| 4 | `subscribe_feed` | `url`, `title`, `category` | 피드 구독 |
| 5 | `unsubscribe_feed` | `url` | 구독 해제 |
| 6 | `list_subscriptions` | | 구독 목록 + 상태 |
| 7 | `collect_feeds` | `category` | 모든 구독에서 새 기사 수집 |
| 8 | `search_articles` | `query`, `count=10` | 수집된 기사 전문 검색 |
| 9 | `get_latest_articles` | `category`, `count=20` | 최근 수집 기사 조회 |

## 내장 카탈로그

444개 검증 피드, 6개 카테고리. 페이월(Bloomberg, FT, WSJ) 및 깨진 URL 제거 완료.

| 카테고리 | 피드 수 | 하위 카테고리 | 주요 피드 |
|---------|-------:|-------------|----------|
| **technology** | 68 | ai_ml, developer, it_news, security, startup, ... | AWS, Cloudflare, Stripe, Netflix, HN, Go Blog, Rust Blog |
| **science** | 128 | journal, preprint, news, government | Nature, Science, arXiv, bioRxiv, medRxiv, NASA, PLOS |
| **society** | 119 | news_us, news_ko, news_uk, news_intl, factcheck, ... | BBC, NPR, NYT, NHK, JTBC, PolitiFact, Snopes |
| **finance** | 89 | markets, central_bank, regulatory, crypto | Fed, BOE, BOJ, SEC, CNBC, CoinDesk, Yahoo Finance |
| **pets** | 27 | veterinary, community, blog, health | AKC, PetMD, ASPCA, dvm360, r/dogs, r/cats |
| **academia** | 13 | ai_ml, research, institution | Google AI, DeepMind, Stanford HAI, Hugging Face |

**언어:** 영어 (381), 한국어 (47), 일본어 (14), 중국어 (2)

전체 피드 목록: [CATALOG.md](CATALOG.md)

## 면책 조항

이 패키지는 **공개적으로 이용 가능한 RSS 피드 URL 카탈로그**를 배포하며, 피드 콘텐츠 자체는 배포하지 않습니다. RSS는 신디케이션 표준으로, RSS 피드를 게시하는 것은 구독자의 구독을 명시적으로 초대하는 것입니다. FeedKit은 사용자를 대신하여 피드를 가져오며 저작권이 있는 콘텐츠를 저장하거나 재배포하지 않습니다.

하드 페이월(Bloomberg, FT, WSJ, Barron's) 및 공격적인 이용약관을 가진 피드는 카탈로그에서 제거되었습니다.

## 라이선스

[MIT](LICENSE)
