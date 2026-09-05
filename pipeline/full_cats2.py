import json, os, sys, time
from concurrent.futures import ThreadPoolExecutor
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import items as I

idx  = json.load(open(os.path.join(BASE, "full_index.json")))
OUT  = os.path.join(BASE, "item_categories.json")
cats = json.load(open(OUT)) if os.path.exists(OUT) else {}

want = set(json.load(open(os.path.join(BASE, "cats_needed.json"))))
need = {}
for k, v in idx.items():
    if k not in cats and k in want: need.setdefault(v["host"], []).append(v["title"])
jobs = []
for host, titles in need.items():
    t = sorted(set(titles))
    for i in range(0, len(t), 45): jobs.append((host, t[i:i+45]))
print("categories to fetch: %d items in %d batches" % (sum(len(v) for v in need.values()), len(jobs)), flush=True)

def run(job):
    host, titles = job
    params = {"action":"query","prop":"categories","cllimit":"max","titles":"|".join(titles),
              "format":"json","formatversion":"2","redirects":"1"}
    pages, q = {}, {}
    for _ in range(25):
        d = None
        for a in range(4):
            d = I.api(host, params)
            if d: break
            time.sleep(5 + 5*a)
        if not d: break
        q = d.get("query", {}) or q
        for p in q.get("pages", []):
            if p.get("missing"): continue
            cur = pages.setdefault(p["title"], [])
            for c in (p.get("categories") or []):
                t = c["title"].replace("Category:", "")
                if t not in cur: cur.append(t)
        if "continue" in d: params.update(d["continue"])
        else: break
    nm = {n["from"]: n["to"] for n in q.get("normalized", [])}
    rd = {r["from"]: r["to"] for r in q.get("redirects", [])}
    res = {}
    for t in titles:
        t2 = rd.get(nm.get(t, t), nm.get(t, t)); res.setdefault(t2, []).append(t)
    out = {}
    for ttl, cs in pages.items():
        for orig in res.get(ttl, []) + [ttl]: out["%s|%s" % (host, orig)] = cs
    time.sleep(0.6)
    return out

done = 0
with ThreadPoolExecutor(max_workers=2) as ex:
    for out in ex.map(run, jobs):
        cats.update(out); done += 1
        if done % 15 == 0:
            json.dump(cats, open(OUT, "w")); print("  %d/%d  cats=%d" % (done, len(jobs), len(cats)), flush=True)
json.dump(cats, open(OUT, "w"))
have = sum(1 for k in idx if k in cats)
hm = sum(1 for k, v in cats.items() if any("Hardmode-only" in c for c in v))
print("categories for %d/%d items | Hardmode-only tagged: %d" % (have, len(idx), hm), flush=True)
