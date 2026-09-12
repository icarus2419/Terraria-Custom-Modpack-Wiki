import json, os, re
BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
from gen_css import CSS as BASECSS
import site_common as SC

FULL = json.load(open(os.path.join(BASE,"full_site_data.json")))
LO   = json.load(open(os.path.join(BASE,"loadouts.json")))
SP   = json.load(open(os.path.join(BASE,"full_sprites.json")))
IDX  = json.load(open(os.path.join(BASE,"full_index.json")))
V1   = json.load(open(os.path.join(BASE,"site_data.json")))

n_rec   = len(FULL["recipes"]); n_items = len(FULL["items"])
n_st    = len(FULL["stations"])
n_mod   = sum(1 for v in FULL["items"].values() if v["own"] != "vanilla")
n_pre   = sum(1 for r in FULL["recipes"] if r["phm"] is True)
n_hard  = sum(1 for r in FULL["recipes"] if r["phm"] is False)
n_tink  = len(V1["recipes"])
n_stage = len(LO["stages"])
n_gear  = sum(len(b["items"]) for s in LO["data"].values() for c in s.values()
              for m in c.values() for b in m)
SHARED  = {"Mixed", "All Classes"}          # class-agnostic gear, not a class you pick
n_cls   = len({c for s in LO["data"].values() for c in s} - SHARED)

def sprite_of(name):
    for k, v in IDX.items():
        if v["name"] == name and k in SP: return SP[k]
    return None
ICONS = {n: sprite_of(n) for n in
         ["Tinkerer's Workshop","Soul Forge","Terraspark Boots","Ankh Shield"]}

SGP = os.path.join(ROOT, "data", "stars_guide.json")
SG  = json.load(open(SGP, encoding="utf-8")) if os.path.exists(SGP) else {"icons": {}, "source": ""}
SICON = SG.get("icons", {})

BOSSES = json.load(open(os.path.join(BASE, "bosses.json"), encoding="utf-8"))["bosses"] \
         if os.path.exists(os.path.join(BASE, "bosses.json")) else \
         json.load(open(os.path.join(os.path.dirname(BASE), "data", "bosses.json"),
                        encoding="utf-8"))["bosses"]
BSP     = json.load(open(os.path.join(BASE, "boss_sprites.json"), encoding="utf-8"))
n_boss  = len(BOSSES)
n_bmod  = sum(1 for b in BOSSES if b["mod"] != "vanilla")

# the card's two figures: bosses from the merged order, abilities from the mod's own
# Stellar Array page, so neither goes stale if the pack or the mod changes
n_sboss = sum(1 for b in json.load(open(os.path.join(ROOT, "data", "bosses.json"),
                                        encoding="utf-8"))["bosses"] if b.get("mod") == "stars")
_m = re.search(r"there are (\d+) abilities", SG.get("systems", {}).get("Stellar Array", ""))
n_sabil = int(_m.group(1)) if _m else 24

MODS = [("Thorium Mod","thorium","#3f9e8c","11 bosses, ~2,600 items, and the Bard, Healer and Thrower classes."),
        ("Fargo's Souls / Mutant","fargo","#c9552f","Eternity Mode rewrites every vanilla boss. Boss summons and re-fights."),
        ("Spirit Reforged","spirit_reforged","#7a5cc4","Biomes, events and atmosphere, built for multiplayer."),
        ("Spirit Classic","spirit","#5a80c9","~12 bosses. Added last, after a clean join test."),
        ("The Stars Above","stars","#c2a1e8","9 bosses, Hardmode to post-Moon Lord. Native Thorium damage support."),
        ("Calamity Fables","fables","#b8518d","A standalone Calamity reimagining. 3 pre-Hardmode bosses.")]
per_mod = {}
for r in FULL["recipes"]: per_mod[r["m"]] = per_mod.get(r["m"], 0) + 1

