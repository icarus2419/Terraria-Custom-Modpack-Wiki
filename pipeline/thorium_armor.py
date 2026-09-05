"""Thorium's own Armor page, parsed into sets by class and era.

The class-setup guide leaves armour off many cards (Melee has no armour entry at
Pre-Eater / Brain at all), so this fills those gaps from the mod's own armour
reference rather than leaving the reader thinking Thorium has no armour.
"""
import json, os, re, sys
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import items as I

SRC = os.path.join(BASE, "guides", "thorium_armor.json")

CLASS_PAT = [
    ("Melee",    r"melee"),
    ("Ranged",   r"\branged\b|ranged damage"),
    ("Magic",    r"\bmagic\b|mana"),
    ("Summoner", r"summon|minion"),
    ("Thrower",  r"throw"),
    ("Healer",   r"radiant|healing"),
    ("Bard",     r"symphonic|inspiration"),
]

def classes_for(text):
    t = (text or "").lower()
    out = [c for c, pat in CLASS_PAT if re.search(pat, t)]
    return out

def parse():
    if not os.path.exists(SRC):
        d = I.api("thoriummod.wiki.gg", {"action":"parse","page":"Armor","prop":"text",
                                         "formatversion":"2","format":"json"})
        json.dump(d, open(SRC, "w"))
    h = json.load(open(SRC))["parse"]["text"]
    heads = [(m.start(), m.group(1)) for m in
             re.finditer(r'id="(Pre-Hardmode|Hardmode|Thrower|Healer|Bard|Miscellaneous)"', h)]
    tabs = [m.start() for m in re.finditer(r"<table", h)]
    out = {}      # (class, hardmode) -> [ {name, img, url} ]
    for ti, t in enumerate(tabs):
        prev = [nm for pos, nm in heads if pos < t]
        sect = prev[-1] if prev else ""
        if sect == "Miscellaneous": continue
        end = tabs[ti + 1] if ti + 1 < len(tabs) else len(h)
        seg = h[t:end]
        rows = re.findall(r"<tr>(.*?)</tr>", seg, re.S)
        for r in rows:
            tds = re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)
            if len(tds) < 6: continue
            setcell = tds[1]
            m = re.search(r'<a href="(/wiki/[^"]+)"[^>]*>([^<]+)</a>', setcell)
            if not m: continue
            url, name = "https://thoriummod.wiki.gg" + m.group(1), m.group(2).strip()
            if not re.search(r"armor|armour", name, re.I): continue
            img = re.search(r'src="(/images/[^"]+)"', setcell)
            img = ("https://thoriummod.wiki.gg" + img.group(1)) if img else None
            notes = re.sub(r"<[^>]+>", " ", tds[6] if len(tds) > 6 else "")
            if sect in ("Thrower", "Healer", "Bard"):
                cls = [sect]
                hard = bool(re.search(r"hardmode", notes, re.I))
            else:
                cls = classes_for(notes) or ["Mixed"]
                hard = (sect == "Hardmode")
            for c in cls:
                out.setdefault("%s|%s" % (c, int(hard)), [])
                if not any(x["name"] == name for x in out["%s|%s" % (c, int(hard))]):
                    out["%s|%s" % (c, int(hard))].append({"name": name, "img": img, "url": url})
    return out

if __name__ == "__main__":
    d = parse()
    json.dump(d, open(os.path.join(BASE, "thorium_armor.json"), "w"))
    print("thorium armour sets by class/era:")
    for k in sorted(d):
        cls, hard = k.split("|")
        print("  %-9s %-13s %2d  %s" % (cls, "hardmode" if hard=="1" else "pre-hardmode",
                                        len(d[k]), ", ".join(x["name"] for x in d[k][:5])))
