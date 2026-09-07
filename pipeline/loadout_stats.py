"""Basic combat stats per loadout item, for the hover card.

Two sources, both authoritative:
  vanilla  - Module:Iteminfo/data (the game's own item table)
  modded   - the {{item infobox}} on each item's own wiki page
"""
import json, os, re, sys
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import build_items as B

L     = json.load(open(os.path.join(BASE, "loadouts.json")))
cache = json.load(open(os.path.join(BASE, "wikitext_cache.json")))
vdb   = json.load(open(os.path.join(BASE, "vanilla_itemdb.json")))

bytitle = {}
for k in cache:
    host, t = k.split("|", 1)
    bytitle.setdefault(t, []).append(k)

DMG_TYPE = {"melee":"Melee","ranged":"Ranged","magic":"Magic","summon":"Summon",
            "radiant":"Radiant","symphonic":"Symphonic","throwing":"Throwing","thrown":"Throwing",
            "rogue":"Rogue","true melee":"Melee"}

def speed_word(use):
    try: u = float(use)
    except: return None
    for lim, w in ((8,"Insanely fast"),(20,"Very fast"),(25,"Fast"),(30,"Average"),
                   (35,"Slow"),(45,"Very slow"),(55,"Extremely slow")):
        if u < lim: return w
    return "Snail"

def from_vanilla(name):
    e = vdb.get(name)
    if not e: return None
    s = {}
    if e.get("damage") and e["damage"] > 0:
        s["damage"] = e["damage"]
        for k, lbl in (("melee","Melee"),("ranged","Ranged"),("magic","Magic"),("summon","Summon")):
            if e.get(k): s["dtype"] = lbl; break
    if e.get("defense"):    s["defense"] = e["defense"]
    if e.get("crit"):       s["crit"] = str(e["crit"]) + "%"
    if e.get("knockBack"):  s["knockback"] = e["knockBack"]
    if e.get("useTime"):
        s["use"] = e["useTime"]
        w = speed_word(e["useTime"])
        if w: s["speed"] = w
    if e.get("mana"):       s["mana"] = e["mana"]
    if e.get("accessory"):  s["kind"] = "Accessory"
    return s or None

def from_wiki(name):
    keys = bytitle.get(name)
    if not keys: return None
    best = None
    for k in keys:
        wt = cache[k]
        ib = B.I.parse_infobox(wt)
        if not ib: continue
        s = {}
        def num(v):
            v = re.sub(r"<[^>]+>", "", v or "")
            m = re.search(r"[\d.]+", v)
            return m.group(0) if m else None
        if ib.get("damage"):
            d = num(ib["damage"])
            if d: s["damage"] = d
        dt = (ib.get("damagetype") or ib.get("damage_type") or "").strip().lower()
        dt = re.sub(r"[\[\]]", "", dt)
        if dt in DMG_TYPE: s["dtype"] = DMG_TYPE[dt]
        if ib.get("defense"):
            d = num(ib["defense"])
            if d: s["defense"] = d
        for src, dst in (("knockback","knockback"),("critical","crit"),("mana","mana"),
                         ("velocity","velocity")):
            if ib.get(src):
                v = num(ib[src])
                if v: s[dst] = v
        if ib.get("use") or ib.get("usetime"):
            u = num(ib.get("use") or ib.get("usetime"))
            if u:
                s["use"] = u
                w = speed_word(u)
                if w: s["speed"] = w
        if ib.get("setbonus"):
            s["setbonus"] = re.sub(r"\s+", " ", B.unwrap_templates(B.preclean(ib["setbonus"]))).strip()[:400]
        ty = [ib.get(x) for x in ("type","type2","type3") if ib.get(x)]
        if ty: s["kind"] = " · ".join(t.strip() for t in ty[:2])
        if ib.get("tooltip"):
            tt = re.sub(r"\s+", " ", B.unwrap_templates(B.preclean(ib["tooltip"]))).strip()
            if tt: s["tip"] = tt[:320]
        # vanilla pages carry no tooltip field, so an accessory would otherwise show
        # nothing useful - fall back to the first sentence of the article
        if "tip" not in s:
            lead = B.lead(wt) or ""
            m = re.split(r"(?<=\.)\s", lead)
            if m and len(m[0]) > 24:
                sent = m[0]
                if len(sent) < 70 and len(m) > 1: sent = sent + " " + m[1]
                s["tip"] = re.sub(r"\s+", " ", sent).strip()[:320]
        if s and (best is None or len(s) > len(best)): best = s
    return best

if __name__ == "__main__":
    names = set()
    for st, cls in L["data"].items():
        for cl, mods in cls.items():
            for m, bs in mods.items():
                for b in bs:
                    for it in b["items"]: names.add(it["name"])
    out, hit = {}, 0
    for n in sorted(names):
        s = from_wiki(n) or {}
        v = from_vanilla(n) or {}
        for k, val in v.items(): s.setdefault(k, val)
        if s: out[n] = s; hit += 1
    json.dump(out, open(os.path.join(BASE, "loadout_stats.json"), "w"))
    have = lambda k: sum(1 for s in out.values() if k in s)
    print("items with any stats: %d / %d" % (hit, len(names)))
    print("  damage %d | dtype %d | speed %d | defense %d | setbonus %d | tooltip %d"
          % (have("damage"), have("dtype"), have("speed"), have("defense"),
             have("setbonus"), have("tip")))