EXTRA = """
<style>
.hero{padding:46px 0 30px; border-bottom:1px solid var(--line); position:relative; overflow:hidden;
  background:linear-gradient(180deg, color-mix(in srgb,var(--brass-soft) 45%, var(--surface)) 0%, var(--surface) 100%)}
.hero::after{content:""; position:absolute; inset:0; pointer-events:none;
  background-image:repeating-linear-gradient(0deg,transparent 0 3px,var(--grid) 3px 4px),
                   repeating-linear-gradient(90deg,transparent 0 3px,var(--grid) 3px 4px)}
.hero-in{position:relative; z-index:1; max-width:76ch}
.hero .eyebrow{margin:0 0 8px; font-family:"Pixelify Sans",sans-serif; font-size:11px;
  letter-spacing:.14em; text-transform:uppercase; color:var(--brass)}
.hero h1{font-family:"Pixelify Sans",sans-serif; font-weight:600; font-size:clamp(32px,5vw,54px);
  line-height:1; margin:0 0 12px; text-shadow:2px 2px 0 var(--wordshadow)}
.hero p{margin:0; font-size:16px; line-height:1.55; color:var(--ink-2); max-width:62ch}
.hero p b{color:var(--ink); font-weight:600}

.cards{display:grid; grid-template-columns:repeat(auto-fit,minmax(258px,1fr)); gap:16px; padding:26px 0 6px}
a.card{display:flex; flex-direction:column; gap:9px; text-decoration:none; color:inherit;
  background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
  box-shadow:var(--shadow); padding:18px 18px 16px; border-top:3px solid var(--ccol); position:relative}
a.card:hover{border-color:var(--brass-line); border-top-color:var(--ccol); transform:translateY(-2px)}
a.card{transition:transform .12s ease, border-color .12s ease}
@media (prefers-reduced-motion:reduce){ a.card{transition:none} a.card:hover{transform:none} }
a.card .ic{width:44px;height:44px;display:grid;place-items:center;background:var(--slot-bg);
  border:1px solid var(--slot-line); border-radius:5px; box-shadow:inset 0 1px 0 var(--slot-in)}
a.card .ic img{max-width:30px;max-height:30px;width:auto;height:auto}
a.card h2{margin:0; font-family:"Pixelify Sans",sans-serif; font-size:20px; line-height:1.15; color:var(--ink)}
a.card p{margin:0; font-size:13.5px; line-height:1.5; color:var(--ink-2)}
a.card .figs{display:flex; gap:16px; margin-top:auto; padding-top:10px; flex-wrap:wrap}
a.card .figs div{display:flex; flex-direction:column}
a.card .figs dt{font-family:"Pixelify Sans",sans-serif; font-size:9.5px; letter-spacing:.08em;
  text-transform:uppercase; color:var(--ink-3)}
a.card .figs dd{margin:0; font-family:"JetBrains Mono",monospace; font-size:17px; font-weight:700;
  color:var(--ink); font-variant-numeric:tabular-nums}
a.card .go{font-family:"Pixelify Sans",sans-serif; font-size:11.5px; color:var(--brass);
  letter-spacing:.05em}

.sec{padding:30px 0 0}
.sec > h2{margin:0 0 4px; font-family:"Pixelify Sans",sans-serif; font-size:15px; letter-spacing:.02em}
.sec > p.lede{margin:0 0 14px; color:var(--ink-2); font-size:13.5px; max-width:68ch}
.modgrid{display:grid; grid-template-columns:repeat(auto-fill,minmax(250px,1fr)); gap:10px}
.modrow{background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
  padding:11px 13px; border-left:3px solid var(--mcol); display:flex; flex-direction:column; gap:3px}
.modrow .top{display:flex; align-items:baseline; gap:8px}
.modrow h3{margin:0; font-family:"Pixelify Sans",sans-serif; font-size:13.5px; color:var(--ink)}
.modrow .cnt{margin-left:auto; font-family:"JetBrains Mono",monospace; font-size:11.5px; color:var(--ink-3)}
.modrow p{margin:0; font-size:12px; color:var(--ink-2); line-height:1.45}

.quick{display:flex; flex-wrap:wrap; gap:7px; padding-top:4px}
a.qlink{display:inline-flex; align-items:center; gap:7px; text-decoration:none; font-size:12.5px;
  background:var(--surface); border:1px solid var(--line-strong); border-radius:100px;
  padding:5px 13px; color:var(--ink-2)}
a.qlink:hover{border-color:var(--brass); color:var(--brass)}
a.qlink .n{font-family:"JetBrains Mono",monospace; font-size:10.5px; color:var(--ink-3)}
.startbox{background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
  box-shadow:var(--shadow); padding:16px 18px; margin-top:14px}
.startbox ol{margin:0; padding-left:20px; font-size:13.5px; line-height:1.7; color:var(--ink-2)}
.startbox ol b{color:var(--ink)}
.startbox a{font-weight:600}

</style>
"""

