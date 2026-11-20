#!/usr/bin/env python3
"""Crawl Zap's store directory (stdlib only).

Usage:
  python3 scripts/scrape_zap.py                # full crawl
  python3 scripts/scrape_zap.py --test         # 2 directory pages + 1 facet
Output: .cache/zap_stores.json  (stores + facet membership), .cache/html/* (resumable page cache).

Source: https://www.zap.co.il/modelsstore.aspx?sog=g-stores[&pageinfo=N][&db245399=<id>|&db245408=<id>]
Facet lists: main categories (db245399) are fully listed in the page HTML; sub-categories
(db245408) are behind the "more..." popup, fetched from GET /models/getmorefilters?dbid=245408&sogname=g-stores.
Plain GET with a desktop UA and Accept-Language he-IL; needs an Israeli IP. No browser.
"""
import hashlib, html, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"
HTMLC = CACHE / "html"
BASE = "https://www.zap.co.il"
LIST = BASE + "/modelsstore.aspx?sog=g-stores"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
DELAY = 1.0
MAX_PAGES = 600
stats = {"requests": 0, "cached": 0}
_last = [0.0]


def get(url, tag=None):
    HTMLC.mkdir(parents=True, exist_ok=True)
    f = HTMLC / (hashlib.md5(url.encode()).hexdigest() + ".html")
    if f.exists() and f.stat().st_size > 1000:
        stats["cached"] += 1
        return f.read_text(encoding="utf-8")
    for attempt in range(5):
        wait = DELAY - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        stats["requests"] += 1
        try:
            hdr = {"User-Agent": UA, "Accept-Language": "he-IL", "Accept": "*/*"}
            if "/models/" in url:
                hdr["X-Requested-With"] = "XMLHttpRequest"
            req = urllib.request.Request(url, headers=hdr)
            body = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
            if len(body) < 5000 and "Request Rejected" in body:
                raise RuntimeError("Request Rejected")
            f.write_text(body, encoding="utf-8")
            return body
        except Exception as e:
            back = 2 ** (attempt + 1)
            print(f"  retry {attempt+1} {url} ({e}); sleep {back}s", file=sys.stderr)
            time.sleep(back)
    raise SystemExit(f"giving up on {url}")


ROW = re.compile(r'<div class="compare-item-row product-item" data-site-id="(\d+)">(.*?)(?=<div class="compare-item-row product-item"|<!--\s*end|\Z)', re.S)


def parse_rows(page):
    out = []
    for sid, blk in ROW.findall(page):
        def one(rx):
            m = re.search(rx, blk, re.S)
            return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).replace("‎", "").replace("‏", "").strip() if m else None
        name = one(r'itemprop="name">(.*?)</span>')
        desc = one(r'class="store-guide-desc">(.*?)</span>')
        site = one(r'itemprop="url"[^>]*>(.*?)</a>')
        rate = one(r'<span class="rate">(.*?)</span>')
        cnt = one(r'itemprop="ratingCount" content="(\d+)"') or (re.search(r'ratingCount" content="(\d+)"', blk) or [None, None])[1]
        addr = one(r'itemprop="streetAddress">(.*?)</span>')
        out.append({"siteid": int(sid), "name_zap": re.sub(r"\s+", " ", name or ""), "description_he": desc,
                    "website": site, "rating": float(rate) if rate and re.match(r"^[\d.]+$", rate) else None,
                    "rating_count": int(cnt) if cnt else None, "address_he": addr})
    return out


def crawl(qs, label, max_pages=MAX_PAGES):
    seen = {}
    for n in range(1, max_pages + 1):
        url = LIST + qs + ("" if n == 1 else f"&pageinfo={n}")
        rows = parse_rows(get(url))
        new = [r for r in rows if r["siteid"] not in seen]
        for r in new:
            seen[r["siteid"]] = r
        print(f"{label} page {n}: {len(rows)} rows, {len(new)} new, total {len(seen)}", flush=True)
        if not new:
            break
    return seen


def facets(dbid, page1):
    """Return {id: (name_he, count)} for a facet, via the getmorefilters popup (falls back to page HTML)."""
    q = urllib.parse.urlencode({"dbid": dbid, "keyword": "", "sogname": "g-stores", "link": urllib.parse.quote(LIST, safe="").lower()})
    body = get(f"{BASE}/models/getmorefilters?{q}")
    found = re.findall(r"<div id=\"(\d+)\" data-count=\"(\d+)\"\s+aria-label='([^']*)'", body)
    res = {i: (html.unescape(n), int(c)) for i, c, n in found}
    if not res:  # fallback: visible rows on the directory page
        for i, n, c in re.findall(rf"<a id=\"(\d+)\"\s+aria-label='([^']*)' class='filter-row' href=\"[^\"]*db{dbid}=\d+\"[^>]*>\s*<div[^>]*>[^<]*</div><span class='filterCount'>\((\d+)\)", page1):
            res[i] = (html.unescape(n), int(c))
    return res


def main():
    test = "--test" in sys.argv
    t0 = time.time()
    CACHE.mkdir(exist_ok=True)
    page1 = get(LIST)
    main_f = facets("245399", page1)
    sub_f = facets("245408", page1)
    print(f"facets: {len(main_f)} main, {len(sub_f)} sub")
    stores = crawl("", "directory", 2 if test else MAX_PAGES)
    membership = {}  # siteid -> {"main": [names], "sub": [names]}
    for level, dbn, fac in (("main", "db245399", main_f), ("sub", "db245408", sub_f)):
        items = list(fac.items())[:1] if test else fac.items()
        for fid, (fname, fcount) in items:
            got = crawl(f"&{dbn}={fid}", f"{level}:{fname}")
            if len(got) != fcount:
                print(f"  note: {fname} listed {fcount}, crawled {len(got)}")
            for sid, r in got.items():
                stores.setdefault(sid, r)  # store seen only under a facet
                membership.setdefault(sid, {"main": [], "sub": []})[level].append(fname)
    out = {"scraped": time.strftime("%Y-%m-%d"), "facets_main": {i: {"name_he": n, "count": c} for i, (n, c) in main_f.items()},
           "facets_sub": {i: {"name_he": n, "count": c} for i, (n, c) in sub_f.items()},
           "stores": [dict(r, categories_main_he=membership.get(s, {}).get("main", []), categories_he=membership.get(s, {}).get("sub", []))
                      for s, r in sorted(stores.items())],
           "requests": stats["requests"], "cache_hits": stats["cached"], "seconds": round(time.time() - t0)}
    (CACHE / ("zap_stores_test.json" if test else "zap_stores.json")).write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"done: {len(out['stores'])} stores, {stats['requests']} requests, {out['seconds']}s")


if __name__ == "__main__":
    main()
