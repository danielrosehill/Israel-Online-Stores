#!/usr/bin/env python3
"""Merge .cache/zap_stores.json into stores.json and emit stores-index.json.

Usage: uv run --with deep-translator scripts/merge.py   (python3 works too; translation is skipped if deep-translator is missing)
Rules: match existing records by Zap siteid, else normalised website domain (unclaimed, unique), else name.
Existing hand-filled fields are never overwritten (only nulls are filled). Stores absent from Zap keep
their record with store_details.status = "not_on_zap_2026-11".
"""
import json, re, sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TODAY = "2026-11-20"
GONE = "not_on_zap_2026-11"
CMAP = json.load(open(ROOT / "scripts/category_map.json"))
SRC = json.load(open(ROOT / ".cache/zap_stores.json"))
stores = json.load(open(ROOT / "stores.json"))

try:
    from deep_translator import GoogleTranslator
except Exception:
    GoogleTranslator = None


def domain(url):
    if not url:
        return None
    u = re.sub(r"^https?://", "", url.strip().lower()).split("/")[0].split("?")[0]
    u = re.sub(r"^www\d*\.", "", u)
    return u or None


def norm(s):
    return re.sub(r"[^\w]+", "", (s or "").lower())


def name_variants(n):
    n = n or ""
    out = {norm(n)}
    m = re.match(r"^(.*?)\s*\((.*)\)\s*$", n)
    if m:
        out |= {norm(m.group(1)), norm(m.group(2))}
    return {x for x in out if x}


def blank_record(name, website, he, en, city_he, city_en):
    return {"name": name, "website": website, "store_details": {
        "date_added": TODAY, "status": None, "year_founded": None, "tier": None,
        "descriptions": {"he": he, "en": en, "personal": None, "notes_he": None, "notes_en": None},
        "contact": {"email": None, "wa_support": None, "wa_number": None, "instagram_url": None, "fb_url": None, "zap_url": None},
        "locations": {"branches": [{"city_he": city_he, "city_en": city_en, "address": None}] if city_he else [],
                      "online_only": None, "has_bricks_mortar": None, "eilat_door": None, "business_hours": None,
                      "delivers": {"jerusalem": None, "tel_aviv": None, "eilat": None}},
        "chain": {"is_chain": None, "store_number_approx": None, "store_number_exact": None},
        "commerce": {"prices_ex_vat": None, "prices_non_ils": None, "trade_only": None,
                     "accepts": {"bit": None, "paypal": None, "crypto": None}},
        "delivery": {k: None for k in ["store_collection", "courier_delivery", "israel_post_delivery", "delivery_point_delivery",
                                       "same_day_delivery", "next_day_delivery", "ships_abroad"]},
        "categorisation": {"categories": [], "brands": [], "official_importer": None, "official_importer_brand": []},
        "policies": {"warranty": None, "return": None, "sale_tos_link": None, "testimonials_url": None},
        "authorisations": {"gov_supplier": None, "min_comms": None, "min_defence": None},
        "agent_integration": {"example_search_url": None, "search_syntax": None, "has_mcp": None, "has_api": None}}}


def last_segment(text):
    parts = [p.strip() for p in re.split(r"[.\n]", text or "") if p.strip()]
    return parts[-1] if len(parts) >= 2 else None


def map_categories(main_he, sub_he):
    tags = []
    for c in sub_he:
        tags += CMAP["sub"].get(c, [])
    if not tags:
        for c in main_he:
            tags += CMAP["main"].get(c, [])
    if not tags and sub_he:
        tags = ["other"] if "שונות" in sub_he else []
    seen = []
    for t in tags:
        if t not in seen:
            seen.append(t)
    return seen


def description_tags(text):
    """Fallback tags from Hebrew keywords in the Zap description (category_map.json description_keywords)."""
    tags = []
    for k, v in CMAP.get("description_keywords", {}).items():
        if not k.startswith("_") and k in (text or ""):
            tags += v
    return list(dict.fromkeys(tags))


def is_tech(tags):
    if not tags:
        return None
    return any(t in CMAP["tech_tags"] for t in tags)


# ---- match ----
by_sid, by_dom, by_name = {}, {}, {}
for s in stores:
    z = (s["store_details"].get("zap") or {})
    if z.get("siteid"):
        by_sid[z["siteid"]] = s
    by_dom.setdefault(domain(s.get("website")), []).append(s)
    for v in name_variants(s["name"]):
        by_name.setdefault(v, []).append(s)
by_dom.pop(None, None)

claimed = {id(s) for s in by_sid.values()}
matched, new_src = {}, []
how = {"siteid": 0, "domain": 0, "name": 0}
for z in SRC["stores"]:
    s = by_sid.get(z["siteid"])
    if s:
        how["siteid"] += 1
    else:
        c = [x for x in by_dom.get(domain(z["website"]), []) if id(x) not in claimed]
        if len(c) == 1:
            s, k = c[0], "domain"
        else:
            c = [x for x in {id(y): y for v in name_variants(z["name_zap"]) for y in by_name.get(v, [])}.values() if id(x) not in claimed]
            s, k = (c[0], "name") if len(c) == 1 else (None, None)
        if s:
            how[k] += 1
            claimed.add(id(s))
    if s:
        matched[z["siteid"]] = s
    else:
        new_src.append(z)

