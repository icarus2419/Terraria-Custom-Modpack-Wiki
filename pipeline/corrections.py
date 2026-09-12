"""Hand-verified fixes for things the scrape got wrong.

Each entry below was checked against the mod's own wiki page, and the source is named.
These are corrections, not opinions: a damage figure that is off by a factor of 28, a
class label that contradicts the item's own tooltip, a boss placed before three bosses
it cannot be summoned without.

Run this after the data build and before the page generators:

    python3 pipeline/corrections.py

It rewrites data/loadouts.json, data/loadout_stats.json and data/bosses.json in place,
then prints what it changed. Re-running is safe -- every fix is idempotent.
"""
import json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, BASE)
import version_gate as VG
import world_gate as WG
import tier_floor as TF


# ---------- loadout_stats.json ----------

# The Old One's Army sentry rods scraped their item id into every numeric field. 3824 is
# the Ballista Rod's id, 3832 the Explosive Trap Rod's; "Snail" is what the speed lookup
# returns for a use time that is really an id. Damage and damage type survived, so keep
# those and drop the rest rather than printing a knockback of 3824.
ID_SCRAPED = {
    "Ballista Rod": 3824, "Ballista Cane": 3824,
    "Explosive Trap Rod": 3832, "Explosive Trap Cane": 3832, "Explosive Trap": 3832,
}

# thoriummod.wiki.gg/wiki/The_Blender -- 12 Radiant damage, a pre-Hardmode Healer scythe
# crafted from 8 Crimtane Bars. The scrape recorded 340 Melee, which put it top of every
# pre-mechanical melee ranking on the site by a margin of three.
STAT_FIXES = {
    "The Blender": {
        "damage": 12, "dtype": "Radiant", "kind": "Weapon · Healer",
        "tip": "Hitting foes grants Soul Essence; at 5 stacks you recover life and mana.",
    },
}


def fix_stats(stats):
    changed = []
    for name, bad in ID_SCRAPED.items():
        s = stats.get(name)
        if not s:
            continue
        for field in ("knockback", "velocity", "use", "tip"):
            if str(s.get(field)) == str(bad):
                del s[field]
                changed.append("%s: dropped %s (was the item id)" % (name, field))
        if s.get("speed") == "Snail":
            del s["speed"]
            changed.append("%s: dropped speed (derived from the id)" % name)
    for name, fields in STAT_FIXES.items():
        s = stats.get(name)
        if not s:
            continue
        for k, v in fields.items():
            if s.get(k) != v:
                changed.append("%s: %s %r -> %r" % (name, k, s.get(k), v))
                s[k] = v
    return changed


# ---------- loadouts.json ----------

# (stage, class, item) placements that are wrong about the class or the tier.
#   Pain Monger's armor  -- spiritmod.wiki.gg: every piece is magic damage, crit or mana.
#                           No summon damage, no minion slots, no sentry slots.
#   Phantom In The Mirror -- starsabovemod.wiki.gg: the Dioskouroi unlock is pre-Hardmode,
#                           which is why it surfaces early, but the recipe needs a
#                           Shroomite Bar, The Horseman's Blade and a Christmas Tree
#                           Sword. Ectoplasm gates the Horseman's Blade, so post-Plantera.
DROP_PLACEMENTS = [
    ("mech", "Summoner", "Pain Monger's armor"),
    ("mech", "Melee", "Phantom In The Mirror"),
]

# parse_guides.py follows every link in a guide's gear list, including ones that point
# at a concept page rather than an item. These reached the panels as equippable picks:
# "aggro" is the game mechanic, and "Explosive Trap" the sentry-type page (the item is
# the Explosive Trap Rod, which is listed separately and correctly).
CONCEPT_LINKS = {"aggro", "Explosive Trap"}

MOVE_PLACEMENTS = [
    # (from_stage, to_stage, class, item)
    ("mech", "golem", "Melee", "Phantom In The Mirror"),
]


def fix_loadouts(loadouts):
    changed = []
    data = loadouts["data"]

    for stage, classes in data.items():
        for cls, mods in classes.items():
            for sections in mods.values():
                for sec in sections:
                    before = {i["name"] for i in sec["items"]}
                    sec["items"] = [i for i in sec["items"] if i["name"] not in CONCEPT_LINKS]
                    for n in sorted(before - {i["name"] for i in sec["items"]}):
                        changed.append("%s: concept link removed from %s/%s" % (n, stage, cls))

    # Move first, so the moved copy is built before the source placement is dropped.
    for src, dst, cls, item in MOVE_PLACEMENTS:
        found = None
        for mod, sections in data.get(src, {}).get(cls, {}).items():
            for sec in sections:
                for it in sec["items"]:
                    if it["name"] == item:
                        found = (mod, sec["t"], it)
        if not found:
            continue
        mod, title, entry = found
        dest = data.setdefault(dst, {}).setdefault(cls, {}).setdefault(mod, [])
        sec = next((s for s in dest if s["t"] == title), None)
        if sec is None:
            sec = {"t": title, "src": "Corrected tier", "items": []}
            dest.append(sec)
        if not any(i["name"] == item for i in sec["items"]):
            sec["items"].append(entry)
            changed.append("%s: %s/%s -> %s/%s" % (item, src, cls, dst, cls))

    for stage, cls, item in DROP_PLACEMENTS:
        for mod, sections in list(data.get(stage, {}).get(cls, {}).items()):
            for sec in sections:
                before = len(sec["items"])
                sec["items"] = [i for i in sec["items"] if i["name"] != item]
                if len(sec["items"]) != before:
                    changed.append("%s: removed from %s/%s/%s" % (item, stage, cls, sec["t"]))
            data[stage][cls][mod] = [s for s in sections if s["items"]]
            if not data[stage][cls][mod]:
                del data[stage][cls][mod]
    return changed


