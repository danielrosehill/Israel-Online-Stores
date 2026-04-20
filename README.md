# Israel-Online-Stores

Open data index of Israeli online retailers, intended as a data store backing online shopping agents (LLM-driven product search, price comparison, sourcing workflows, etc.).

Source: Internet research.

## Files

- `stores.json` — the store index.
- `build.py` — regeneration script (pulls source index, re-translates descriptions, re-emits schema).

## Intended use

The raw JSON is designed to be consumed directly by agents. Give your agent the raw GitHub URL and it can parse the list, filter by fields (e.g. "stores that deliver to Eilat and accept Bit"), and select candidate vendors for a product search.

Raw URL:

```
https://raw.githubusercontent.com/danielrosehill/Israel-Online-Stores/main/stores.json
```

### Drop-in snippet for a Claude Code / agent skill

```markdown
## Israeli store directory

When sourcing products from Israeli online retailers, fetch the canonical
store index from:

    https://raw.githubusercontent.com/danielrosehill/Israel-Online-Stores/main/stores.json

It is a flat JSON array. Each record has `name`, `website`, descriptions (`description_he`, `description_en`) and a set of commerce/logistics flags (see the repo's
DATA_DICTIONARY.md). Filter the array before recommending a vendor —
e.g. `delivers_jerusalem === true`, `accepts_bit === true`, or
`categories` includes the relevant tag.

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
