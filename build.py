"""Build stores.json: restructure schema + translate Hebrew descriptions.

Reads the source index, translates each Hebrew description into English,
French, and Russian (via Google Translate through deep-translator), and
emits a record per store populated with the full schema. All enrichment
fields default to null / [] and are expected to be filled over time.
"""

import json
import sys
import time
from pathlib import Path
from deep_translator import GoogleTranslator

SOURCE = Path("/home/daniel/repos/github/my-repos/israeli-store-scraper/israeli-stores.json")
OUT = Path(__file__).parent / "stores.json"
DATE_ADDED = "2026-04-20"

BOOLEAN_NULL_FIELDS = [
    "tier", "chain", "offers_same_day",
    "delivers_jerusalem", "delivers_telaviv", "delivers_eilat", "eilat_door",
    "has_mcp", "has_api",
    "prices_ex_vat", "prices_non_ils",
    "trade_only",
    "authorised_gov_supplier", "authorised_min_comms", "authorised_min_defence",
    "online_only", "has_bricks_mortar",
    "wa_support",
    "accepts_bit", "accepts_paypal", "accepts_crypto",
    "official_importer",
]
STRING_NULL_FIELDS = [
    "email", "zap_url", "instagram_url", "fb_url",
    "example_search_url", "search_syntax",
    "wa_number", "business_hours",
    "personal_desc", "my_notes_he", "my_notes_en",
    "status",
    "warranty_policy", "return_policy", "sale_tos_link", "testimonials_url",
]
NUMERIC_NULL_FIELDS = ["year_founded", "store_number_approx", "store_number_exact"]
ARRAY_FIELDS = ["delivery_options", "categories", "official_importer_brand", "brands"]


def translate_batch(texts, target, chunk=50):
    """Translate list of Hebrew strings into target lang, chunked."""
    tr = GoogleTranslator(source="iw", target=target)
    out = []
    for i in range(0, len(texts), chunk):
        batch = texts[i:i + chunk]
        # translate_batch returns list aligned with input
        for attempt in range(3):
            try:
                result = tr.translate_batch(batch)
                out.extend(result)
                break
            except Exception as e:
                print(f"  retry {attempt + 1} ({target}) chunk {i}: {e}", file=sys.stderr)
                time.sleep(2 ** attempt)
        else:
            # final fallback: empty strings so indexing stays aligned
            out.extend(["" for _ in batch])
        print(f"  {target}: {min(i + chunk, len(texts))}/{len(texts)}", file=sys.stderr)
        time.sleep(0.3)
    return out


def main():
    src = json.loads(SOURCE.read_text(encoding="utf-8"))
    descriptions = [r.get("description", "") or "" for r in src]

    print(f"Translating {len(descriptions)} descriptions...", file=sys.stderr)
    en = translate_batch(descriptions, "en")

    records = []
    for i, r in enumerate(src):
        rec = {
            "name": r.get("name", ""),
            "website": r.get("website", ""),
            "description_he": r.get("description", "") or "",
            "description_en": en[i] if i < len(en) else "",
            "date_added": DATE_ADDED,
        }
        for f in BOOLEAN_NULL_FIELDS + STRING_NULL_FIELDS + NUMERIC_NULL_FIELDS:
            rec[f] = None
        for f in ARRAY_FIELDS:
            rec[f] = []
        records.append(rec)

    OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} records → {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
