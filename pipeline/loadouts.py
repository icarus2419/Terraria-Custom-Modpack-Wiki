"""Merge the four class-setup guides onto one canonical boss timeline."""
import json, os, re, sys
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import parse_guides as PG

# canonical progression: (key, label, the boss this stage prepares you for, hardmode?)
#   key, full stage label, what you are gearing up for, hardmode?, short nav name
STAGES = [
 ("start",     "Pre-Boss",             "Before any boss \u2014 gearing up",             False, "Your first boss"),
 ("eye",       "Pre-Eye of Cthulhu",   "Eye of Cthulhu",                               False, "Eye of Cthulhu"),
 ("evil",      "Pre-Eater / Brain",    "Eater of Worlds or Brain of Cthulhu",          False, "Eater / Brain"),
 ("skeletron", "Pre-Skeletron",        "Skeletron",                                    False, "Skeletron"),
 ("wof",       "Pre-Wall of Flesh",    "Wall of Flesh \u2014 the gate into Hardmode",   False, "Wall of Flesh"),
 ("mech",      "Pre-Mechanical Bosses","The Twins, Destroyer, Skeletron Prime",        True,  "Mechanical Bosses"),
 ("plantera",  "Pre-Plantera",         "Plantera",                                     True,  "Plantera"),
 ("golem",     "Pre-Golem",            "Golem",                                        True,  "Golem"),
 ("cultist",   "Pre-Lunatic Cultist",  "Lunatic Cultist and the Lunar Events",         True,  "Lunatic Cultist"),
 ("moonlord",  "Pre-Moon Lord",        "Moon Lord",                                    True,  "Moon Lord"),
 ("endgame",   "Endgame",              "Post-Moon Lord and the mods' final bosses",    True,  "Endgame"),
]
ORDER = [s[0] for s in STAGES]

MAP = {
 "gearing up":"start", "pre-boss":"start", "pre-bosses":"eye",
 "pre-eye of cthulhu":"eye",
 "pre-eater of worlds / brain of cthulhu":"evil", "pre-evil boss":"evil",
 "pre-the vagrant of space and time":"evil",
 "mid pre-hardmode":"skeletron", "pre-skeletron":"skeletron",
 "pre-wall of flesh":"wof",
 "post-wall of flesh":"mech", "pre-mech bosses":"mech", "pre-mechanical bosses":"mech",
 "post-mechanical bosses":"plantera", "pre-plantera":"plantera",
 "pre-golem":"golem",
 "pre-lunatic cultist":"cultist", "pre-lunar invasion":"cultist",
 "pre-moon lord":"moonlord",
 "endgame":"endgame", "pre-primordials":"endgame", "pre-warrior of light":"endgame",
 "pre-tsukiyomi, the first starfarer":"endgame",
}
SKIP_CLASS = {"Building/Wiring","Fishing","Catching","Exploring/Mining"}
CLASS_ORDER = ["Melee","Ranged","Magic","Summoner","Thrower","Bard","Healer","Mixed","All Classes"]
CLASS_META = {
 "Melee":     ("#d24b3a","Swords, spears and yoyos. High defence, short reach."),
 "Ranged":    ("#4a9e57","Bows, guns and launchers. Needs ammo, hits hardest at distance."),
 "Magic":     ("#4f7fd4","Mana-hungry, high damage, low defence."),
 "Summoner":  ("#8b5bc4","Minions and whips fight for you. Frail alone."),
 "Thrower":   ("#c9852a","Thorium's throwing class — consumables and returning weapons."),
 "Bard":      ("#c94f9e","Thorium's support class. Buffs scale with party size — strong in co-op."),
 "Healer":    ("#3fae9e","Thorium's healer. Only functions in multiplayer."),
 "Mixed":     ("#7d85ab","Gear that suits any class."),
 "All Classes":("#7d85ab","Gear that suits any class."),
}
CANON = {"armor":"Armour","armors":"Armour","armour":"Armour","armours":"Armour",
         "accessories":"Accessories","accessory":"Accessories",
         "buffs/potions":"Buffs","buffs":"Buffs","buffs/potions/flasks":"Buffs",
         "sentries & banners":"Sentries","sentries":"Sentries",
         "single-target ammunition":"Ammunition","crowd-control ammunition":"Ammunition",
         "ammunition":"Ammunition"}
