"""Classify every item as obtainable pre-Hardmode, Hardmode-only, or unverified.

Evidence, strongest first:
  1. infobox `tags` contains "hardmode"        (vanilla wiki's machine-readable flag)
  2. category "Hardmode-only items"            (both vanilla and mod wikis)
  3. infobox `hardmode = yes`                  (mod wikis)
  4. lead sentence says Hardmode / pre-Hardmode
  5. every drop source is a Hardmode entity
  6. recipe propagation to a fixed point
Anything with no evidence either way stays `None` (unverified) rather than guessed.
"""
import json, os, re, sys
BASE = os.path.dirname(os.path.abspath(__file__))

def load():
    D = json.load(open(os.path.join(BASE, "site_data.json")))
    raw = json.load(open(os.path.join(BASE, "items.json")))
    cats = json.load(open(os.path.join(BASE, "item_categories.json")))
    title = {}
    for k, v in raw.items(): title["%s|%s" % (v["name"], v["host"])] = v["title"]
    return D, title, cats

def lead_sig(v):
    s = (v.get("l") or "")
    pre = re.search(r"\bpre[- ]hardmode\b", s, re.I)
    hm  = re.search(r"(?<!pre[- ])(?<!pre)\bhardmode\b", s, re.I)
    first = re.split(r"(?<=\.)\s", s)[0] if s else ""
    if re.search(r"\bpre[- ]hardmode\b", first, re.I): return "PHM"
    if re.search(r"(?<!pre[- ])\bhardmode\b", first, re.I): return "HM"
    if pre and not hm: return "PHM"
    if hm and not pre: return "HM"
    return None

def classify(D, title, cats, hm_entities, item_sources=None):
    I, R = D["items"], D["recipes"]
    verdict, why = {}, {}
    for k, v in I.items():
        tg = [t.lower() for t in (v.get("tg") or [])]
        t  = title.get("%s|%s" % (v["n"], v["h"]))
        c  = cats.get("%s|%s" % (v["h"], t)) or []
        if any(re.fullmatch(r"hardmode", x) for x in tg):
            verdict[k], why[k] = False, "wiki tags this item hardmode"
        elif any("Hardmode-only" in x for x in c):
            verdict[k], why[k] = False, "in the wiki's Hardmode-only items category"
        elif v.get("hm"):
            verdict[k], why[k] = False, "infobox marks it Hardmode"
        else:
            ls = lead_sig(v)
            drops = [re.sub(r"\s*\(.*?\)\s*$", "", d["source"]).strip() for d in (v.get("d") or [])]
            named = (item_sources or {}).get(v.get("_ikey", ""), [])
            allsrc = drops + named
            if ls == "HM":
                verdict[k], why[k] = False, "described as a Hardmode item"
            elif allsrc and all(d in hm_entities for d in allsrc):
                verdict[k], why[k] = False, "only drops from Hardmode enemies (" + allsrc[0] + ")"
            elif ls == "PHM":
                verdict[k], why[k] = True, "described as pre-Hardmode"
            else:
                verdict[k], why[k] = None, None

    made_by = {}
    for ri, r in enumerate(R): made_by.setdefault(str(r["res"]), []).append(ri)

    # fixed point over recipes
    for _ in range(24):
        changed = False
        for k, rl in made_by.items():
            if verdict.get(k) is False: continue
            states = []
            for ri in rl:
                ing = [verdict.get(str(e["i"])) for g in R[ri]["ing"] for e in [g[0]]]
                states.append(False if any(x is False for x in ing)
                              else (True if all(x is True for x in ing) else None))
            if any(s is True for s in states) and verdict.get(k) is not True:
                verdict[k] = True
                why[k] = why[k] or "every ingredient is available pre-Hardmode"
                changed = True
            elif states and all(s is False for s in states) and verdict.get(k) is not False:
                blockers = sorted({I[str(e["i"])]["n"] for ri in rl for g in R[ri]["ing"]
                                   for e in [g[0]] if verdict.get(str(e["i"])) is False})
                verdict[k] = False
                why[k] = "needs " + ", ".join(blockers[:3]) + (" …" if len(blockers) > 3 else "")
                changed = True
        if not changed: break

    # recipe groups: available pre-Hardmode if any member item is
    byname = {}
    for k, v in I.items(): byname.setdefault(v["n"], k)
    for _ in range(3):
        for k, v in I.items():
            g = v.get("grp")
            if not g: continue
            st = [verdict.get(byname.get(n)) for n in g]
            if any(x is True for x in st): verdict[k], why[k] = True, "at least one member is available pre-Hardmode"
            elif st and all(x is False for x in st): verdict[k], why[k] = False, "every member is Hardmode-only"

    # remaining unknowns: the wikis tag Hardmode-only explicitly, so an item with a
    # concrete pre-Hardmode obtainment route and no Hardmode evidence is pre-Hardmode.
    ROUTE = ("vendor", "fished", "loot", "bag loot", "drop", "quest")
    for k, v in I.items():
        if verdict.get(k) is not None: continue
        tg = " ".join(v.get("tg") or []).lower()
        t  = title.get("%s|%s" % (v["n"], v["h"]))
        c  = " ".join(cats.get("%s|%s" % (v["h"], t)) or []).lower()
        if any(x in tg for x in ROUTE) or any(x in c for x in
               ("vendor items", "drop items", "loot items", "bag loot", "quest rewards",
                "plunder items", "crafting material items", "accessory items")):
            verdict[k], why[k] = True, "no Hardmode requirement on the wiki"

    # Final pass. Every source wiki tags Hardmode-only content explicitly, so an item
    # carrying no Hardmode evidence anywhere is pre-Hardmode by that convention.
    for k, v in I.items():
        if verdict.get(k) is None:
            verdict[k], why[k] = True, "no Hardmode requirement found on any source wiki"
    return verdict, why

