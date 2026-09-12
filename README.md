# Terraria Custom Modpack Wiki

An offline wiki for a Terraria tModLoader 1.4.4 modpack. Every recipe the pack adds, every crafting
station, how to get each item, and a suggested loadout for every class before every boss.

**Live:** https://josephwiki.pages.dev · **Mirror:** https://icarus2419.github.io/Terraria-Custom-Modpack-Wiki

**87 bosses · 5,455 recipes · 6,255 items · 130 stations · 2,956 loadout entries**

Open `index.html` in any browser. No install, no build step, no network.

## The six pages

They are in the order a player needs them: what to fight, what to wear, what to make.

| Page | What it is |
|---|---|
| `index.html` | Home — where to start |
| `bosses.html` | Every boss in the pack in one fight order, as a tickable checklist |
| `loadouts.html` | One filled equipment panel per class, per boss checkpoint |
| `recipes.html` | Every recipe the six mods add, across all 130 stations |
| `tinkerers.html` | Every accessory combination, modded and vanilla side by side |
| `stars.html` | The Stars Above, explained — the one mod that adds a system |

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

## The Stars Above

Five of the six mods add things to make and fight. The Stars Above also adds a companion and a
menu bound to an item, and none of that is discoverable from a recipe list — so the home page
so it gets its own page, reached from its own card on the home page.

Every part of it answers the same four questions — **what it does, why you want it, how you get it,
and when in the run**: the **Spatial Disk**, the permanent Asphodene/Eridani choice, and the four
screens behind the disk's right-click (Stellar Array, Stellar Nova, Astrolabe, Archive), each with
its unlock — the Nova after The Vagrant of Space and Time, the Astrolabe after King Slime. Then the
Nova's damage table, the mod's nine bosses in the pack's own fight order, and the handful of items
worth knowing by name with their recipes.

`stars_guide.py` fetches the mod's `Early Guide` and its `Stellar Array`, `Stellar Novas`,
`Cosmic Voyages`, `Key Items` and `Essences` pages into `data/stars_guide.json`, along with the six
icons the page shows. The **Nova damage table is parsed out of that wikitext** rather than typed
into the generator, so it cannot drift from its source; recipes, stations and the fight order come
from the same datasets as the rest of the site, and the page links to every wiki page it used.

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

### The vanilla wiki is a version ahead

terraria.wiki.gg documents current desktop Terraria. tModLoader is a separate build that lags it,
and this pack is **tModLoader 1.4.4** — so every vanilla item added in 1.4.5 is on the wiki, gets
scraped, and gets recommended for a game you cannot launch. Ninety-one such picks were reaching the
loadout panels across every class, including the whole whip tag-slot accessory chain (Twilight
Grasp, Wicked Armlet, Wicked Claws, Armlet Of Ruin, Druidic Serpent Cloak, Silver Shield) and the
Ruinous Staff, all introduced in 1.4.5.7.

`pipeline/version_gate.py` holds the 1.4.5.7 item list and the target `GAME_VERSION`, and drops
those picks. Only vanilla entries are gated — a mod shipping its own item under a name the vanilla
wiki also uses is real. If tModLoader ships a 1.4.5 build, change `GAME_VERSION` and the gate opens.

Worth knowing: **whip stacking still works in 1.4.4.** Tags from different whips stack natively —
that is what 1.4.5.0 removed and 1.4.5.7 handed back through those accessories. The summoner build
is intact; the accessories simply are not there.

### Half the evil-biome loot is not in this world

The world is **Corruption** (Large, Expert — per the Covenant Route install reference). The wikis
document both evils side by side, the scrape keeps both, and the loadouts recommended both. No
Crimson biome generates here, breaking altars in Hardmode spreads Corruption and Hallow rather than
Crimson, and there is no cross-world route to Crimtane, Tissue Sample, Vertebra or Ichor.

`pipeline/world_gate.py` drops the 24 Crimson-locked picks that were reaching the panels. Four of
them were tagged **Best**: Fetid Baghnakhs and Vampire Knives for Melee, Life Drain for Magic, and
**Flask of Ichor** for both Summoner and Melee at five checkpoints each — Ichor drops only from
Ichor Stickers in the Underground Crimson and from Hematic Crates fished in Crimson water. Flask of
Cursed Flames is the Corruption equivalent and inherits the tag where it is listed.

Set `WORLD_EVIL = "crimson"` to flip the gate to the Corruption-locked list instead.

### Known gap: Fargo's Souls

The item database holds 497 Fargo's items, and **two** of them reach a loadout panel. Fargo's Souls
is the pack's difficulty layer — Eternity Mode rewrites every vanilla boss — and Fargo's Mutant Mod
supplies the boss summons, so the loadouts are quietest about the mod that changes the fights most.
Fargo's publishes no class-setup guide for `parse_guides.py` to read, which is why. Its gear has to
be found on the boss pages: the Banished Baron's Decrepit Airstrike Remote, for one, is a 375-damage
summon weapon that appears nowhere on this site.

