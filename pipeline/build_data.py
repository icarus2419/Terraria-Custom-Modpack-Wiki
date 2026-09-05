import json, os, re, urllib.parse
BASE = os.path.dirname(os.path.abspath(__file__))

MODS = {
  "vanilla":         {"name":"Terraria",          "short":"Vanilla", "wiki":"terraria.wiki.gg"},
  "thorium":         {"name":"Thorium Mod",       "short":"Thorium", "wiki":"thoriummod.wiki.gg"},
  "fargo":           {"name":"Fargo's Souls / Mutant", "short":"Fargo's", "wiki":"fargosmods.wiki.gg"},
  "spirit_reforged": {"name":"Spirit Reforged",   "short":"Reforged","wiki":"spiritmod.wiki.gg"},
  "spirit":          {"name":"Spirit Classic",    "short":"Spirit",  "wiki":"spiritmod.wiki.gg"},
  "fables":          {"name":"Calamity Fables",   "short":"Fables",  "wiki":"calamityfables.wiki.gg"},
}
ORDER = ["vanilla","thorium","fargo","spirit_reforged","spirit","fables"]

recipes_raw = json.load(open(os.path.join(BASE,"recipes_raw.json")))
items_raw   = json.load(open(os.path.join(BASE,"items.json")))
sprites     = json.load(open(os.path.join(BASE,"sprites.json")))

def norm(s): return re.sub(r"\s+"," ",s or "").strip()
def clean_title(t):
    t = t.split("?")[0].split("#")[0]
    return urllib.parse.unquote(t).replace("_"," ").strip()

MOD_HOST = {"vanilla":"terraria.wiki.gg","thorium":"thoriummod.wiki.gg","fargo":"fargosmods.wiki.gg",
            "spirit":"spiritmod.wiki.gg","spirit_reforged":"spiritmod.wiki.gg","fables":"calamityfables.wiki.gg"}

def key_for(src, name, url, img):
    vanilla_art = bool(img and "terraria.wiki.gg" in img)
    host = "terraria.wiki.gg" if vanilla_art else MOD_HOST[src]
    title = norm(name)
    if url:
        m = re.search(r"/wiki/(.+)$", url)
        if m:
            c = clean_title(m.group(1))
            if c and not c.startswith("Special:"): title = c
    return "%s|%s" % (host, title)

# ---- items ----
ITEMS, kmap = {}, {}
for k, v in items_raw.items():
    info = v.get("info") or {}
    iid = len(ITEMS)
    kmap[k] = iid
    lead = info.get("lead")
    if lead and len(lead) > 620: lead = lead[:617].rsplit(" ",1)[0] + "…"
    ITEMS[iid] = {
        "n": v["name"], "ti": v["title"], "h": v["host"], "u": v["url"],
        "sp": sprites.get(k),
        "van": bool(v["vanilla_art"]),
        "tt": info.get("tooltip"), "ty": info.get("types") or [],
        "tg": info.get("tags") or [],
        "r": info.get("rare"), "rn": info.get("rare_name"),
        "hm": bool(info.get("hardmode")),
        "df": info.get("defense"),
        "b": info.get("buy"), "s": info.get("sell"),
        "l": lead, "d": (info.get("drops") or [])[:10],
    }

# ---- recipes ----
RECIPES = []
for src in ORDER:
    for r in recipes_raw.get(src, []):
        rk = key_for(src, r["result"], r.get("result_url"), r.get("result_img"))
        if rk not in kmap: continue
        groups = []
        for g in r["ingredients"]:
            gi = []
            for it in g:
                ik = key_for(src, it["name"], it.get("url"), it.get("img"))
                if ik in kmap:
                    gi.append({"i": kmap[ik], "q": it.get("qty",1)})
            if gi: groups.append(gi)
        if not groups: continue
        RECIPES.append({"src": src, "res": kmap[rk], "rq": r.get("result_qty",1), "ing": groups})

# ---- indexes ----
for iid in ITEMS:
    ITEMS[iid]["mk"] = []      # made by (recipe idx)
    ITEMS[iid]["ui"] = []      # used in (recipe idx)
    ITEMS[iid]["ms"] = set()   # mods this item appears under
for ri, r in enumerate(RECIPES):
    ITEMS[r["res"]]["mk"].append(ri)
    ITEMS[r["res"]]["ms"].add(r["src"])
    seen = set()
    for g in r["ing"]:
        for e in g:
            ITEMS[e["i"]]["ms"].add(r["src"])
            if e["i"] not in seen:
                ITEMS[e["i"]]["ui"].append(ri); seen.add(e["i"])