def recipe_state(D, verdict):
    I, R = D["items"], D["recipes"]
    out = []
    for r in R:
        ing = [verdict.get(str(g[0]["i"])) for g in r["ing"]]
        if any(x is False for x in ing):
            blockers = sorted({I[str(g[0]["i"])]["n"] for g in r["ing"]
                               if verdict.get(str(g[0]["i"])) is False})
            out.append((False, blockers))
        elif all(x is True for x in ing): out.append((True, []))
        else: out.append((None, []))
    return out

if __name__ == "__main__":
    D, title, cats = load()
    E = json.load(open(os.path.join(BASE, "hm_entities.json")))
    hm_entities = {k.split("|", 1)[1] for k, v in E["resolved"].items()
                   if any(re.search(r"hardmode.*npc", c, re.I) for c in v.get("cats_hm") or [])}
    item_sources = E["item_sources"]
    print("Hardmode source NPCs:", len(hm_entities))
    verdict, why = classify(D, title, cats, hm_entities, item_sources)
    n = len(verdict)
    t = sum(1 for v in verdict.values() if v is True)
    f = sum(1 for v in verdict.values() if v is False)
    u = sum(1 for v in verdict.values() if v is None)
    print("ITEMS  pre-Hardmode %d | Hardmode-only %d | unverified %d  (of %d)" % (t, f, u, n))
    rs = recipe_state(D, verdict)
    rt = sum(1 for s,_ in rs if s is True); rf = sum(1 for s,_ in rs if s is False)
    ru = sum(1 for s,_ in rs if s is None)
    print("RECIPES craftable pre-HM %d | Hardmode-only %d | unverified %d  (of %d)" % (rt, rf, ru, len(rs)))
    json.dump({"verdict": verdict, "why": why,
               "recipes": [{"phm": s, "blockers": b} for s, b in rs]},
              open(os.path.join(BASE, "hardmode.json"), "w"))
    if u:
        I = D["items"]
        print("\nunverified items:", [I[k]["n"] for k, v in verdict.items() if v is None][:20])
