"""Mine old.reddit search for real pain-point signal. Primary source, no auth."""
import re, html, time, json, urllib.request, urllib.parse, sys

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"

def search(sub, q, t="year"):
    url = ("https://old.reddit.com/r/%s/search?q=%s&restrict_sr=1&sort=top&t=%s"
           % (sub, urllib.parse.quote(q), t))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        h = urllib.request.urlopen(req, timeout=35).read().decode("utf-8", "replace")
    except Exception as e:
        return {"sub": sub, "q": q, "error": str(e)[:60], "hits": []}
    blocks = re.findall(r'<div class="[^"]*search-result-link.*?</div>\s*</div>\s*</div>', h, re.S)
    hits = []
    for b in blocks:
        tm = re.search(r'class="search-title[^"]*"[^>]*>(.*?)</a>', b, re.S)
        if not tm:
            continue
        title = html.unescape(re.sub("<[^>]+>", "", tm.group(1))).strip()
        sc = re.search(r'class="search-score">([\d,]+)\s*point', b)
        cm = re.search(r'class="search-comments[^"]*"[^>]*>([\d,]+)\s*comment', b)
        hits.append({
            "title": title,
            "score": int(sc.group(1).replace(",", "")) if sc else 0,
            "comments": int(cm.group(1).replace(",", "")) if cm else 0,
        })
    return {"sub": sub, "q": q, "hits": hits}

QUERIES = [
    ("SkincareAddiction", "sagging jawline"), ("SkincareAddiction", "neck wrinkles"),
    ("30PlusSkinCare", "turkey neck"), ("30PlusSkinCare", "jowls"),
    ("30PlusSkinCare", "microcurrent"), ("30PlusSkinCare", "red light therapy"),
    ("tressless", "red light therapy"), ("tressless", "thinning hair devastated"),
    ("FemaleHairLoss", "widening part"),
    ("acne", "cystic acne desperate"), ("acne", "blue light therapy"),
    ("SkincareAddiction", "dark circles"), ("SkincareAddiction", "hyperpigmentation"),
    ("Rosacea", "redness treatment"),
    ("SkincareAddiction", "melasma"),
    ("30PlusSkinCare", "eye bags"),
    ("SkincareAddiction", "keratosis pilaris"),
    ("SkincareAddiction", "LED mask worth it"),
]

out = []
for sub, q in QUERIES:
    r = search(sub, q)
    out.append(r)
    n = len(r.get("hits", []))
    top = max((x["score"] for x in r["hits"]), default=0)
    tot = sum(x["comments"] for x in r["hits"])
    print(f"r/{sub:<20} {q:<28} hits={n:<3} top_score={top:<6} total_comments={tot}")
    sys.stdout.flush()
    time.sleep(2.5)

json.dump(out, open("reddit_data.json", "w"), indent=1)
print("\nsaved reddit_data.json")