for iid in ITEMS: ITEMS[iid]["ms"] = sorted(ITEMS[iid]["ms"], key=lambda s: ORDER.index(s))

# ---- signatures, duplicate detection, genuine overrides ----
def sig(r):
    gs = []
    for g in r["ing"]:
        gs.append(tuple(sorted((ITEMS[e["i"]]["n"], e["q"]) for e in gr_items(g))))
    return (ITEMS[r["res"]]["n"], tuple(sorted(gs)))
def gr_items(g): return g

seen_sig = {}
for ri, r in enumerate(RECIPES):
    s = sig(r)
    r["sig"] = "|".join("%s x%d" % (n, q) for grp in s[1] for n, q in grp)
    if s in seen_sig:
        r["dup"] = seen_sig[s]                 # identical recipe already listed by an earlier source
    else:
        seen_sig[s] = ri
        r["dup"] = None

# a result is "changed" when a mod defines a recipe for it that vanilla does not have
van_sigs, mod_sigs = {}, {}
for ri, r in enumerate(RECIPES):
    nm = ITEMS[r["res"]]["n"]
    (van_sigs if r["src"] == "vanilla" else mod_sigs).setdefault(nm, set()).add(sig(r))
CHANGED = {}
for nm, sigs in mod_sigs.items():
    if nm not in van_sigs: continue
    novel = sigs - van_sigs[nm]
    if novel:
        srcs = sorted({r["src"] for r in RECIPES
                       if ITEMS[r["res"]]["n"] == nm and r["src"] != "vanilla" and sig(r) in novel},
                      key=lambda s: ORDER.index(s))
        CHANGED[nm] = srcs
for ri, r in enumerate(RECIPES):
    nm = ITEMS[r["res"]]["n"]
    r["chg"] = bool(nm in CHANGED and r["src"] != "vanilla" and sig(r) not in van_sigs.get(nm, set()))
CONFLICTS = sorted(CHANGED.keys())

# ---- recipe groups ("Any X" is a group, not an item) ----
GROUPS = json.load(open(os.path.join(BASE,"recipe_groups.json")))
# Fargo's "Any Emblem": derive members from the emblem-based Avenger Emblem recipes we verified
emb = []
for r in RECIPES:
    if ITEMS[r["res"]]["n"] != "Avenger Emblem": continue
    if r["src"] not in ("vanilla", "thorium"): continue
    names = [ITEMS[e["i"]]["n"] for g in r["ing"] for e in g]
    if len(set(n for n in names if n.endswith("Emblem"))) == 1:
        for n in names:
            if n.endswith("Emblem") and n != "Avenger Emblem" and n not in emb:
                emb.append(n)
if emb: GROUPS["Any Emblem"] = emb
for iid, it in ITEMS.items():
    if it["n"] in GROUPS:
        it["grp"] = GROUPS[it["n"]]
        if it["n"] == "Any Emblem":
            it["l"] = ("A recipe group, not an item. Fargo's collapses the Avenger Emblem recipe so that "
                       "any single class emblem works in place of a specific one.")

# ---- mod ownership of an item (which mod ADDS it) ----
for iid, it in ITEMS.items():
    if it["van"]: it["own"] = "vanilla"
    else:
        host = it["h"]
        owners = [m for m in ORDER if MOD_HOST[m] == host and m != "vanilla"]
        # prefer the mod whose recipes actually reference it
        pref = [m for m in it["ms"] if m in owners]
        it["own"] = (pref or owners or ["vanilla"])[0]

for r in RECIPES: r.pop("sig", None)
data = {"mods": MODS, "order": ORDER, "items": ITEMS, "recipes": RECIPES,
        "conflicts": CONFLICTS, "changed": CHANGED}
out = os.path.join(BASE, "site_data.json")
json.dump(data, open(out,"w"), separators=(",",":"))
print("items %d | recipes %d | conflicts %d | %.0f KB" %
      (len(ITEMS), len(RECIPES), len(CONFLICTS), os.path.getsize(out)/1024))
print("per-mod recipes:", {m: sum(1 for r in RECIPES if r["src"]==m) for m in ORDER})
print("modded items:", sum(1 for i in ITEMS.values() if i["own"]!="vanilla"))
print("overridden/extended by mods:", CHANGED)
print("duplicate rows:", sum(1 for r in RECIPES if r.get("dup") is not None))
print("recipe groups attached:", {n: len(v) for n, v in GROUPS.items()})