def canon_cat(t):
    t = re.sub(r"\s+", " ", (t or "")).strip()
    return CANON.get(t.lower(), t or "Gear")

CAT_ORDER = ["Armour","Accessories","Mobility Accessories","Offensive Accessories",
             "Survivability Accessories","Weapons","Single-Target Weapons",
             "Crowd-Control Weapons","Support Weapons","Whips","Minions","Sentries",
             "Mounts","Ammunition","Techniques","Glyphs","Stellar Array","Stellar Novas",
             "Support Tools","Buffs"]
def cat_rank(t):
    t = (t or "").strip()
    return CAT_ORDER.index(t) if t in CAT_ORDER else len(CAT_ORDER)

MODS = {"vanilla":"Terraria","thorium":"Thorium","spirit":"Spirit","stars":"Stars Above"}

def build():
    cards = PG.parse_all()
    out = {}   # stage -> class -> mod -> [ {title, items} ]
    unmapped = set()
    for mod, cs in cards.items():
        for c in cs:
            cl = c.get("cls")
            if not cl or cl in SKIP_CLASS: continue
            raw = re.sub(r"\s+", " ", (c.get("stage") or "")).strip()
            key = MAP.get(raw.lower())
            if not key:
                unmapped.add("%s: %s" % (mod, raw)); continue
            boxes = [b for b in c["boxes"] if b["items"]]
            if not boxes: continue
            boxes.sort(key=lambda b: cat_rank(canon_cat(b["title"])))
            out.setdefault(key, {}).setdefault(cl, {}).setdefault(mod, [])
            for b in boxes:
                out[key][cl][mod].append({"t": canon_cat(b["title"]),
                                          "src": raw,
                                          "items": b["items"][:14]})
    # A guide may not re-list accessories at every stage (vanilla drops them at Pre-Moon Lord).
    # Rather than show a gap, point at the most recent stage that does list them for that class.
    for want, pat in (("Armour", r"^armour$"), ("Accessories", r"accessor")):
        for si, key in enumerate(ORDER):
            for cl, mods in out.get(key, {}).items():
                if any(re.search(pat, b["t"], re.I) for m in mods.values() for b in m):
                    continue
                for back in range(si - 1, -1, -1):
                    prev = out.get(ORDER[back], {}).get(cl, {})
                    hits = [b for m, bs in prev.items() if m != "_carry" for b in bs
                            if re.search(pat, b["t"], re.I)]
                    if hits:
                        lbl = next(s[1] for s in STAGES if s[0] == ORDER[back])
                        out[key][cl].setdefault("_carry", []).append(
                            {"t": want, "src": lbl, "carry": ORDER[back],
                             "items": [i for b in hits for i in b["items"]][:12]})
                        break
    return out, sorted(unmapped)

if __name__ == "__main__":
    data, unmapped = build()
    tot = 0
    print("%-22s %s" % ("STAGE", "classes"))
    for k, label, boss, hm, short in STAGES:
        cl = data.get(k, {})
        n = sum(len(b["items"]) for c in cl.values() for m in c.values() for b in m)
        tot += n
        print("  %-20s %-58s %3d items" % (label, ", ".join(sorted(cl, key=lambda x: CLASS_ORDER.index(x) if x in CLASS_ORDER else 9)), n))
    print("\ntotal loadout items:", tot)
    if unmapped: print("UNMAPPED stages:", unmapped)
    json.dump({"stages": STAGES, "order": ORDER, "class_order": CLASS_ORDER,
               "class_meta": CLASS_META, "mods": MODS, "cat_order": CAT_ORDER, "data": data},
              open(os.path.join(BASE, "loadouts.json"), "w"))
