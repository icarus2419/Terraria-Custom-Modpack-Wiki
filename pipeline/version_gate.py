"""The vanilla wiki documents a newer game than the one this pack runs on.

terraria.wiki.gg tracks current desktop Terraria. tModLoader is a separate build that
lags it, and this pack is tModLoader 1.4.4. So every vanilla item added in 1.4.5 is on
the wiki, gets scraped into our item database, and gets recommended in loadouts -- for a
game the player cannot launch. Twenty-seven of them were reaching the loadout panels,
including the entire whip tag-slot accessory chain, which 1.4.5.7 introduced and which
this pack's summoner therefore does not have.

Whip stacking still works in 1.4.4: tags from different whips stack natively, which is
what 1.4.5.0 removed and 1.4.5.7 gave back through these accessories. The build is fine.
The accessories are not there.

Names below are the "new items" list from the 1.4.5.7 patch page, verbatim:
https://terraria.wiki.gg/wiki/1.4.5.7

If tModLoader ever ships a 1.4.5 build, set GAME_VERSION to that and the gate opens.
"""

GAME_VERSION = "1.4.4"

# Vanilla items introduced in Desktop 1.4.5.7, grouped as the patch page groups them.
ADDED_IN_1_4_5_7 = {
    # summon weapons
    "Daybloom Staff", "Glacier Fang", "Mystic Bloom", "Lightning Strike",
    "Clay Bud Staff", "Ruinous Staff", "Arc Surge",
    # accessories -- the whip tag-slot system lives here
    "Silver Bracer", "Snake Band", "Mobius Strip", "Wicked Armlet", "Poison Barb",
    "Harpy Charm", "Snapping Stone", "Chaos Cylinder", "Heavy Sling", "Ouroboros Ring",
    "Twilight Grasp", "Scout's Sling", "Templar's Sling", "Royal Guard's Harness",
    "Pyroclastic Stone", "Armlet Of Ruin", "Seraph Necklace", "Phoenix Quiver",
    "Wicked Claws", "Silver Shield", "Sweet Barb", "Catalyst Band",
    "Druidic Serpent Cloak", "Crossed Heart Necklace", "Restoration Shield",
    "Mystic Arts Sash",
    # consumables and misc
    "Kinship Peach", "Little Kinship Peach", "Giant Tiki", "Guide to Old World Parkour",
}

# Version each set of names was introduced in, so a future tModLoader build can reopen
# the gate one release at a time rather than all at once.
BY_VERSION = {"1.4.5.7": ADDED_IN_1_4_5_7}


def _tuple(v):
    return tuple(int(p) for p in v.split("."))


def unavailable(version=GAME_VERSION):
    """Item names that exist on the vanilla wiki but not in `version` of the game."""
    out = set()
    for added, names in BY_VERSION.items():
        if _tuple(version) < _tuple(added):
            out |= names
    return out


def gate_loadouts(loadouts, version=GAME_VERSION):
    """Drop vanilla picks the player's build cannot have. Returns a list of what went.

    Only vanilla entries are touched. A mod may legitimately ship its own item under a
    name the vanilla wiki also uses, and the mod's copy is real.
    """
    gone, blocked = [], unavailable(version)
    for stage, classes in loadouts["data"].items():
        for cls, mods in classes.items():
            for mod, sections in mods.items():
                if mod not in ("vanilla", "_carry"):
                    continue
                for sec in sections:
                    keep = []
                    for it in sec["items"]:
                        if it["name"] in blocked:
                            gone.append((stage, cls, mod, sec["t"], it["name"]))
                        else:
                            keep.append(it)
                    sec["items"] = keep
    # A section emptied by the gate would render as a heading with nothing under it.
    for stage, classes in loadouts["data"].items():
        for cls, mods in classes.items():
            for mod in list(mods):
                mods[mod] = [s for s in mods[mod] if s["items"]]
                if not mods[mod]:
                    del mods[mod]
    return gone