# ---- create new records ----
for z in new_src:
    m = re.match(r"^(.*?)\s*\((.*)\)\s*$", z["name_zap"])
    name = m.group(2).strip() if m and re.search(r"[A-Za-z]", m.group(2)) else z["name_zap"]
    he = z["description_he"]
    rec = blank_record(name, z["website"], he, None, last_segment(he), None)
    stores.append(rec)
    matched[z["siteid"]] = rec

# ---- translate: every record added today with he set and en null (re-run to retry after a rate limit) ----
def translate_pending():
    import time
    pend = [s for s in stores if s["store_details"]["date_added"] == TODAY and s["store_details"]["descriptions"]["he"]
            and not s["store_details"]["descriptions"]["en"]]
    if not pend or not GoogleTranslator:
        print(f"translation skipped: {len(pend)} pending, deep-translator {'missing' if not GoogleTranslator else 'ok'}")
        return
    tr = GoogleTranslator(source="iw", target="en")
    texts = sorted({s["store_details"]["descriptions"]["he"] for s in pend})
    en_map, fails = {}, 0
    for i in range(0, len(texts), 50):
        chunk = texts[i:i + 50]
        try:
            for t, e in zip(chunk, tr.translate_batch(chunk)):
                en_map[t] = e
            fails = 0
        except Exception as e:
            fails += 1
            print("translate failed:", str(e)[:80], file=sys.stderr)
            if fails >= 2:  # rate-limited: stop early, leave en null, retry later
                break
            time.sleep(5)
        time.sleep(0.3)
    for s in pend:
        d = s["store_details"]
        en = en_map.get(d["descriptions"]["he"])
        if en:
            d["descriptions"]["en"] = en
            if d["locations"]["branches"]:
                d["locations"]["branches"][0]["city_en"] = last_segment(en)
    print(f"translated {len(en_map)}/{len(texts)} descriptions")


# English translation dropped 2026-11-20: not worth maintaining (Google Translate rate-limits; agents read Hebrew).
# translate_pending() is kept for manual use only.

# ---- apply Zap data ----
zap_by_sid = {z["siteid"]: z for z in SRC["stores"]}
for sid, s in matched.items():
    z = zap_by_sid[sid]
    d = s["store_details"]
    d["contact"]["zap_url"] = f"https://www.zap.co.il/clientcard.aspx?siteid={sid}"
    main_he, sub_he = z["categories_main_he"], z["categories_he"]
    d["zap"] = {"siteid": sid, "name_zap": z["name_zap"], "rating": z["rating"], "rating_count": z["rating_count"],
                "categories_main_he": main_he, "categories_he": sub_he, "last_seen": TODAY}
    if d.get("status") == GONE:
        d["status"] = None
    if not s.get("website") and z["website"]:
        s["website"] = z["website"]
    if not d["descriptions"].get("he") and z["description_he"]:
        d["descriptions"]["he"] = z["description_he"]
    tags = map_categories(main_he, sub_he)
    cat = d["categorisation"]
    if cat.get("categories_source") == "default_other":
        cat["categories"] = []          # re-derive: a placeholder "other" must not block real tags
    cat["categories_source"] = "zap_facet" if tags else None
    if not tags:
        tags = description_tags(d["descriptions"].get("he") or z["description_he"])
        cat["categories_source"] = "description_keywords" if tags else None
    # categories are generated from Zap; keep any tag already present (hand-filled) and add mapped ones
    cat["categories"] = list(dict.fromkeys((cat.get("categories") or []) + tags))
    if not cat["categories"]:
        cat["categories"] = ["other"]   # uncategorised (city-only or vague description), by decision 2026-11-20
        cat["categories_source"] = "default_other"
    cat["is_tech"] = is_tech(cat["categories"])

matched_ids = {id(s) for s in matched.values()}
dropped = 0
for s in stores:
    d = s["store_details"]
    if id(s) not in matched_ids:
        dropped += 1
        d["status"] = GONE
        d.setdefault("categorisation", {}).setdefault("is_tech", None)
    else:
        d.setdefault("categorisation", {}).setdefault("is_tech", None)

stores.sort(key=lambda s: s["name"].lower())
json.dump(stores, open(ROOT / "stores.json", "w"), ensure_ascii=False, indent=2)
open(ROOT / "stores.json", "a").write("\n")

index = []
for s in stores:
    d = s["store_details"]
    z = d.get("zap") or {}
    br = d["locations"]["branches"]
    index.append({"name": s["name"], "website": s.get("website"), "domain": domain(s.get("website")),
                  "zap_siteid": z.get("siteid"), "zap_url": d["contact"].get("zap_url"),
                  "categories": d["categorisation"]["categories"], "categories_he": z.get("categories_he", []),
                  "is_tech": d["categorisation"].get("is_tech"), "city_he": br[0]["city_he"] if br else None,
                  "description_he": d["descriptions"].get("he"), "description_en": d["descriptions"].get("en"),
                  "status": d.get("status")})
json.dump(index, open(ROOT / "stores-index.json", "w"), ensure_ascii=False, separators=(",", ":"))
withcat = sum(1 for s in stores if s["store_details"]["categorisation"]["categories"])
print(json.dumps({"total": len(stores), "matched": how, "new": len(new_src), "not_on_zap": dropped,
                  "with_category": withcat, "pct": round(100 * withcat / len(stores), 1)}))