def card(href, ccol, icon, title, desc, figs, go):
    f = "".join('<div><dt>%s</dt><dd>%s</dd></div>' % (k, v) for k, v in figs)
    ic = ('<span class="ic"><img class="px" src="%s" alt=""></span>' % icon) if icon else ""
    return ('<a class="card" href="%s" style="--ccol:%s">%s<h2>%s</h2><p>%s</p>'
            '<dl class="figs">%s</dl><span class="go">%s &rarr;</span></a>'
            % (href, ccol, ic, title, desc, f, go))

cards = "".join([
 card("bosses.html", "var(--brass)", BSP.get("Skeletron") or BSP.get("King Slime"),
      "Boss Order",
      "Every boss the pack contains, merged into one fight order and tickable as you go. Tick them "
      "off and the rest of the wiki follows &mdash; it knows which checkpoint you are on.",
      [("Bosses", n_boss), ("Added by mods", n_bmod)], "Open the checklist"),
 card("loadouts.html", "var(--brass)", ICONS.get("Terraspark Boots"),
      "Loadouts",
      "Pick the boss you are about to fight and your class, and get one filled equipment panel: "
      "armour, five <b>accessories</b>, a weapon hotbar, ammo and buffs. Everything else the guides "
      "list sits underneath.",
      [("Checkpoints", n_stage), ("Classes", n_cls)], "Gear up for a boss"),
 card("recipes.html", "var(--brass)", ICONS.get("Soul Forge"),
      "All Recipes",
      "Every recipe the six mods add, across all %d crafting stations. Search any item, filter by "
      "mod, or browse one station at a time." % n_st,
      [("Recipes", "{:,}".format(n_rec)), ("Stations", n_st)], "Browse recipes"),
 card("tinkerers.html", "var(--brass)", ICONS.get("Tinkerer's Workshop"),
      "Tinkerer's Workshop",
      "Every accessory combination in the pack, modded and vanilla side by side. The station where "
      "mod and vanilla gear actually meet.",
      [("Combinations", n_tink), ("Changed by mods", 9)], "Open the workshop"),
 card("stars.html", "var(--brass)", sprite_of("Spatial Disk"),
      "The Stars Above",
      "The one mod that adds a <b>system</b> rather than more things to make: a companion, and a "
      "menu with four screens behind it. What each one does, why you want it, how you get it and "
      "when &mdash; then its nine bosses in order.",
      [("Bosses", n_sboss), ("Abilities", n_sabil)], "Learn the mod"),
])

modrows = "".join(
 '<div class="modrow" style="--mcol:%s"><div class="top"><h3>%s</h3>'
 '<span class="cnt">%s</span></div><p>%s</p></div>'
 % (col, name, "{:,} recipes".format(per_mod.get(key, 0)) if per_mod.get(key) else "&mdash;", desc)
 for name, key, col, desc in MODS)

