# Terraria Custom Modpack Wiki

An offline wiki for a Terraria tModLoader 1.4.4 modpack. Every recipe the pack adds, every crafting
station, how to get each item, and a suggested loadout for every class before every boss.

**Live:** https://josephwiki.pages.dev · **Mirror:** https://icarus2419.github.io/Terraria-Custom-Modpack-Wiki

**87 bosses · 5,455 recipes · 6,255 items · 130 stations · 2,956 loadout entries**

Open `index.html` in any browser. No install, no build step, no network.

## The five pages

They are in the order a player needs them: what to fight, what to wear, what to make.

| Page | What it is |
|---|---|
| `index.html` | Home — where to start |
| `bosses.html` | Every boss in the pack in one fight order, as a tickable checklist |
| `loadouts.html` | One filled equipment panel per class, per boss checkpoint |
| `recipes.html` | Every recipe the six mods add, across all 130 stations |
| `tinkerers.html` | Every accessory combination, modded and vanilla side by side |

## One run, followed across the site

The boss checklist is the only place you enter anything. What you tick is kept in your browser,
and every other page reads it back:

- **Loadouts** opens on the checkpoint you are actually at, and marks it on the timeline.
- **All Recipes** and **Tinkerer's Workshop** offer *Only what I can make now*, which hides
  everything gated behind Hardmode until you have ticked off the Wall of Flesh.
- Every page carries a one-line run bar: how many bosses are down, what is next, which era you
  are in.

Nothing is uploaded; it is `localStorage` in the one browser, and the site works exactly as before
if you never tick anything.

## Bosses

**87 bosses — 54 of them added by the mods** — merged into a single fight order.

Thorium, Spirit, The Stars Above and Calamity Fables each publish a boss progression chart that
already interleaves their bosses with the vanilla ones. Those charts are laid over one another on
the vanilla bosses they share, so *after Skeletron* is that wiki's own placement, not a guess.
Vanilla's order is its own `Bosses` page.

Six bands: pre-Hardmode, Hardmode, post-Moon Lord, event bosses, mini-bosses and optional fights,
and secret world seeds. A modded boss sits in the band of the vanilla boss it follows, with the
Wall of Flesh and Moon Lord treated as gates rather than as the last of their band.

Fargo's Souls publishes no chart — but its boss pages say in words where each fight belongs
(*"intended to be fought before the mechanical bosses"*, *"meant to be fought before King Slime"*),
so those are placed from their own sentences, which are quoted on the row. A placement read that
way is clamped to the tier its wiki files the boss under, so a post-Moon Lord superboss can never
drift into pre-Hardmode. Where a boss sits between two placed ones on its own Bosses page it
inherits a spot between them, marked as inferred rather than stated.

That leaves **15 unordered**, all of them mini-bosses: no wiki sequences them, and guessing would
be worse than saying so. They sit in their own band.

Of the 87: 64 placed by a progression chart, 5 by their page's own words, 3 inferred from listing
position, 15 left unordered.

Each row carries the summon item, the environment and the health its wiki publishes, and links to
the Loadouts checkpoint you want to be geared for. Where a wiki publishes none of that, the row
says nothing rather than inventing it: 85 of 87 have a summon item, 73 have art on their own page,
53 publish health inline.

## Loadouts

Eleven boss checkpoints from Pre-Boss to Endgame on one timeline, split at Hardmode. You pick the
boss on the timeline and your class; the page answers with a single **Terraria equipment panel** —
one armour set, five accessory slots, a weapon hotbar, ammo, buffs and utility — rather than a wall
of every option at once. Arrow keys walk the run; your class is remembered between visits.

Seven classes, including Thorium's **Bard, Healer and Thrower**. Healer only functions in
multiplayer; Bard buffs scale with party size. The guides' *Mixed* and *All Classes* sections are
not a class you pick — that gear is folded into every class's panel and tagged **any class**.

### How a slot gets filled

The guides list far more gear than you can wear — 134 entries for Melee at Pre-Mechanical Bosses
alone. Each slot takes the first of:

1. an entry the wiki itself marks **Best** (or *Second Best*)
2. the highest published defence, for armour, or damage, for weapons
3. whatever that wiki lists first

Distinct roles are covered before doubling up, so a hotbar is not six broadswords. **Every pick
states the basis it was chosen on**, and nothing is invented: where a wiki publishes no ranking and
no stats, the slot says it is simply what that guide lists first.

Nothing is hidden. **Everything else the guides list** under the panel holds every published entry
for that class at that checkpoint, ranked the same way, with the equipped ones marked — all 2,956
gear entries are still reachable. An item a wiki lists under two roles keeps both listings.

Each slot's top pick is marked **recommended**, and says what it replaces — *"↑ upgrade from
Lodestone armor (Pre-Mechanical Bosses)"* — so the panel reads as a progression rather than a
snapshot. The comparison is against the last checkpoint where this class had a published list.

**New here** means the gear was not in this class's list at *its* previous checkpoint. Healer has no
published list at Pre-Moon Lord, so its Endgame list is compared against Pre-Lunatic Cultist rather
than pretending everything is new. Where a class has no published setup at a checkpoint at all
(9 of the 77 class-checkpoint pairs), the page says so, shows the any-class gear instead, and links
to the nearest checkpoints that do have one.

Each mod names its checkpoints differently — Thorium's *Pre-Eater of Worlds / Brain of Cthulhu*,
Spirit's *Pre-Evil Boss* and Stars Above's *Pre-The Vagrant of Space and Time* all sit at the same
point. They are mapped onto one timeline, and every block still shows which wiki it came from.

Where a guide stops re-listing armour or accessories at a later stage (vanilla does this at
Pre-Moon Lord), the previous stage's gear is carried forward, labelled as such, and never counted as
new.

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

Boss rosters and fight order come from each wiki's own `Bosses` page and its progression chart;
per-boss detail from the `npc infobox` on each boss's page.

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
index.html bosses.html loadouts.html recipes.html tinkerers.html   the wiki
data/         merged datasets (bosses, recipes, items, Hardmode verdicts, loadouts)
pipeline/     the scripts that build it from the source wikis
_preserved/   the first Tinkerer's-only build, kept for reference
```

Every generator writes its page into the repository root. The JSON caches under `pipeline/` are
regenerable intermediates and are not committed; the merged datasets in `data/` are.

## Rebuilding

Python 3, standard library only. From inside `pipeline/`:

```bash
python3 boss_fetch.py       # each wiki's Bosses page, boss categories and boss pages
python3 bosses.py --write   # merge the progression charts into one order
python3 boss_sprites.py     # a sprite for every boss
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
python3 boss_gen.py         # bosses.html
python3 home_gen.py         # index.html
```

Every stage caches, so a re-run after a parser change costs no requests.

## Licence

Recipe and item data belongs to the respective wikis, under their own terms (wiki.gg communities are
CC BY-SA unless stated otherwise). Item sprites are © Re-Logic and the respective mod authors, used
here for reference. A fan reference tool, not affiliated with Re-Logic or any mod team.