### Hand-verified corrections

`pipeline/corrections.py` fixes what the scrape got wrong, each one checked against the mod's own
wiki page with the source named in the file:

| Fix | Was | Source |
|---|---|---|
| The Blender | 340 Melee — topped every pre-mechanical melee ranking | 12 Radiant, a pre-Hardmode Healer scythe |
| Ballista / Explosive Trap rods and canes | knockback, velocity, use and tip all scraped the item id (3824, 3832); speed read "Snail" | fields dropped, damage and type kept |
| Pain Monger's armor | listed for Summoner | every piece is magic damage, crit or mana |
| Phantom In The Mirror | Pre-Mechanical | Dioskouroi unlocks it pre-Hardmode, but the recipe needs a Shroomite Bar, The Horseman's Blade and a Christmas Tree Sword — Ectoplasm gates it to post-Plantera |
| Lich | order 33, ahead of The Twins | cannot be summoned until all three mechanical bosses are down |

The corrections are idempotent, and they patch both the `pipeline/` working copy and the committed
`data/` copy — the generators resolve to `pipeline/` first, so a fix applied to only one is a fix
the page never sees.

## Repository layout

```
index.html bosses.html loadouts.html recipes.html tinkerers.html   the wiki
data/         merged datasets (bosses, recipes, items, Hardmode verdicts, loadouts,
              and the Stars Above guide the home page's explainer is built from)
pipeline/     the scripts that build it from the source wikis
_preserved/   the first Tinkerer's-only build, kept for reference
```

Every generator writes its page into the repository root. The JSON caches under `pipeline/` are
regenerable intermediates and are not committed; the merged datasets in `data/` are.

## Rebuilding

Python 3, standard library only. From inside `pipeline/`:

Fetch and parse, in this order:

```bash
# bosses -> bosses.json, boss_sprites.json
python3 boss_fetch.py       # each wiki's Bosses page, its categories, and every boss page
python3 bosses.py --write   # merge the progression charts into one order
python3 boss_sprites.py     # a sprite for every boss

# recipes and items -> full_site_data.json, full_index.json, full_sprites.json
python3 full_fetch.py       # every Recipes/<Station> page across the seven wikis
python3 full_items.py       # parse stations, then batch-fetch item wikitext
python3 full_sprites.py     # download and base64-encode every sprite
python3 full_entities.py    # resolve drop-source NPCs
python3 full_cats2.py       # categories for items with no direct Hardmode signal
python3 full_data.py        # merge, index, classify Hardmode

# the Stars Above explainer on the home page -> ../data/stars_guide.json
python3 stars_guide.py      # its own Early Guide, plus the six icons that page uses

# loadouts -> loadouts.json, loadout_sprites.json, loadout_stats.json
python3 loadouts.py         # parse the class-setup guides onto one timeline
python3 loadout_sprites.py
python3 loadout_stats_fetch.py   # item pages behind the hover stat card
python3 loadout_stats.py         # -> loadout_stats.json, required by loadout_gen.py

# the Tinkerer's-only dataset the v1 page still uses
python3 parse.py            # -> recipes_raw.json
python3 items.py            # -> items.json
python3 sprites.py          # -> sprites.json
python3 hm_cats.py          # -> item_categories.json
python3 hardmode.py         # -> hardmode.json
python3 build_data.py       # -> site_data.json
```

Then apply the hand-verified corrections, which must run after the data build and before the
generators:

```bash
python3 corrections.py      # patches loadouts.json, loadout_stats.json, bosses.json in place
```

Then generate the pages, which only read the files above:

```bash
python3 full_gen.py         # recipes.html
python3 gen.py              # tinkerers.html
python3 loadout_gen.py      # loadouts.html
python3 boss_gen.py         # bosses.html
python3 stars_gen.py        # stars.html
python3 home_gen.py         # index.html
```

Every fetch stage caches, so a re-run after a parser change costs no requests.

`pipeline/logo.py` holds the site mark — a 16x16 pixel grid rendered to SVG for the nav and to
transparent PNGs for the favicon. It has no fetch step and no output file; the generators import
it directly.

`data/boss_icons.json` is the one committed dataset with no script that regenerates it. The boss
icons on the loadout timeline come from it, and it was recovered from a built page rather than
fetched. Keep it.

## Licence

Recipe and item data belongs to the respective wikis, under their own terms (wiki.gg communities are
CC BY-SA unless stated otherwise). Item sprites are © Re-Logic and the respective mod authors, used
here for reference. A fan reference tool, not affiliated with Re-Logic or any mod team.
