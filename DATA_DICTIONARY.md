# Data dictionary — `stores.json`

Each entry is one Israeli online retailer. `name` and `website` stay at the top level for easy scanning; everything else lives under `store_details`, grouped by theme.

All enrichment fields default to `null` (scalar) or `[]` (array) when unknown. **Treat `null` as "unknown", not "false".**

## Top level

| Field | Type | Notes |
|---|---|---|
| `name` | string | Store display name (Latin script as used by the store). |
| `website` | string | Canonical store URL. |
| `store_details` | object | Container for all other fields. |

## `store_details` — identity

| Field | Type | Notes |
|---|---|---|
| `date_added` | string (YYYY-MM-DD) | When the entry was first added to the index. |
| `status` | string \| null | One of `active`, `defunct`, `acquired`, `unknown`. |
| `year_founded` | number \| null | |
| `tier` | boolean \| null | Flag for tier-1 / major retailer status. |
| `status` (Zap refresh) | string \| null | `not_on_zap_2026-11` = store was in the earlier (April 2026) index but is absent from the Zap directory as of 2026-11-20. Kept, not deleted. |

## `store_details.descriptions`

| Field | Type | Notes |
|---|---|---|
| `he` | string | Original Hebrew description (category + often city). |
| `en` | string | Machine-translated English (Google Translate). Not human-reviewed. |
| `personal` | string \| null | Curator's own description; overrides `he`/`en` where set. |
| `notes_he` | string \| null | Curator's private notes, Hebrew. |
| `notes_en` | string \| null | Curator's private notes, English. |

## `store_details.contact`

| Field | Type | Notes |
|---|---|---|
| `email` | string \| null | Primary customer email. |
| `wa_support` | boolean \| null | Offers WhatsApp customer support. |
| `wa_number` | string \| null | WhatsApp number (E.164 preferred). |
| `instagram_url` | string \| null | |
| `fb_url` | string \| null | |
| `zap_url` | string \| null | Store page on zap.co.il (`https://www.zap.co.il/clientcard.aspx?siteid=<id>`). Set for every store seen on Zap. |

## `store_details.locations`

| Field | Type | Notes |
|---|---|---|
| `branches` | array\<object\> | One entry per physical branch: `{ city_he, city_en, address }`. Empty for nationwide chains with no extractable city, or online-only stores. |
| `online_only` | boolean \| null | No physical premises. |
| `has_bricks_mortar` | boolean \| null | Has at least one physical storefront. |
| `eilat_door` | boolean \| null | Has a physical presence in Eilat (relevant for VAT-exempt pickup). |
| `business_hours` | string \| null | Free-form hours description. |
| `delivers.jerusalem` | boolean \| null | Delivers to Jerusalem. |
| `delivers.tel_aviv` | boolean \| null | Delivers to Tel Aviv. |
| `delivers.eilat` | boolean \| null | Delivers to Eilat. |

### Branch object

| Field | Type | Notes |
|---|---|---|
| `city_he` | string \| null | Branch city, Hebrew. |
| `city_en` | string \| null | Branch city, English (machine-translated). |
| `address` | string \| null | Full street address if known. |

## `store_details.chain`

| Field | Type | Notes |
|---|---|---|
| `is_chain` | boolean \| null | Operates as a chain (multi-branch / national). Auto-set to `true` when the source description marks the store as nationwide (e.g. "פריסה ארצית"). |
| `store_number_approx` | number \| null | Approximate number of physical stores. |
| `store_number_exact` | number \| null | Exact, verified store count. |

## `store_details.commerce`

| Field | Type | Notes |
|---|---|---|
| `prices_ex_vat` | boolean \| null | Listed prices exclude VAT (common for trade stores). |
| `prices_non_ils` | boolean \| null | Prices displayed in a currency other than ILS. |
| `trade_only` | boolean \| null | B2B / trade customers only. |
| `accepts.bit` | boolean \| null | Accepts Bit payment app. |
| `accepts.paypal` | boolean \| null | Accepts PayPal. |
| `accepts.crypto` | boolean \| null | Accepts cryptocurrency. |

## `store_details.delivery`

| Field | Type | Notes |
|---|---|---|
| `store_collection` | boolean \| null | Offers in-store collection / pickup. |
| `courier_delivery` | boolean \| null | Offers courier delivery. |
| `israel_post_delivery` | boolean \| null | Offers delivery via Israel Post. |
| `delivery_point_delivery` | boolean \| null | Offers delivery to pickup points / lockers. |
| `same_day_delivery` | boolean \| null | Offers guaranteed same-day delivery. |
| `next_day_delivery` | boolean \| null | Offers next-day delivery. |
| `ships_abroad` | boolean \| null | Ships internationally. |