BODY = """
<div class="hero"><div class="wrap hero-in">
  <p class="eyebrow">Terraria &middot; tModLoader 1.4.4 &middot; Covenant Route</p>
  <h1><span class="wm-a">Joseph's</span> <span class="wm-b">Modpack Wiki</span><span class="wm-rule"></span></h1>
  <p>Everything the pack adds, in one place: <b>@@NREC@@ recipes</b> across <b>@@NST@@ crafting
  stations</b>, <b>@@NITEM@@ items</b> with how to get each one, and a ready equipment panel for
  every class at every boss. Built from the mods' own wikis, and it works offline.</p>
</div></div>

<main class="wrap">
  <div class="cards">@@CARDS@@</div>

  <section class="sec">
    <h2>Start here</h2>
    <p class="lede">If you are not sure where to look:</p>
    <div class="startbox"><ol>
      <li><b>Not sure what to fight next?</b> Open the <a href="bosses.html">Boss Order</a> and tick
      off what you have already killed. Every other page then knows where you are: Loadouts opens on
      your checkpoint, and the recipe pages can hide what you cannot make yet.</li>
      <li><b>About to fight a boss?</b> Go to <a href="loadouts.html">Loadouts</a>, click the boss on
      the timeline, then your class. You get one panel of what to equip &mdash; and each pick says why
      it was chosen. Arrow keys walk the run; the full list is a click below.</li>
      <li><b>Wondering what an item combines into?</b> The
      <a href="tinkerers.html">Tinkerer's Workshop</a> page shows every accessory combination, and
      flags the @@NCHG@@ recipes the mods change from vanilla.</li>
      <li><b>Looking for a specific recipe?</b> <a href="recipes.html">All Recipes</a> searches every
      item in the pack at once, and can filter to what is craftable before Hardmode.</li>
    </ol></div>
  </section>

  <section class="sec">
    <h2>Jump straight to a checkpoint</h2>
    <p class="lede">The boss checkpoints most people look up first. The number is how much gear the
    guides publish there; the page picks one per slot out of it.</p>
    <div class="quick">@@QUICK@@</div>
  </section>

  <section class="sec">
    <h2>What's in the pack</h2>
    <p class="lede">Six content mods, plus the vanilla Tinkerer's Workshop where their accessories meet.</p>
    <div class="modgrid">@@MODS@@</div>
  </section>

  <section class="sec">
    <h2>Before and after Hardmode</h2>
    <p class="lede">Every recipe is checked against the wikis to see whether you can actually make it
    yet. @@NPRE@@ are craftable before Hardmode; @@NHARD@@ need Hardmode content.</p>
  </section>
</main>

<footer><div class="wrap fgrid">
  <div><h2 class="fh">How it was built</h2>
    <p>Recipes are parsed from each wiki's own generated recipe tables through the MediaWiki API &mdash;
    161 station pages across seven wikis. Loadouts come from each wiki's <code>Guide:Class setups</code>.
    Nothing is written from memory.</p></div>
  <div><h2 class="fh">Offline</h2>
    <p>Every page is self-contained with its sprites embedded, so the wiki works with the Wi-Fi off &mdash;
    handy on a second monitor mid-session.</p></div>
  <div><h2 class="fh">Sources</h2>
    <p>terraria.wiki.gg &middot; thoriummod.wiki.gg &middot; fargosmods.wiki.gg &middot;
    spiritmod.wiki.gg &middot; starsabovemod.wiki.gg &middot; calamityfables.wiki.gg.
    A fan reference tool, not affiliated with Re-Logic or any mod team.</p></div>
</div></footer>
"""

quick = "".join('<a class="qlink" href="loadouts.html#%s">%s<span class="n">%d</span></a>'
                % (s[0], s[1], sum(len(b["items"]) for c in LO["data"].get(s[0], {}).values()
                             for m in c.values() for b in m))
                for s in LO["stages"][:7])

