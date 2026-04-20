# Data dictionary — `stores.json`

Each entry in `stores.json` is one Israeli online retailer. All enrichment fields default to `null` (scalar) or `[]` (array) when unknown. **Treat `null` as "unknown", not "false".**

## Core identity

| Field | Type | Notes |
|---|---|---|
| `name` | string | Store display name (Latin script as used by the store). |
| `website` | string | Canonical store URL. |
| `date_added` | string (YYYY-MM-DD) | When the entry was first added to the index. |

## Descriptions

| Field | Type | Notes |
|---|---|---|
| `description_he` | string | Original Hebrew description (category + often city). |
| `description_en` | string | Machine-translated English (Google Translate). Not human-reviewed. |
| `personal_desc` | string \| null | Curator's own description of the store (overrides official one where set). |
| `my_notes_he` | string \| null | Curator's private notes, Hebrew. |
| `my_notes_en` | string \| null | Curator's private notes, English. |

## Contact & socials

| Field | Type | Notes |
|---|---|---|
| `email` | string \| null | Primary customer email. |
| `wa_support` | boolean \| null | Whether the store offers WhatsApp customer support. |
| `wa_number` | string \| null | WhatsApp number (E.164 preferred). |
| `instagram_url` | string \| null | |
| `fb_url` | string \| null | |
| `zap_url` | string \| null | Store page on zap.co.il (Israeli price-comparison site). |

## Commerce & payments

| Field | Type | Notes |
|---|---|---|
| `prices_ex_vat` | boolean \| null | `true` if listed prices exclude VAT (common for trade stores). |
| `prices_non_ils` | boolean \| null | `true` if prices are displayed in a currency other than ILS. |
| `accepts_bit` | boolean \| null | Accepts Bit payment app. |
| `accepts_paypal` | boolean \| null | Accepts PayPal. |
| `accepts_crypto` | boolean \| null | Accepts cryptocurrency. |
| `trade_only` | boolean \| null | B2B / trade customers only. |
| `warranty_policy` | string \| null | Summary of warranty terms (free-form). |
| `return_policy` | string \| null | Summary of return policy (free-form). |
| `sale_tos_link` | string \| null | URL to the store's terms of sale. |
| `testimonials_url` | string \| null | URL to reviews / testimonials page. |

## Brands & importer status

| Field | Type | Notes |
|---|---|---|
| `brands` | array\<string\> | Main brands stocked by the store. |
| `official_importer` | boolean \| null | Whether the store is an official importer (יבואן רשמי) for any brand. |
| `official_importer_brand` | array\<string\> | Brand(s) the store officially imports, if `official_importer` is true. |

## Delivery & logistics

| Field | Type | Notes |
|---|---|---|
| `delivery_options` | array\<string\> | Free-form tags, e.g. `courier`, `pickup`, `post`, `locker`. |
| `offers_same_day` | boolean \| null | Same-day delivery available (typically within a metro area). |
| `delivers_jerusalem` | boolean \| null | Delivers to Jerusalem. |
| `delivers_telaviv` | boolean \| null | Delivers to Tel Aviv. |
| `delivers_eilat` | boolean \| null | Delivers to Eilat. |

## Physical presence

| Field | Type | Notes |
|---|---|---|
| `online_only` | boolean \| null | No physical premises. |
| `has_bricks_mortar` | boolean \| null | Has at least one physical storefront. |
| `store_number_approx` | number \| null | Approximate number of physical stores. |
| `store_number_exact` | number \| null | Exact, verified store count. |
| `eilat_door` | boolean \| null | Has a physical presence in Eilat (relevant for VAT-exempt pickup). |
| `business_hours` | string \| null | Free-form hours description. |

## Categories & tier

| Field | Type | Notes |
|---|---|---|
| `categories` | array\<string\> | Product category tags (e.g. `electronics`, `pets`, `fashion`). |
| `tier` | boolean \| null | Flag for tier-1 / major retailer status. |
| `chain` | boolean \| null | Operates as a chain (multi-branch / national). |
| `status` | string \| null | One of `active`, `defunct`, `acquired`, `unknown`. |
| `year_founded` | number \| null | |

## Agent / integration metadata

| Field | Type | Notes |
|---|---|---|
| `example_search_url` | string \| null | Example URL pattern for running a product search on the site. |
| `search_syntax` | string \| null | Notes on the site's search URL syntax or required query params. |
| `has_mcp` | boolean \| null | Store exposes an MCP server. |
| `has_api` | boolean \| null | Store exposes a public / documented API. |

## Authorisations

| Field | Type | Notes |
|---|---|---|
| `authorised_gov_supplier` | boolean \| null | Authorised supplier to Israeli government. |
| `authorised_min_comms` | boolean \| null | Authorised supplier to Ministry of Communications. |
| `authorised_min_defence` | boolean \| null | Authorised supplier to Ministry of Defence. |
