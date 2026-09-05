import json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import items as I

L = json.load(open(os.path.join(BASE, "loadouts.json")))
cache = json.load(open(os.path.join(BASE, "wikitext_cache.json")))
HOST = {"vanilla":"terraria.wiki.gg","thorium":"thoriummod.wiki.gg","spirit":"spiritmod.wiki.gg",
        "stars":"starsabovemod.wiki.gg","_carry":"terraria.wiki.gg","_tharmour":"thoriummod.wiki.gg"}

# item name -> the hosts it might live on, from the wiki that recommended it
want = {}
for st, cls in L["data"].items():
    for cl, mods in cls.items():
        for m, bs in mods.items():
            for b in bs:
                for it in b["items"]:
                    n = it["name"]
                    h = HOST.get(m, "terraria.wiki.gg")
                    want.setdefault(n, set()).add(h)
                    if it.get("url"):
                        mm = re.match(r"https://([^/]+)/wiki/(.+)$", it["url"])
                        if mm: want[n].add(mm.group(1))

have = {k.split("|",1)[1] for k in cache}
need = {}
for n, hosts in want.items():
    if n in have: continue
    for h in hosts: need.setdefault(h, []).append(n)
print("items needing stats: %d across %s" % (sum(len(v) for v in need.values()),
      {h: len(v) for h, v in need.items()}), flush=True)

jobs = []
for h, ts in need.items():
    t = sorted(set(ts))
    for i in range(0, len(t), 40): jobs.append((h, t[i:i+40]))

def run(job):
    host, titles = job
    for a in range(4):
        d = I.api(host, {"action":"query","prop":"revisions","rvprop":"content","rvslots":"main",
                         "titles":"|".join(titles),"format":"json","formatversion":"2","redirects":"1"})
        if d and "query" in d: break
        time.sleep(4 + 5*a)
    else: return {}
    q = d["query"]
    nm = {x["from"]: x["to"] for x in q.get("normalized", [])}
    rd = {x["from"]: x["to"] for x in q.get("redirects", [])}
    res = {}
    for t in titles:
        t2 = rd.get(nm.get(t, t), nm.get(t, t)); res.setdefault(t2, []).append(t)
    out = {}
    for p in q.get("pages", []):
        if p.get("missing"): continue
        c = (p.get("revisions") or [{}])[0].get("slots", {}).get("main", {}).get("content", "")
        if not c: continue
        for orig in res.get(p["title"], []) + [p["title"]]:
            out["%s|%s" % (host, orig)] = c
    time.sleep(0.4)
    return out

done = 0
with ThreadPoolExecutor(max_workers=3) as ex:
    for out in ex.map(run, jobs):
        cache.update(out); done += 1
        if done % 5 == 0:
            json.dump(cache, open(os.path.join(BASE,"wikitext_cache.json"),"w"))
            print("  %d/%d" % (done, len(jobs)), flush=True)
json.dump(cache, open(os.path.join(BASE,"wikitext_cache.json"),"w"))
have = {k.split("|",1)[1] for k in cache}
print("loadout items with wikitext: %d / %d" % (sum(1 for n in want if n in have), len(want)), flush=True)