## `store_details.categorisation`

| Field | Type | Notes |
|---|---|---|
| `categories` | array\<string\> | Product category tags from the fixed vocabulary below. Generated from Zap categories via `scripts/category_map.json`; empty when Zap has no category for the store (about 87% of stores) - empty means unknown. Hand-added tags are preserved on refresh. |
| `is_tech` | boolean \| null | `true` if any tag is in {computers, mobile, peripherals, photography, audio, pro_audio, tv_av, gaming, power_battery, smart_home}; `false` if tagged but none of those; `null` if untagged. Coarse. |
| `brands` | array\<string\> | Main brands stocked. |
| `official_importer` | boolean \| null | Whether the store is an official importer (יבואן רשמי) for any brand. |
| `official_importer_brand` | array\<string\> | Brand(s) the store officially imports, if `official_importer` is true. |

## `store_details.policies`

| Field | Type | Notes |
|---|---|---|
| `warranty` | string \| null | Summary of warranty terms (free-form). |
| `return` | string \| null | Summary of return policy (free-form). |
| `sale_tos_link` | string \| null | URL to the store's terms of sale. |
| `testimonials_url` | string \| null | URL to reviews / testimonials page. |

## `store_details.authorisations`

| Field | Type | Notes |
|---|---|---|
| `gov_supplier` | boolean \| null | Authorised supplier to Israeli government. |
| `min_comms` | boolean \| null | Authorised supplier to Ministry of Communications. |
| `min_defence` | boolean \| null | Authorised supplier to Ministry of Defence. |

## `store_details.agent_integration`

| Field | Type | Notes |
|---|---|---|
| `example_search_url` | string \| null | Example URL pattern for running a product search on the site. |
| `search_syntax` | string \| null | Notes on the site's search URL syntax or required query params. |
| `has_mcp` | boolean \| null | Store exposes an MCP server. |
| `has_api` | boolean \| null | Store exposes a public / documented API. |

## `store_details.zap` (added 2026-11-20)

Provenance from Zap (zap.co.il store directory, `modelsstore.aspx?sog=g-stores`). Present on every store seen on Zap; absent on the 6 stores with `status` = `not_on_zap_2026-11`.

| Field | Type | Notes |
|---|---|---|
| `siteid` | number | Zap store id. Primary match key on refresh. |
| `name_zap` | string | Name as shown on Zap (usually Hebrew name plus Latin name in brackets). |
| `rating` | number \| null | Zap user rating (0-5) if shown. |
| `rating_count` | number \| null | Number of ratings. |
| `categories_main_he` | array\<string\> | Zap main categories (קטגוריה ראשית, facet `db245399`, 7 values), Hebrew. |
| `categories_he` | array\<string\> | Zap sub-categories (קטגוריה, facet `db245408`, 57 values), Hebrew. |
| `last_seen` | string (YYYY-MM-DD) | Date the store was last seen on Zap. |

## Category vocabulary

`computers, mobile, peripherals, appliances, photography, audio, pro_audio, musical_instruments, tv_av, gaming, office, lighting, tactical, camping_outdoor, power_battery, smart_home, security, tools, spare_parts, accessories, home_garden, furniture, health_beauty, kids_baby, auto, pets, sport, fashion, gifts, food, books_media, other`

Zap sub-category to tags: `scripts/category_map.json`. Main categories are used only as a fallback when no sub-category maps to a tag. Not produced from Zap (assign by hand): `lighting, tactical, power_battery, smart_home, spare_parts`.

## `stores-index.json`

Slim derived file for agents (about 2 MB vs 15 MB). One object per store: `name, website, domain, zap_siteid, zap_url, categories, categories_he, is_tech, city_he, description_he, description_en, status`. Regenerated by `scripts/merge.py`; do not edit by hand.

## Notes on the 2026-11-20 refresh

- Zap lists 5,584 stores; only 705 carry any category facet. The rest are uncategorised (`categories: []`, `is_tech: null`).
- The same website can appear under several Zap siteids (branches/duplicates); each siteid is its own record.
- New stores (4,760) have `date_added` 2026-11-20. Google Translate rate-limited the 2026-11-20 run, so their `descriptions.en` and `city_en` are null (Hebrew present); re-run `scripts/merge.py` later to fill them.