# ---------- bosses.json ----------

# thoriummod.wiki.gg/wiki/Lich -- "can only be summoned after defeating all three
# mechanical bosses". The chart merge had it at 33, ahead of The Twins at 34, so the
# checklist told you to fight a boss you cannot summon yet.
BOSS_FIXES = {
    "Lich": {
        "order": 37.5,
        "how": "stated",
        "evidence": "It can only be summoned at night after all three mechanical "
                    "bosses have been defeated.",
        # anchor is the boss it follows in the list, stage the loadout checkpoint it
        # belongs to. Both still pointed at the pre-mechanical position.
        "anchor": "Skeletron Prime",
        "stage": "plantera",
    },
}


def fix_bosses(bosses):
    changed = []
    for b in bosses["bosses"]:
        fix = BOSS_FIXES.get(b["name"])
        if not fix:
            continue
        for k, v in fix.items():
            if b.get(k) != v:
                changed.append("%s: %s %r -> %r" % (b["name"], k, b.get(k), v))
                b[k] = v
    return changed


def _rewrite(path, obj, indent=None):
    """Write back in the format the build wrote, so the diff shows only real changes."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=indent)


# The generators resolve a data file to pipeline/ first and fall back to data/. The
# pipeline copy is the build's working output and the data copy is what ships, so a
# correction has to land on both or the page is built from the one that was missed.
def _copies(name):
    return [p for p in (os.path.join(BASE, name), os.path.join(DATA, name))
            if os.path.exists(p)]


def _patch(name, fn, indent=None):
    """Apply fn to every copy. Report the union: a copy already fixed reports nothing,
    and reporting only the last one would call a real run a no-op."""
    seen, lines = set(), []
    for p in _copies(name):
        obj = json.load(open(p, encoding="utf-8"))
        for line in fn(obj):
            if line not in seen:
                seen.add(line)
                lines.append(line)
        _rewrite(p, obj, indent)
    return lines


def main():
    report = {}
    report["loadout_stats"] = _patch("loadout_stats.json", fix_stats)

    gate_log, world_log, floor_log = [], [], []

    def _loadouts(obj):
        changed = fix_loadouts(obj)
        gate_log[:] = VG.gate_loadouts(obj)
        world_log[:] = WG.gate_loadouts(obj)
        floor_log[:] = TF.apply(obj)
        return changed

    report["loadouts"] = _patch("loadouts.json", _loadouts)
    report["version gate (%s)" % VG.GAME_VERSION] = [
        "%s: removed from %s/%s/%s" % (n, st, cls, sect) for st, cls, _m, sect, n in gate_log
    ]
    report["world gate (%s)" % WG.WORLD_EVIL] = [
        "%s: %s/%s/%s" % (n, st, cls, sect) for st, cls, sect, n in world_log
    ]
    report["tier floor"] = [
        "%s: dropped from %s/%s (not craftable until %s)" % (n, st, cls, floor)
        for st, cls, _sect, n, floor in floor_log
    ]
    report["bosses"] = _patch("bosses.json", fix_bosses, indent=1)

    # The page ships a sprite and a stats blob for every name the loadouts mention.
    # Gated names are no longer mentioned, so their entries are dead payload -- a
    # base64 PNG and a tooltip for gear the player will never be shown. Drop only the
    # names that survive nowhere in the loadouts, so a mod item that happens to share a
    # vanilla name keeps its data.
    still_used = set()
    for p in _copies("loadouts.json"):
        L = json.load(open(p, encoding="utf-8"))
        for classes in L["data"].values():
            for mods in classes.values():
                for sections in mods.values():
                    for sec in sections:
                        still_used |= {i["name"] for i in sec["items"]}
    orphans = (VG.unavailable() | WG.locked()) - still_used
    pruned = []
    for name in ("loadout_sprites.json", "loadout_stats.json"):
        for p in _copies(name):
            obj = json.load(open(p, encoding="utf-8"))
            hit = [k for k in orphans if k in obj]
            for k in hit:
                del obj[k]
            if hit:
                _rewrite(p, obj)
                pruned += ["%s: dropped %s" % (os.path.basename(name), k) for k in sorted(hit)]
    report["dead payload"] = sorted(set(pruned))

    total = 0
    for section, lines in report.items():
        if not lines:
            continue
        print("== %s (%d)" % (section, len(lines)))
        for line in lines:
            print("   " + line)
        total += len(lines)
    print("\n%d corrections applied." % total)


if __name__ == "__main__":
    main()
