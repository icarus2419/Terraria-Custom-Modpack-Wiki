"""Caches each wiki's own boss list, and the categories that name a boss page.

Nothing here decides what a boss is or what order they come in -- that is read off the
wikis' own Bosses pages in bosses.py. This script only fetches and caches.
"""
import json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import items as I
BASE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(BASE, "bosses_raw"); os.makedirs(OUT, exist_ok=True)

WIKIS = {"vanilla":"terraria.wiki.gg", "thorium":"thoriummod.wiki.gg",
         "fargo":"fargosmods.wiki.gg", "spirit":"spiritmod.wiki.gg",
         "fables":"calamityfables.wiki.gg", "stars":"starsabovemod.wiki.gg"}

# candidate list pages, tried in order until one has content
PAGES = ["Bosses", "Boss", "Guide:Bosses", "Bosses/Progression", "Boss progression"]
CATS  = ["Category:Boss NPCs", "Category:Bosses", "Category:Boss", "Category:Boss summon items"]

def cache(name, fn):
    p = os.path.join(OUT, name + ".json")
    if os.path.exists(p):
        return json.load(open(p, encoding="utf-8"))
    v = fn()
    json.dump(v, open(p, "w", encoding="utf-8"))
    return v

def wikitext(host, title):
    d = I.api(host, {"action":"query","prop":"revisions","rvprop":"content","rvslots":"main",
                     "titles":title,"format":"json","formatversion":"2"})
    try:
        pg = d["query"]["pages"][0]
        if pg.get("missing"): return None
        return pg["revisions"][0]["slots"]["main"]["content"]
    except Exception:
        return None

def catmembers(host, cat):
    d = I.api(host, {"action":"query","list":"categorymembers","cmtitle":cat,"cmlimit":"500",
                     "cmnamespace":"0","format":"json","formatversion":"2"})
    return [m["title"] for m in (d or {}).get("query",{}).get("categorymembers",[])]

if __name__ == "__main__":
    for mod, host in WIKIS.items():
        got = cache("pages_" + mod, lambda: {t: wikitext(host, t) for t in PAGES})
        cats = cache("cats_" + mod, lambda: {c: catmembers(host, c) for c in CATS})
        print("%-8s %s" % (mod, host))
        for t, wt in got.items():
            if wt: print("    page  %-22s %6d chars" % (t, len(wt)))
        for c, ms in cats.items():
            if ms: print("    cat   %-22s %3d members" % (c, len(ms)))

# ---------------------------------------------------------------- per-boss detail
def batched_wikitext(host, titles, size=18):
    out = {}
    for i in range(0, len(titles), size):
        chunk = titles[i:i+size]
        d = I.api(host, {"action":"query","prop":"revisions","rvprop":"content","rvslots":"main",
                         "titles":"|".join(chunk),"format":"json","formatversion":"2"})
        for pg in (d or {}).get("query",{}).get("pages",[]):
            if pg.get("missing"): out[pg["title"]] = None; continue
            try: out[pg["title"]] = pg["revisions"][0]["slots"]["main"]["content"]
            except Exception: out[pg["title"]] = None
        print("    %s %d/%d" % (host, min(i+size, len(titles)), len(titles)), flush=True)
    return out

def batched_imageinfo(host, files, size=18):
    out = {}
    for i in range(0, len(files), size):
        chunk = ["File:" + f for f in files[i:i+size]]
        d = I.api(host, {"action":"query","prop":"imageinfo","iiprop":"url",
                         "titles":"|".join(chunk),"format":"json","formatversion":"2"})
        for pg in (d or {}).get("query",{}).get("pages",[]):
            ii = pg.get("imageinfo")
            out[pg["title"][5:]] = ii[0]["url"] if ii else None
        print("    %s images %d/%d" % (host, min(i+size, len(files)), len(files)), flush=True)
    return out
