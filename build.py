"""Build stores.json with nested schema + English translations + city parsing.

Reads the source index (Hebrew descriptions), translates each to English
via Google Translate (deep-translator), parses city from the description
where possible, and emits one record per store under a partial-wrap
nested structure: `name` and `website` stay at the top level for easy
scanning; everything else lives under `store_details`.
"""

import json
import re
import sys
import time
from pathlib import Path
from deep_translator import GoogleTranslator

SOURCE = Path("/home/daniel/repos/github/my-repos/israeli-store-scraper/israeli-stores.json")
OUT = Path(__file__).parent / "stores.json"
DATE_ADDED = "2026-04-20"

NATIONWIDE_MARKERS_HE = ["פריסה ארצית", "ארצי", "כל הארץ"]
NATIONWIDE_MARKERS_EN = ["nationwide", "all over the country", "throughout the country", "countrywide"]


def translate_batch(texts, target, chunk=50):
    tr = GoogleTranslator(source="iw", target=target)
    out = []
    for i in range(0, len(texts), chunk):
        batch = texts[i:i + chunk]
        for attempt in range(3):
            try:
                out.extend(tr.translate_batch(batch))
                break
            except Exception as e:
                print(f"  retry {attempt + 1} ({target}) chunk {i}: {e}", file=sys.stderr)
                time.sleep(2 ** attempt)
        else:
            out.extend(["" for _ in batch])
        print(f"  {target}: {min(i + chunk, len(texts))}/{len(texts)}", file=sys.stderr)
        time.sleep(0.3)
    return out


def parse_last_segment(text):
    if not text:
        return None
    parts = [p.strip() for p in re.split(r"[.\n]", text) if p.strip()]
    if len(parts) < 2:
        return None
    return parts[-1]


def is_nationwide(he, en):
    he_l = (he or "")
    en_l = (en or "").lower()
    return any(m in he_l for m in NATIONWIDE_MARKERS_HE) or any(m in en_l for m in NATIONWIDE_MARKERS_EN)


def extract_branches(he, en):
    """Return (branches_list, inferred_is_chain)."""
    if is_nationwide(he, en):
        return [], True
    city_he = parse_last_segment(he)
    city_en = parse_last_segment(en)
    if not city_he and not city_en:
        return [], None
    return [{"city_he": city_he, "city_en": city_en, "address": None}], None


def build_record(name, website, desc_he, desc_en):
    branches, inferred_chain = extract_branches(desc_he, desc_en)
    return {
        "name": name,
        "website": website,
        "store_details": {
            "date_added": DATE_ADDED,
            "status": None,
            "year_founded": None,
            "tier": None,
            "descriptions": {
                "he": desc_he,
                "en": desc_en,
                "personal": None,
                "notes_he": None,
                "notes_en": None,
            },
            "contact": {
                "email": None,
                "wa_support": None,
                "wa_number": None,
                "instagram_url": None,
                "fb_url": None,
                "zap_url": None,
            },
            "locations": {
                "branches": branches,
                "online_only": None,
                "has_bricks_mortar": None,
                "eilat_door": None,
                "business_hours": None,
                "delivers": {
                    "jerusalem": None,
                    "tel_aviv": None,
                    "eilat": None,
                },
            },
            "chain": {
                "is_chain": inferred_chain,
                "store_number_approx": None,
                "store_number_exact": None,
            },
            "commerce": {
                "prices_ex_vat": None,
                "prices_non_ils": None,
                "trade_only": None,
                "accepts": {
                    "bit": None,
                    "paypal": None,
                    "crypto": None,
                },
            },
            "delivery": {
                "store_collection": None,
                "courier_delivery": None,
                "israel_post_delivery": None,
                "delivery_point_delivery": None,
                "same_day_delivery": None,
                "next_day_delivery": None,
                "ships_abroad": None,
            },
            "categorisation": {
                "categories": [],
                "brands": [],
                "official_importer": None,
                "official_importer_brand": [],
            },
            "policies": {
                "warranty": None,
                "return": None,
                "sale_tos_link": None,
                "testimonials_url": None,
            },
            "authorisations": {
                "gov_supplier": None,
                "min_comms": None,
                "min_defence": None,
            },
            "agent_integration": {
                "example_search_url": None,
                "search_syntax": None,
                "has_mcp": None,
                "has_api": None,
            },
        },
    }


def main():
    src = json.loads(SOURCE.read_text(encoding="utf-8"))
    descriptions = [r.get("description", "") or "" for r in src]

    print(f"Translating {len(descriptions)} descriptions to English...", file=sys.stderr)
    en = translate_batch(descriptions, "en")

    records = [
        build_record(
            name=r.get("name", ""),
            website=r.get("website", ""),
            desc_he=descriptions[i],
            desc_en=en[i] if i < len(en) else "",
        )
        for i, r in enumerate(src)
    ]

    OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} records → {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