# the full label ("Pre-Eater / Brain"), not the short one: a boss's stage is the checkpoint
# you want to be geared at *before* the fight, so "after Eater / Brain" would be backwards
STAGE_FULL = {st[0]: st[1] for st in LO["stages"]}
BAND_NAME   = {"pre": "Pre-Hardmode", "hard": "Hardmode", "postml": "Post-Moon Lord",
               "event": "Event boss", "mini": "Mini-boss", "seed": "Secret seed"}

def _icon(key, cls="ti"):
    d = SICON.get(key)
    return ('<img class="%s" src="%s" alt="">' % (cls, d)) if d else ""

def _inline(key, label):
    """The two permanent choices, named next to their own icon."""
    d = SICON.get(key)
    return ('<span class="pick">%s<b>%s</b></span>'
            % (('<img src="%s" alt="">' % d) if d else "", label))

disk_sp = sprite_of("Spatial Disk") or ""
stars_bosses = sorted((b for b in BOSSES if b.get("mod") == "stars"),
                      key=lambda b: b.get("order", 999))
sboss = "".join(
  '<li><a href="loadouts.html#%s"><span class="sp">%s</span><span class="tx">'
  '<span class="nm">%s</span><span class="at">%s &middot; gear at %s</span></span></a></li>'
  % (b.get("stage", ""),
     ('<img class="px" src="%s" alt="">' % BSP[b["name"]]) if b["name"] in BSP else "",
     b["name"],
     BAND_NAME.get(b.get("band"), b.get("band", "")),
     STAGE_FULL.get(b.get("stage"), b.get("stage", "")))
  for b in stars_bosses)

starsrc = ('The four screens and the twins are summarised from The Stars Above\'s own '
           '<a href="%s" target="_blank" rel="noopener noreferrer">Early Guide</a>; the disk\'s '
           'recipe and the fight order come from the same data as the rest of this site. '
           'Nothing here is written from memory.' % SG.get("source", ""))

for a, b in [("@@NREC@@", "{:,}".format(n_rec)), ("@@NST@@", str(n_st)),
             ("@@NITEM@@", "{:,}".format(n_items)), ("@@CARDS@@", cards),
             ("@@MODS@@", modrows), ("@@NPRE@@", "{:,}".format(n_pre)),
             ("@@NHARD@@", "{:,}".format(n_hard)), ("@@NCHG@@", "9"),
             ("@@QUICK@@", quick),
             ("@@DISKSP@@", disk_sp), ("@@SBOSSES@@", sboss), ("@@STARSRC@@", starsrc),
             ("@@ASTRAL@@", _inline("astral", "Astral")),
             ("@@UMBRAL@@", _inline("umbral", "Umbral")),
             ("@@I_ARRAY@@", _icon("stellar_array")), ("@@I_NOVA@@", _icon("stellar_nova")),
             ("@@I_VOYAGE@@", _icon("voyage")), ("@@I_ARCHIVE@@", _icon("archive"))]:
    BODY = BODY.replace(a, b)

HTML = (SC.head('index.html', "Joseph's Modpack Wiki", 'An offline wiki for a Terraria tModLoader 1.4.4 modpack: 87 bosses in one fight order, 5,455 recipes across 130 stations, and a filled equipment panel for every class at every boss.') + BASECSS + SC.NAV_CSS + SC.PROGRESS_CSS + EXTRA
        + SC.nav("index.html", "offline &middot; " + "{:,}".format(n_rec) + " recipes")
        + SC.runbar() + BODY)
HTML = HTML.replace("<title>Joseph's Modpack Wiki</title>",
                    "<title>Joseph's Modpack Wiki</title>", 1)
out = os.path.join(ROOT, "index.html")
open(out, "w", encoding="utf-8").write(HTML + SC.progress_js("index.html"))
print("wrote index.html %.0f KB" % (os.path.getsize(out)/1024))
