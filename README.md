# Israel-Online-Stores

Open data index of Israeli online retailers. Used as a data store backing online shopping agents.

## Files

- `stores.json` — the store index (830 entries at initial import).

## Schema

Each record has the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Store display name |
| `description` | string | Short description, typically Hebrew, often includes category + city |
| `website` | string | Store URL |
| `tier` | boolean \| null | Flag for tier-1 / major retailer status |
| `chain` | boolean \| null | Whether the retailer operates as a chain (multi-branch or national) |
| `delivery_options` | array | Delivery methods offered (e.g. `["courier", "pickup", "post"]`) |
| `offers_same_day` | boolean \| null | Whether same-day delivery is available |

Fields with `null` / `[]` are not yet populated — they will be enriched over time.

## Planned fields

- `category` — normalised product category (electronics, pets, fashion, grocery, etc.)
- `location` — city / region, parsed out of the description
- `sells` — structured tags for product types

## License

Data released as-is for public use. Contributions welcome.
