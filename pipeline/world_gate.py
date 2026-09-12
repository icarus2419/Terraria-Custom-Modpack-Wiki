"""This pack's world is Corruption, so half the evil-biome loot does not exist.

The wikis document both evils side by side, the scrape keeps both, and the loadouts
recommend both. In a Corruption world the Crimson half is unreachable: no Crimson
biome generates, breaking altars in Hardmode spreads Corruption and Hallow rather than
Crimson, and there is no cross-world route to Crimtane, Tissue Sample, Vertebra or Ichor.

The one that matters most is **Ichor**. It drops from Ichor Stickers in the Underground
Crimson and from Hematic Crates fished in Crimson water -- neither of which exists here --
and Flask of Ichor was the "Best" buff pick for Summoner and Melee at five checkpoints
each. Flask of Cursed Flames is the Corruption equivalent and inherits the tag.

World settings come from the Covenant Route install reference: Large, Expert, Corruption.
Set WORLD_EVIL to "crimson" and the gate flips to the Corruption-locked list instead.
"""

WORLD_EVIL = "corruption"

# Verified Crimson-locked: either every option group in the recipe forces a Crimson-only
# material, or the item's own page names the Crimson as its only source.
CRIMSON_LOCKED = {
    # summoner
    "Crimson Hound Staff",       # Vertebra
    "Cloak of the Desert King",  # Crimson Cloak
    "Bleeding Heart Staff",      # Crimtane Bar, Tissue Sample
    # melee
    "Fetid Baghnakhs",           # Crimson Mimic
    "Vampire Knives",            # Crimson Key -> Crimson Chest
    "Bladetongue",               # fishing the Crimson desert
    "Head Spinner",              # Ichor
    "The Rotted Fork",           # Hematic Crate
    "Vile Flail-Core",           # Ichor
    "Crimson Sakura Alpha",
    # ranged
    "The Undertaker",            # Hematic Crate
    "Ripper Slug",               # Tissue Sample
    "Crimson Outbreak",
    # magic
    "Crimson Rod",               # Hematic Crate
    "Life Drain",
    "Vessel Buster",             # Crimtane Bar
    # other classes
    "Crimtane Tomahawk", "Festering Balloon", "Shadewood Tambourine",
    "The Blender", "Dark Contagion",
    # shared
    "Grisly Tongue", "Magiluminescence", "Panic Necklace",
    # keys and their chests -- a Crimson Key cannot drop in a Corruption world
    "Crimson Key", "Crimson Chest",
    # flasks: Ichor has no Corruption source. Its recipe is not in the modded recipe
    # dataset, so it has to be named here rather than derived.
    "Flask of Ichor",
}

CORRUPTION_LOCKED = {
    "Corruptling Staff", "Corruption Key", "Corruption Chest",
    "Scourge of the Corruptor", "Flask of Cursed Flames", "Putrid Scent",
}

# When the gate takes a featured pick away, the counterpart inherits its note rather
# than leaving the slot with nothing marked.
SUCCESSORS = {
    "Flask of Ichor": "Flask of Cursed Flames",
    "Flask of Cursed Flames": "Flask of Ichor",
}


def locked(evil=WORLD_EVIL):
    return CRIMSON_LOCKED if evil == "corruption" else CORRUPTION_LOCKED


def gate_loadouts(loadouts, evil=WORLD_EVIL):
    """Drop unreachable evil-biome picks; hand any 'Best' tag to the counterpart."""
    gone, blocked = [], locked(evil)
    for stage, classes in loadouts["data"].items():
        for cls, mods in classes.items():
            promote = {}
            for sections in mods.values():
                for sec in sections:
                    keep = []
                    for it in sec["items"]:
                        if it["name"] in blocked:
                            gone.append((stage, cls, sec["t"], it["name"]))
                            heir = SUCCESSORS.get(it["name"])
                            if heir and it.get("note"):
                                promote[heir] = it["note"]
                        else:
                            keep.append(it)
                    sec["items"] = keep
            for sections in mods.values():
                for sec in sections:
                    for it in sec["items"]:
                        if it["name"] in promote and not it.get("note"):
                            it["note"] = promote[it["name"]]
                            gone.append((stage, cls, sec["t"],
                                         "%s inherits '%s'" % (it["name"], promote[it["name"]])))
            for mod in list(mods):
                mods[mod] = [s for s in mods[mod] if s["items"]]
                if not mods[mod]:
                    del mods[mod]
    return gone
