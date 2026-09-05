"""Merge stations + items + sprites + Hardmode verdicts into one dataset."""
import json, os, re, sys, urllib.parse
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import build_items as B, hardmode as HM

MODS = {
 "vanilla":         {"name":"Terraria",              "short":"Vanilla", "wiki":"terraria.wiki.gg"},
 "thorium":         {"name":"Thorium Mod",           "short":"Thorium", "wiki":"thoriummod.wiki.gg"},
 "fargo":           {"name":"Fargo's Souls / Mutant","short":"Fargo's", "wiki":"fargosmods.wiki.gg"},
 "spirit_reforged": {"name":"Spirit Reforged",       "short":"Reforged","wiki":"spiritmod.wiki.gg"},
 "spirit":          {"name":"Spirit Classic",        "short":"Spirit",  "wiki":"spiritmod.wiki.gg"},
 "stars":           {"name":"The Stars Above",       "short":"Stars",   "wiki":"starsabovemod.wiki.gg"},
 "fables":          {"name":"Calamity Fables",       "short":"Fables",  "wiki":"calamityfables.wiki.gg"},
}
ORDER = ["vanilla","thorium","fargo","spirit_reforged","spirit","stars","fables"]

idx     = json.load(open(os.path.join(BASE,"full_index.json")))
recipes = json.load(open(os.path.join(BASE,"full_recipes.json")))
cache   = json.load(open(os.path.join(BASE,"wikitext_cache.json")))
sprites = json.load(open(os.path.join(BASE,"full_sprites.json")))
vdb     = json.load(open(os.path.join(BASE,"vanilla_itemdb.json")))
cats    = json.load(open(os.path.join(BASE,"item_categories.json")))

MOD_HOST = {m: MODS[m]["wiki"] for m in ORDER}

# ---------- items ----------
ITEMS, kmap = {}, {}
for k, v in idx.items():
    wt = cache.get(k)
    info = B.extract(v["host"], v["title"], wt, vdb) if wt else {}
    lead = info.get("lead")
    if lead and len(lead) > 300: lead = lead[:297].rsplit(" ",1)[0] + "…"
    iid = len(ITEMS); kmap[k] = iid
    ITEMS[iid] = {
        "n": v["name"], "ti": v["title"], "h": v["host"],
        "u": "https://%s/wiki/%s" % (v["host"], urllib.parse.quote(v["title"].replace(" ","_"))),
        "sp": sprites.get(k), "van": v["van"],
        "tt": info.get("tooltip"), "ty": (info.get("types") or [])[:3],
        "tg": info.get("tags") or [],
        "r": info.get("rare"), "rn": info.get("rare_name"),
        "hm": bool(info.get("hardmode")), "b": info.get("buy"), "s": info.get("sell"),
        "l": lead, "d": (info.get("drops") or [])[:8],
        "mk": [], "ui": [], "_k": k,
    }

# ---------- stations ----------
stations, sindex = [], {}
for r in recipes:
    key = (r["mod"], r["station"])
    if key not in sindex:
        sindex[key] = len(stations)
        stations.append({"mod": r["mod"], "name": r["station"], "n": 0})

RECIPES = []
for r in recipes:
    if r["res"] not in kmap: continue
    gs = []
    for g in r["ing"]:
        gi = [{"i": kmap[e["k"]], "q": e["q"]} for e in g if e["k"] in kmap]
        if gi: gs.append(gi)
    if not gs: continue
    si = sindex[(r["mod"], r["station"])]
    stations[si]["n"] += 1
    RECIPES.append({"m": r["mod"], "s": si, "res": kmap[r["res"]], "rq": r["rq"], "ing": gs})

for ri, r in enumerate(RECIPES):
    ITEMS[r["res"]]["mk"].append(ri)
    seen = set()
    for g in r["ing"]:
        for e in g:
            if e["i"] not in seen:
                ITEMS[e["i"]]["ui"].append(ri); seen.add(e["i"])
for it in ITEMS.values():
    it["uin"] = len(it["ui"]); it["ui"] = it["ui"][:40]

# ---------- ownership ----------
used_by = {}
for r in RECIPES:
    for i in [r["res"]] + [e["i"] for g in r["ing"] for e in g]:
        used_by.setdefault(i, set()).add(r["m"])
for iid, it in ITEMS.items():
    if it["van"]: it["own"] = "vanilla"
    else:
        owners = [m for m in ORDER if MOD_HOST[m] == it["h"] and m != "vanilla"]
        pref = [m for m in sorted(used_by.get(iid, []), key=lambda s: ORDER.index(s)) if m in owners]
        it["own"] = (pref or owners or ["vanilla"])[0]

# ---------- Hardmode ----------
D = {"items": {str(k): v for k, v in ITEMS.items()},
     "recipes": [{"res": r["res"], "ing": r["ing"]} for r in RECIPES]}
for k, v in D["items"].items(): v["_ikey"] = v["_k"]
title = {"%s|%s" % (v["n"], v["h"]): v["ti"] for v in D["items"].values()}
E = json.load(open(os.path.join(BASE,"full_entities.json")))
hm_ents = {k.split("|",1)[1] for k, v in E["resolved"].items()
           if any(re.search(r"hardmode.*npc", c, re.I) for c in v.get("cats_hm") or [])}
srcmap = {}
for k, v in D["items"].items():
    srcmap[v["_k"]] = E["item_sources"].get(v["_k"], [])
    v["_ikey"] = v["_k"]
verdict, why = HM.classify(D, title, cats, hm_ents, srcmap)
rs = HM.recipe_state(D, verdict)
for k, v in D["items"].items():
    v["phm"] = verdict.get(k); v["pw"] = why.get(k)
    v.pop("_k", None); v.pop("_ikey", None)
for i, (st, blk) in enumerate(rs):
    RECIPES[i]["phm"] = st; RECIPES[i]["blk"] = blk[:4]

out = {"mods": MODS, "order": ORDER, "stations": stations,
       "items": D["items"], "recipes": RECIPES}
p = os.path.join(BASE, "full_site_data.json")
json.dump(out, open(p, "w"), separators=(",", ":"))
print("items %d | recipes %d | stations %d | %.1f MB"
      % (len(ITEMS), len(RECIPES), len(stations), os.path.getsize(p)/1048576))
print("pre-HM items %d | HM items %d" % (sum(1 for v in D["items"].values() if v["phm"] is True),
                                          sum(1 for v in D["items"].values() if v["phm"] is False)))
print("pre-HM recipes %d | HM recipes %d" % (sum(1 for r in RECIPES if r["phm"] is True),
                                              sum(1 for r in RECIPES if r["phm"] is False)))
