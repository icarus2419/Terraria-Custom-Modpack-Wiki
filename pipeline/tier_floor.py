"""Thorium's Armor page has two tiers. The run has eleven checkpoints.

`thorium_armor.py` buckets Thorium's armour into pre-Hardmode and Hardmode, and the
loadout merge then offers every Hardmode set at every Hardmode checkpoint. So Terrarium
armour -- 62 defence, crafted at a station the Lunatic Cultist drops -- was listed as an
option for the Pre-Mechanical Bosses panel, four bosses and most of a game too early.

The fix is not another hand-written tier list: it is the recipe, which the site already
has. A set cannot be built before its crafting station exists or its materials drop, and
both are in `full_site_data.json`. The floors below name that evidence.

    Ancient Manipulator   dropped by the Lunatic Cultist        -> moonlord
    Primordial Essences   post-Moon Lord, from The Primordials  -> endgame
    Soul Forge            needs Soul of Fright and Soul of Sight -> plantera
    Chlorophyte Bar       post-mechanical bosses                -> plantera
    Martian Conduit       post-Golem, Martian Madness           -> cultist

Only sets whose gate is later than where they were being offered appear here. Lodestone
and Valadium smelt from chunks at a Hellforge and are genuinely early Hardmode; White
Knight's Hallowed Charm is Pixie Dust and Soul of Light, both available before the
mechanical bosses. Those are left where they are.
"""

# item name -> (earliest stage key, why)
FLOORS = {
    "Terrarium armor":  ("moonlord", "Terrarium Core is crafted at the Ancient Manipulator, "
                                     "which the Lunatic Cultist drops"),
    "Pyromancer armor": ("endgame",  "Inferno Essence is post-Moon Lord, dropped by The Primordials"),
    "Assassin armor":   ("endgame",  "Death Essence is post-Moon Lord, dropped by The Primordials"),
    "Tide Turner armor":("endgame",  "Ocean Essence is post-Moon Lord, dropped by The Primordials"),
    "Life Bloom armor": ("plantera", "Chlorophyte Bar is post-mechanical bosses"),
    "Titan armor":      ("plantera", "Titanic Bar is forged at the Soul Forge, which needs "
                                     "Soul of Fright and Soul of Sight"),
    "Illumite armor":   ("plantera", "Illumite Ingot is forged at the Soul Forge"),
    "Dread armor":      ("plantera", "Dread Soul is forged at the Soul Forge"),
    "Conduit armor":    ("cultist",  "Martian Conduit Plating is post-Golem, from Martian Madness"),
}


def apply(loadouts):
    """Drop placements earlier than the set's own recipe allows."""
    order = loadouts["order"]
    rank = {k: i for i, k in enumerate(order)}
    gone = []
    for stage, classes in loadouts["data"].items():
        for cls, mods in classes.items():
            for sections in mods.values():
                for sec in sections:
                    keep = []
                    for it in sec["items"]:
                        floor = FLOORS.get(it["name"])
                        if floor and rank[stage] < rank[floor[0]]:
                            gone.append((stage, cls, sec["t"], it["name"], floor[0]))
                        else:
                            keep.append(it)
                    sec["items"] = keep
            for mod in list(mods):
                mods[mod] = [s for s in mods[mod] if s["items"]]
                if not mods[mod]:
                    del mods[mod]
    return gone
