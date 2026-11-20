# Israel-Online-Stores

Open data index of Israeli online retailers, intended as a data store backing online shopping agents (LLM-driven product search, price comparison, sourcing workflows, etc.).

Source: Zap (zap.co.il) store directory, refreshed 2026-11-20, plus manual research. 5,590 stores, every one with at least one category: 705 from Zap's own category facets, about 3,600 from Hebrew keywords in Zap's store description (`scripts/category_map.json` → `description_keywords`), and about 1,280 with a city-only or vague description tagged `other` for now. `categorisation.categories_source` says which (`zap_facet` | `description_keywords` | `default_other`). Refreshed monthly (see below).

## Files

- `stores-index.json` — slim index for agents (name, website, domain, Zap id/url, categories, is_tech, city, description). Load this first.
- `stores.json` — full records (nested schema, see DATA_DICTIONARY.md).
- `scripts/scrape_zap.py` — crawls the Zap store directory plus every main/sub-category facet into `.cache/` (stdlib only, resumable, ~1 req/s).
- `scripts/merge.py` — merges the crawl into `stores.json`, writes `stores-index.json`.
- `scripts/category_map.json` — Hebrew Zap category to category-vocabulary tags.
- `build.py` — original April 2026 build (legacy; superseded by the scripts above).

## Refresh (last run 2026-11-20)

Needs an Israeli residential IP for zap.co.il (plain HTTP, no browser; headless browsers are rejected).

```
python3 scripts/scrape_zap.py                          # ~20 min, ~1,500 requests, writes .cache/zap_stores.json
python3 scripts/merge.py                              # rewrites stores.json + stores-index.json
```

The scrape is resumable (page cache in `.cache/html/`, gitignored; delete it to force a fresh crawl). `merge.py` matches by Zap siteid, then website domain, then name; keeps hand-filled fields; flags stores no longer on Zap as `not_on_zap_2026-11`. If Google Translate rate-limits, new stores keep `descriptions.en` null; re-run merge later. Category facet lists are fetched from `GET /models/getmorefilters?dbid=245399|245408&sogname=g-stores` (the "more..." popup), not the page HTML (which shows only 7 per facet).

Zap quirks: unfiltered directory pagination runs to page ~399 (14 stores/page); facet counts shown by Zap overstate what pagination returns by about 20%.

## Intended use

The raw JSON is designed to be consumed directly by agents. Give your agent the raw GitHub URL and it can parse the list, filter by fields (e.g. "stores that deliver to Eilat and accept Bit"), and select candidate vendors for a product search.

Raw URL:

```
https://raw.githubusercontent.com/danielrosehill/Israel-Online-Stores/main/stores.json
https://raw.githubusercontent.com/danielrosehill/Israel-Online-Stores/main/stores-index.json   (slim)
```

### Drop-in snippet for a Claude Code / agent skill

```markdown
## Israeli store directory

When sourcing products from Israeli online retailers, fetch the canonical
store index from:

    https://raw.githubusercontent.com/danielrosehill/Israel-Online-Stores/main/stores.json

It is a flat JSON array. Each record has `name` and `website` at the top
level; everything else lives under `store_details`, grouped by theme
(descriptions, contact, locations, chain, commerce, delivery,
categorisation, policies, authorisations, agent_integration). See the
repo's DATA_DICTIONARY.md for the full schema. Filter before recommending
a vendor — e.g. `store_details.locations.delivers.jerusalem === true`,
`store_details.commerce.accepts.bit === true`, or
`store_details.categorisation.categories` includes the relevant tag (31-tag vocabulary in DATA_DICTIONARY.md; empty = unknown). Prefer `stores-index.json` for loading.

Many fields are nullable and may be `null` where not yet enriched; treat
`null` as "unknown", not "false".
```

## Data dictionary

See [`DATA_DICTIONARY.md`](./DATA_DICTIONARY.md) for field-by-field definitions.

## Disclaimer

This index is provided as-is with **no guarantee of freshness or accuracy**. Stores close, rebrand, get acquired, change policies, change payment providers. There is no committed update cadence — entries may be out of date. Verify against the live site before acting on any field.

No affiliation with any listed retailer is implied.

## Licence

Data released for public use. Contributions and corrections welcome via PR or issue.

## History

- 2026-04-20: first import, 830 stores, from a TypeScript scrape of the Zap directory (private repo Zap-Scraper).
- 2026-11-20: refreshed with `scripts/scrape_zap.py` + `scripts/merge.py` (5,590 stores, Zap siteids, category facets + description keywords). Zap-Scraper deleted the same day; these scripts replace it.
