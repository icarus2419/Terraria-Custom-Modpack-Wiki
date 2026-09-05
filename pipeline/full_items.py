import json, os, re, sys, time, urllib.parse
from concurrent.futures import ThreadPoolExecutor
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import items as I, parse as P, build_items as B

CACHE = os.path.join(BASE, "wikitext_cache.json")
plan  = json.load(open(os.path.join(BASE, "station_plan.json")))

def keep(e, st): return e["mod"] != "vanilla" or st == "Tinkerer's Workshop"
def clean_title(t):
    t = t.split("?")[0].split("#")[0]
    return urllib.parse.unquote(t).replace("_", " ").strip()

def split_tables(html, host):
    """Yield (caption, rows) per crafts table so a page carrying several stations stays separated."""
    starts = [m.start() for m in re.finditer(r"<table[^>]*>", html)]
    bounds = starts + [len(html)]
    out = []
    for i, s in enumerate(starts):
        seg = html[s:bounds[i+1]]
        cap = re.search(r"<caption[^>]*>(.*?)</caption>", seg, re.S)
        captxt = re.sub(r"<[^>]+>", " ", cap.group(1)) if cap else ""
        captxt = re.sub(r"\(Desktop[^)]*\)?", " ", captxt)
        captxt = re.sub(r"\s+", " ", captxt).strip()
        captxt = re.sub(r"\s*\bor\b\s*", " or ", captxt)
        captxt = re.sub(r"\s*\band\b\s+Obtain\b.*$", "", captxt, flags=re.I)
        captxt = re.sub(r"\s+", " ", captxt).strip(" ,;")
        pr = P.CraftsParser(host); pr.feed(seg)
        if pr.rows: out.append((captxt, pr.rows))
    return out


def build_recipes():
    out, idx = [], {}
    for e in plan:
        st = e["title"].split("/")[-1]
        if not keep(e, st): continue
        safe = re.sub(r"[^A-Za-z0-9]+", "_", "%s__%s" % (e["mod"], e["title"]))
        path = os.path.join(BASE, "stations", safe + ".json")
        # the vanilla Tinkerer's article carries the fullest table plus a separate
        # "Tinkerer's Workshop and Ecto Mist" table - keep those as distinct stations
        if e["mod"] == "vanilla" and st == "Tinkerer's Workshop":
            path = os.path.join(BASE, "wiki", "vanilla.json")
        html = json.load(open(path))["parse"]["text"]
        for cap, rows in split_tables(html, e["host"]):
            st_name = cap or st
            for res, groups in rows:
                def ident(it):
                    nm = re.sub(r"\s+", " ", it["name"] or "").strip()
                    va = bool(it.get("img") and "terraria.wiki.gg" in it["img"])
                    host = "terraria.wiki.gg" if va else e["host"]
                    title = nm
                    if it.get("url"):
                        m = re.search(r"/wiki/(.+)$", it["url"])
                        if m:
                            c = clean_title(m.group(1))
                            if c and not c.startswith("Special:"): title = c
                    k = "%s|%s" % (host, title)
                    r = idx.setdefault(k, {"name": nm, "title": title, "host": host,
                                           "img": it.get("img"), "van": va})
                    if it.get("img") and not r["img"]: r["img"] = it["img"]
                    return k
                rk = ident(res)
                gs = [[{"k": ident(i), "q": i.get("qty", 1)} for i in g] for g in groups]
                gs = [g for g in gs if g]
                if not gs: continue
                out.append({"mod": e["mod"], "station": st_name, "host": e["host"],
                            "res": rk, "rq": res.get("qty", 1), "ing": gs})
    return out, idx


if __name__ == "__main__":
    recipes, idx = build_recipes()
    json.dump(recipes, open(os.path.join(BASE, "full_recipes.json"), "w"))
    json.dump(idx,     open(os.path.join(BASE, "full_index.json"), "w"))
    print("recipes %d | items %d" % (len(recipes), len(idx)), flush=True)

    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    need = {}
    for k, v in idx.items():
        if k not in cache: need.setdefault(v["host"], []).append(v["title"])
    jobs = []
    for host, titles in need.items():
        t = sorted(set(titles))
        for i in range(0, len(t), 40): jobs.append((host, t[i:i+40]))
    print("to fetch: %d items in %d batches" % (sum(len(v) for v in need.values()), len(jobs)), flush=True)

    lock_out = {}
    def run(job):
        host, titles = job
        for attempt in range(5):
            d = I.api(host, {"action":"query","prop":"revisions","rvprop":"content","rvslots":"main",
                             "titles":"|".join(titles),"format":"json","formatversion":"2","redirects":"1"})
            if d and "query" in d: break
            time.sleep(4 + 6*attempt)
        else:
            return {}
        q = d["query"]
        nm = {n["from"]: n["to"] for n in q.get("normalized", [])}
        rd = {r["from"]: r["to"] for r in q.get("redirects", [])}
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
        time.sleep(0.5)
        return out

    done = 0
    with ThreadPoolExecutor(max_workers=3) as ex:
        for out in ex.map(run, jobs):
            cache.update(out); done += 1
            if done % 10 == 0:
                json.dump(cache, open(CACHE, "w"))
                print("  batch %d/%d  cache=%d" % (done, len(jobs), len(cache)), flush=True)
    json.dump(cache, open(CACHE, "w"))
    got = sum(1 for k in idx if k in cache)
    print("wikitext cached for %d/%d items" % (got, len(idx)), flush=True)
