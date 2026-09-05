# Terraria Custom Modpack Wiki

An offline wiki for a Terraria tModLoader 1.4.4 modpack. Every recipe the pack adds, every crafting
station, how to get each item, and a suggested loadout for every class before every boss.

**Live:** https://josephwiki.pages.dev · **Mirror:** https://icarus2419.github.io/Terraria-Custom-Modpack-Wiki

**5,455 recipes · 6,255 items · 130 stations · 2,831 loadout entries**

Open `index.html` in any browser. No install, no build step, no network.

## The four pages

| Page | What it is |
|---|---|
| `index.html` | Home — navigation into the three sections below |
| `tinkerers.html` | Every accessory combination, modded and vanilla side by side |
| `recipes.html` | Every recipe the six mods add, across all 130 stations |
| `loadouts.html` | Suggested gear per class at each boss checkpoint |

## Loadouts

Eleven boss stages from Pre-Boss to Endgame, split at Hardmode. For each stage, a card per class
listing **armour, accessories, weapons and buffs** — accessories always present, because they are
what people actually forget.

Nine classes, including Thorium's **Bard, Healer and Thrower**. Healer only functions in
multiplayer; Bard buffs scale with party size.

Each mod names its checkpoints differently — Thorium's *Pre-Eater of Worlds / Brain of Cthulhu*,
Spirit's *Pre-Evil Boss* and Stars Above's *Pre-The Vagrant of Space and Time* all sit at the same
point. They are mapped onto one timeline, and every block still shows which wiki it came from.

Where a guide stops re-listing armour or accessories at a later stage (vanilla does this at
Pre-Moon Lord), the previous stage's gear is carried forward and labelled as such rather than
leaving a gap. 81 of 83 class-stage cards list both armour and accessories; the two that do not are
at Pre-Boss, where there is no earlier stage to carry from.

## Recipes

| Source | Recipes |
|---|---:|
| Thorium Mod | 2,151 |
| Fargo's Souls / Mutant Mod | 1,395 |
| Spirit Classic | 665 |
| Spirit Reforged | 662 |
| The Stars Above | 224 |
| Calamity Fables | 201 |
| Terraria — Tinkerer's Workshop only | 157 |

Vanilla's other ~3,940 recipes are deliberately not duplicated — terraria.wiki.gg covers those. The
vanilla Tinkerer's Workshop is included because it is where mod and vanilla accessories combine.

Station names come from each wiki's own table captions, so cross-mod conditionals survive verbatim:
`Shimmer (With Spirit Classic Installed)`, `Tinkerer's Workshop and Ecto Mist`,
`Iron Anvil or Lead Anvil`.

**The Stars Above adds no Tinkerer's Workshop recipes** — its stations are the Iron Anvil,
Celestriad Root, Loom and Work Bench. Verified, not assumed.

## Pre-Hardmode classification

Every recipe and item is classified as craftable before Hardmode or not, from — strongest first:

1. the wikis' machine-readable infobox `tags` field
2. the `Hardmode-only items` category
3. mod infobox `hardmode = yes`
4. lead-sentence wording, distinguishing *pre-Hardmode* from *Hardmode*
5. drop-source NPCs resolved to the `Hardmode-only NPCs` category
6. recipe propagation to a fixed point

Step 5 exists because the wikis have gaps: Soul of Might carries no `hardmode` tag and sits in no
Hardmode category, despite dropping only from The Destroyer. Items with no Hardmode evidence
anywhere are treated as pre-Hardmode — that is these wikis' tagging convention — and each card
states that weaker basis rather than hiding it.

## Where the data comes from

Nothing is written from memory. Recipes are parsed from each wiki's own generated
`Recipes/<Station>` tables via the MediaWiki API — 161 station pages across seven wikis — with each
table on a page kept separate by its caption. Item descriptions, drop rates and prices come from the
raw wikitext of each item page. Loadouts come from each wiki's `Guide:Class setups`.

Sources: `terraria.wiki.gg` · `thoriummod.wiki.gg` · `fargosmods.wiki.gg` · `spiritmod.wiki.gg` ·
`starsabovemod.wiki.gg` · `calamityfables.wiki.gg`

### Verification

- Integrity checks pass clean across all 5,455 recipes and 6,255 items — no dangling references, no
  bad quantities, no wiki markup leaking into names, descriptions or drop tables.
- Recipes cross-checked against each wiki's recipe *database* by result (`{{recipes|result=X}}`),
  independent of the station pages parsed. Spirit Reforged, whose namespace that query cannot see,
  was diffed against its authoritative `register` pages instead — 224/224 on the Shimmer table.
- The Hardmode classifier was checked against 39 known cases with no misclassifications.
- Loadout entries spot-checked verbatim against live wikitext, including Bard and Healer.

Where a mod's wiki is out of date with its own mod, this inherits that.

## Repository layout

```
index.html tinkerers.html recipes.html loadouts.html   the wiki
data/         merged datasets (recipes, items, Hardmode verdicts, loadouts)
pipeline/     the scripts that build it from the source wikis
_preserved/   the first Tinkerer's-only build, kept for reference
```

## Rebuilding

Python 3, standard library only. From inside `pipeline/`:

```bash
python3 full_fetch.py       # every Recipes/<Station> page across the seven wikis
python3 full_items.py       # parse stations, then batch-fetch item wikitext
python3 full_sprites.py     # download and base64-encode every sprite
python3 full_entities.py    # resolve drop-source NPCs
python3 full_cats2.py       # categories for items with no direct Hardmode signal
python3 full_data.py        # merge, index, classify Hardmode
python3 loadouts.py         # parse the class-setup guides onto one timeline
python3 loadout_sprites.py
python3 full_gen.py         # recipes.html
python3 gen.py              # tinkerers.html
python3 loadout_gen.py      # loadouts.html
python3 home_gen.py         # index.html
```

Every stage caches, so a re-run after a parser change costs no requests.

## Licence

Recipe and item data belongs to the respective wikis, under their own terms (wiki.gg communities are
CC BY-SA unless stated otherwise). Item sprites are © Re-Logic and the respective mod authors, used
here for reference. A fan reference tool, not affiliated with Re-Logic or any mod team.
