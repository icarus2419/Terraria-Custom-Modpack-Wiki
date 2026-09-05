# Terraria Custom Modpack Wiki — Tinkerer's Workshop

A single-file, offline wiki for the **Tinkerer's Workshop** in a Terraria tModLoader 1.4.4 modpack.
The vanilla wiki only knows vanilla; each mod wiki only knows its own mod. This puts all of them in
one table, and tells you how to get every item in it.

**308 combinations · 649 items · 192 of them modded**

Open `index.html` in any browser. No install, no build step, no network.

## What it covers

| Source | Combinations |
|---|---:|
| Terraria (vanilla) | 157 |
| Thorium Mod | 67 |
| Fargo's Souls / Mutant Mod | 70 |
| Spirit Classic | 7 |
| Spirit Reforged | 4 |
| Calamity Fables | 3 |

**The Stars Above adds no Tinkerer's Workshop recipes** — its stations are the Iron Anvil,
Celestriad Root, Loom and Work Bench. Verified, not assumed; nothing is missing on its account.

## What it does

- **Combination table** in the vanilla wiki's Result / Ingredients layout, grouped by source, with
  `or` alternatives and exact quantities.
- **Click any item** — result or ingredient — for its in-game tooltip, rarity, how to get it, drop
  table with real rates, buy/sell price, and every recipe it feeds into.
- **Full crafting chains, expanded.** Terraspark Boots unrolls four levels down to Rocket Boots,
  with each leaf tagged by how you actually obtain it (`chest`, `bought`, `drop`, `fished`).
- **Mod-changed recipes are flagged.** Where a mod redefines a vanilla combination, the mod's
  version is what the game uses and the vanilla row is kept beside it so you can see what moved.
  There are 9 such rows across 6 items — Ankh Shield, Avenger Emblem, Fart in a Balloon,
  Green Horseshoe Balloon, Molten Skull Rose, Yoyo Bag.
- **Recipe groups resolved.** `Any Iron Bar`, `Any Pressure Plate`, `Any Emblem` and the rest list
  what they actually accept, pulled from the game's own recipe-group table.
- Search across every result and ingredient; filter by source; light and dark themes.

## Offline by design

`index.html` is one file, ~820 KB, with no runtime dependencies. All 648 item sprites are embedded
as data URIs, so it works on a second monitor with the Wi-Fi off.

To put it online, enable **GitHub Pages** on this repo (Settings → Pages → Deploy from branch →
`main` / root). `index.html` is at the root, so it serves as-is.

## Repository layout

```
index.html              the wiki — open this
data/site_data.json     the merged dataset (recipes, items, sprites, indexes)
pipeline/               the scripts that build it from the source wikis
```

## Where the data comes from

Nothing here is written from memory. Recipes are parsed structurally from each wiki's own generated
`Recipes/Tinkerer's Workshop` table via the MediaWiki `action=parse` API; item descriptions, drop
rates and prices come from the raw wikitext of each item page; vanilla rarity and coin values come
from `Module:Iteminfo/data`.

Sources: `terraria.wiki.gg` · `thoriummod.wiki.gg` · `fargosmods.wiki.gg` · `spiritmod.wiki.gg` ·
`calamityfables.wiki.gg` (fetched 5 September 2026)

### Verification

- **23 recipes cross-checked independently** — re-resolved through each wiki's recipe *database*
  by result (`{{recipes|result=X}}`), which does not touch the station page that was originally
  parsed. 19 matched exactly; the 4 Spirit Reforged recipes live in a separate namespace and were
  confirmed against its authoritative `register` page instead.
- **Integrity checks pass clean** across all 308 recipes and 649 items — no dangling references,
  no bad quantities, no wiki markup leaking into names, descriptions or drop tables.
- Every item has acquisition text; every item has a sprite except `Any Emblem`, which is a recipe
  group and correctly has no icon.

Where a mod's wiki is out of date with its own mod, this page inherits that. The recipe-database
cross-check is the guard against it.

## Rebuilding

Python 3, standard library only — no dependencies. Run from inside `pipeline/`, in order:

```bash
cd pipeline
python3 fetch.py <host> "<page>" <name>   # pull each wiki's Tinkerer's Workshop table
python3 build_items.py                    # item wikitext -> tooltip/type/rarity/drops/prices/lead
python3 sprites.py                        # download and base64-encode every sprite
python3 build_data.py                     # merge, index, flag duplicate vs changed recipes
python3 gen.py                            # emit the HTML
```

`parse.py` holds the crafts-table parser (rowspan alternatives, the two different quantity markups
the wikis use); `items.py` holds the wikitext helpers. Intermediates are written into `pipeline/`
and are gitignored — `build_items.py` caches raw wikitext, so re-runs after a parser change cost no
requests. `gen.py` writes `pipeline/tinkerers-workshop.html`; copy it to `index.html` at the root
to publish.

## Licence

Recipe and item data belongs to the respective wikis, available under their own terms (wiki.gg
communities are CC BY-SA unless stated otherwise). Item sprites are © Re-Logic and the respective
mod authors, used here for reference. This is a fan reference tool and is not affiliated with
Re-Logic or any of the mod teams.
