"""stars.html -- The Stars Above, explained.

Five of the six mods add things to make and fight. This one also adds a companion, a menu
bound to an item, and four screens behind it, and none of that is discoverable from a recipe
list. So it gets a page that answers the same four questions about every part of it:

    what it does . why you want it . how you get it . when in the run you get it

The prose is a plain-English summary. Everything factual under it is either read out of the
same datasets the rest of the site is built from (recipes, stations, the boss order), or
parsed from the mod's own wiki pages cached in data/stars_guide.json by stars_guide.py --
including the Stellar Nova damage table, which is read from that wikitext rather than typed
out here, so it cannot drift from its source.
"""
import json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
from gen_css import CSS as BASECSS
import site_common as SC

FULL = json.load(open(os.path.join(BASE, "full_site_data.json")))
IDX  = json.load(open(os.path.join(BASE, "full_index.json")))
SP   = json.load(open(os.path.join(BASE, "full_sprites.json")))
LO   = json.load(open(os.path.join(BASE, "loadouts.json")))
SG   = json.load(open(os.path.join(ROOT, "data", "stars_guide.json"), encoding="utf-8"))
BSP  = json.load(open(os.path.join(BASE, "boss_sprites.json"), encoding="utf-8"))
BOSSES = json.load(open(os.path.join(ROOT, "data", "bosses.json"), encoding="utf-8"))["bosses"]

ITEMS, RECIPES, STATIONS = FULL["items"], FULL["recipes"], FULL["stations"]
ICON = SG.get("icons", {})
SYS  = SG.get("systems", {})
SRC  = SG.get("system_sources", {})
GUIDE_URL = SG.get("source", "")

def article(word):
    """"a Iron Anvil" is the kind of thing a generator says and a person never does."""
    return "an" if word[:1].upper() in "AEIOU" else "a"

def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def item_id(name):
    for k, v in IDX.items():
        if v["name"] == name: return k
    return None

def sprite(name, cls="px"):
    i = item_id(name)
    d = SP.get(i) if i else None
    return ('<img class="%s" src="%s" alt="">' % (cls, d)) if d else ""

def item_url(name):
    i = item_id(name)
    return IDX[i]["url"] if i else None

def recipe_of(name):
    """(ingredients string, station) for the first recipe that makes `name`."""
    i = item_id(name)
    if not i: return None, None
    for r in RECIPES:
        if str(r["res"]) == str(i):
            ing = " + ".join(
                "%d %s" % (g["q"], ITEMS.get(str(g["i"]), {}).get("n", "?"))
                for grp in r["ing"] for g in grp)
            return ing, STATIONS[r["s"]]["name"]
    return None, None

# ---------------------------------------------------------------------------
# The Nova damage table, read out of the mod's own wikitext rather than retyped.
# ---------------------------------------------------------------------------
def nova_scaling():
    t = SYS.get("Stellar Novas", "")
    i = t.find("scales with boss progression")
    if i < 0: return []
    out = []
    for line in t[i:i + 900].splitlines():
        m = re.match(r"\*\s*(.+?):\s*([\d,]+)\s*base damage", line.strip())
        if m:
            label = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", m.group(1)).strip()
            out.append((label, int(m.group(2).replace(",", ""))))
    return out

NOVA = nova_scaling()

STAGE_FULL = {st[0]: st[1] for st in LO["stages"]}
BAND = {"pre": ("Pre-Hardmode", "pre"), "hard": ("Hardmode", "hard"),
        "postml": ("Post-Moon Lord", "hard")}

STARS_BOSSES = sorted((b for b in BOSSES if b.get("mod") == "stars"),
                      key=lambda b: b.get("order", 999))

# ---------------------------------------------------------------------------
def fact(k, v):
    return '<div class="f"><dt>%s</dt><dd>%s</dd></div>' % (k, v)

def when_pill(text, kind="pre"):
    return '<span class="when %s">%s</span>' % (kind, text)

def screen(icon_key, name, what, why, how, when, when_kind, extra=""):
    ic = ('<img class="si" src="%s" alt="">' % ICON[icon_key]) if icon_key in ICON else ""
    return ('<article class="screen">'
            '<header>%s<h3>%s</h3>%s</header>'
            '<p class="what">%s</p>'
            '<dl class="facts">%s%s</dl>%s</article>'
            % (ic, name, when_pill(when, when_kind), what,
               fact("Why you want it", why), fact("How you get it", how), extra))

SCREENS = "".join([
 screen("stellar_array", "Stellar Array",
   "Your loadout of special abilities, and the one place you can change what damage type a "
   "weapon deals.",
   "Abilities are free power you are already carrying. And re-typing an Aspected weapon lets a "
   "weapon you like count as your class &mdash; at <b>&minus;10% damage</b>, which is usually "
   "worth it.",
   "Open the Spatial Disk and click the Array icon. There are <b>24 abilities</b>; you unlock "
   "them by beating bosses, so the list fills up on its own as you play.",
   "Straight away", "pre",
   '<p class="note">You get <b>5 points</b> to spend: a tier&nbsp;1 ability costs 1, tier&nbsp;2 '
   'costs 2, tier&nbsp;3 costs 3. Equip any mix that fits. Wearing the '
   '<b>Attire of the Faerie Voyager</b> raises the budget to 6.</p>'),

 screen("stellar_nova", "Stellar Nova",
   "A big activated attack your Starfarer fires for you, on <b>Z</b>.",
   "It is the strongest thing you own for most of the run, it costs no mana or ammo, and its "
   "damage climbs by itself &mdash; see the table below.",
   "Unlocked by beating <b>The Vagrant of Space and Time</b>, the mod's first boss. After that, "
   "pick which Nova is equipped from the disk. <b>Stellar Prisms</b> tweak what it does.",
   "After the Vagrant", "pre",
   '<p class="note">It fires only on a full gauge: combat fills it at about <b>1 per second</b>, '
   'and Starlight dropped by enemies adds <b>5</b> at a time.</p>'),

 screen("voyage", "Astrolabe",
   "Travel. Opens the Celestial Cartography map and drops you into subworlds &mdash; small "
   "mini-dungeons built around gathering.",
   "It is where the mod's materials come from, <b>Prismatic Core</b> especially, which most of "
   "its gear is crafted with.",
   "Talk to your Starfarer once <b>King Slime</b> is dead. The first destination needs nothing; "
   "everything past it needs a <b>Stellaglyph</b>, and better ones need a higher tier.",
   "After King Slime", "pre",
   '<p class="note warn">Inside a subworld you cannot use wings, mounts or explosives, and you '
   'cannot touch blocks. Subworlds also do not work in multiplayer.</p>'),

 screen("archive", "Archive",
   "A log of every message you have been sent, and a box that hands back specific items.",
   "It is your undo button. Sold, lost or used something you needed &mdash; an Essence, a "
   "Mnemonic Trace, a boss summon &mdash; and it is recoverable instead of gone.",
   "Sits in the same disk menu from the start. Nothing to unlock.",
   "Straight away", "pre"),
])

# ---- the two things you do first -------------------------------------------
disk_ing, disk_st = recipe_of("Spatial Disk")
disk_tt = ITEMS.get(item_id("Spatial Disk"), {}).get("tt", "")

def twin(icon_key, name, aspect):
    ic = ('<img src="%s" alt="">' % ICON[icon_key]) if icon_key in ICON else ""
    return ('<div class="twin">%s<div><b>%s</b><span>%s weapons</span></div></div>'
            % (ic, name, aspect))

# ---- the Nova damage table -------------------------------------------------
nmax = max((v for _, v in NOVA), default=1)
novarows = "".join(
  '<tr><th scope="row">%s</th><td class="bar"><i style="width:%.1f%%"></i></td>'
  '<td class="n">%s</td></tr>' % (esc(label), val / nmax * 100, "{:,}".format(val))
  for label, val in NOVA)

# ---- bosses ----------------------------------------------------------------
def boss_row(b):
    band, kind = BAND.get(b.get("band"), (b.get("band", ""), "pre"))
    sp = ('<img class="px" src="%s" alt="">' % BSP[b["name"]]) if b["name"] in BSP else ""
    bits = []
    if b.get("summon"): bits.append(esc(b["summon"]))
    if b.get("life"):   bits.append(esc(b["life"]) + " hp")
    return ('<li><a href="loadouts.html#%s"><span class="sp">%s</span><span class="tx">'
            '<span class="nm">%s</span><span class="sub">%s</span>'
            '<span class="sub dim">%s</span></span>'
            '<span class="when %s">%s</span></a></li>'
            % (b.get("stage", ""), sp, esc(b["name"]),
               "gear at " + esc(STAGE_FULL.get(b.get("stage"), "")),
               " &middot; ".join(bits) or "&nbsp;", kind, band))

BOSSROWS = "".join(boss_row(b) for b in STARS_BOSSES)

# ---- the collectables ------------------------------------------------------
def collect(name, why):
    ing, st = recipe_of(name)
    u = item_url(name)
    title = ('<a href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (u, esc(name))) \
            if u else esc(name)
    made = ('<span class="mk">%s <em>at %s</em></span>' % (ing, esc(st))) if ing else \
           '<span class="mk dim">not crafted &mdash; found out there</span>'
    hm = ITEMS.get(item_id(name), {}).get("phm")
    pill = when_pill("Pre-Hardmode", "pre") if hm else when_pill("Hardmode", "hard")
    return ('<li><span class="sp">%s</span><div class="tx"><span class="nm">%s</span>%s'
            '<span class="why">%s</span></div>%s</li>'
            % (sprite(name), title, made, why, pill))

COLLECT = "".join([
 collect("Stellaglyph (Tier 1)", "Your first travel pad. Unlocks the subworlds beyond the free one."),
 collect("Stellaglyph (Tier 2)", "Opens the next band of subworlds. Built on top of the Tier&nbsp;1."),
 collect("Stellaglyph (Tier 3)", "The last tier &mdash; and yes, it wants 15 Souls of Night and 15 Souls of Light."),
 collect("Prismatic Core", "The mod's main material. Comes out of subworlds, and off enemies once the Vagrant is dead."),
 collect("Attire of the Faerie Voyager", "Worn in the Starfarer slot, it raises your Stellar Array budget from 5 points to 6."),
])

EXTRA = """
<style>
.slede{margin:0 0 18px; color:var(--ink-2); font-size:14.5px; line-height:1.6; max-width:74ch}
.slede b{color:var(--ink); font-weight:600}
.sec2{padding:26px 0 0}
.sec2 > h2{margin:0 0 3px; font-family:"Pixelify Sans",sans-serif; font-size:16px;
  display:flex; align-items:center; gap:10px}
.sec2 > h2::after{content:""; flex:1; height:2px; border-radius:2px;
  background:linear-gradient(90deg, var(--mcol), transparent)}
.sec2 > p.lede{margin:0 0 13px; color:var(--ink-2); font-size:13.5px; max-width:74ch}

/* --mcol is The Stars Above's own colour from MODCOL. Rules, borders and dots only:
   a lilac would not clear 4.5:1 as body text on either ground. */
body{--mcol:#c2a1e8}

.firsttwo{display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:13px;
  align-items:start}
.step{background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
  box-shadow:var(--shadow); border-top:3px solid var(--mcol); padding:15px 16px 14px}
.step .hd{display:flex; align-items:center; gap:11px; margin-bottom:9px}
.step .hd .slot{width:52px; height:52px; flex:none; display:grid; place-items:center;
  background:var(--slot-bg); border:1px solid var(--slot-line); border-radius:6px;
  box-shadow:inset 0 1px 0 var(--slot-in), var(--glow-soft)}
.step .hd .slot img{width:34px; height:34px}
.step h3{margin:0; font-family:"Pixelify Sans",sans-serif; font-size:15px; color:var(--ink)}
.step .tt{margin:1px 0 0; font-size:11.5px; font-style:italic; color:var(--ink-3)}
.step p{margin:0 0 8px; font-size:13px; line-height:1.55; color:var(--ink-2)}
.step p b{color:var(--ink); font-weight:600}
.step p:last-child{margin-bottom:0}
figure.twins{margin:0 0 9px; text-align:center}
figure.twins img{width:100%; max-width:212px; height:auto; margin:0 auto;
  image-rendering:pixelated; image-rendering:crisp-edges}
figure.twins figcaption{margin-top:3px; font-size:11px; color:var(--ink-3)}
.twin{display:flex; align-items:center; gap:9px; padding:7px 10px; border-radius:6px;
  background:var(--surface-2); border:1px solid var(--line); margin-bottom:7px}
.twin img{width:22px; height:22px; flex:none; image-rendering:pixelated}
.twin b{display:block; font-family:"Pixelify Sans",sans-serif; font-size:13px; color:var(--ink)}
.twin span{display:block; font-size:11.5px; color:var(--ink-3)}

.screens{display:grid; grid-template-columns:repeat(auto-fit,minmax(288px,1fr)); gap:13px}
.screen{background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
  padding:14px 16px 15px; display:flex; flex-direction:column; gap:9px}
.screen header{display:flex; align-items:center; gap:10px; flex-wrap:wrap}
.screen .si{width:52px; height:35px; object-fit:contain; flex:none}
.screen h3{margin:0; font-family:"Pixelify Sans",sans-serif; font-size:14.5px; color:var(--ink)}
.screen p.what{margin:0; font-size:13px; line-height:1.55; color:var(--ink-2)}
.screen p.what b, .screen dd b, .screen .note b{color:var(--ink); font-weight:600}
.screen .facts{margin:0; display:flex; flex-direction:column; gap:8px}
.screen .f dt{font-family:"Pixelify Sans",sans-serif; font-size:9.5px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--ink-3); margin-bottom:2px}
.screen .f dd{margin:0; font-size:12.5px; line-height:1.5; color:var(--ink-2)}
.screen .note{margin:0; font-size:12px; line-height:1.5; color:var(--ink-2);
  background:var(--surface-2); border:1px solid var(--line); border-radius:6px; padding:8px 10px}
.screen .note.warn{border-color:color-mix(in srgb,var(--flag) 45%, var(--line))}
.screen .note.warn b{color:var(--flag)}

.when{font-family:"Pixelify Sans",sans-serif; font-size:9.5px; letter-spacing:.07em;
  text-transform:uppercase; border-radius:100px; padding:2px 9px; white-space:nowrap; flex:none}
.when.pre{color:var(--pre); border:1px solid var(--pre-line); background:var(--pre-soft)}
.when.hard{color:var(--hard); border:1px solid var(--hard-line); background:var(--hard-soft)}
header .when{margin-left:auto}

table.nova{width:100%; border-collapse:collapse; font-size:13px}
table.nova th[scope=row]{text-align:left; font-weight:500; color:var(--ink-2); padding:4px 12px 4px 0;
  white-space:nowrap; font-size:12.5px}
table.nova td.bar{width:100%; padding:4px 0}
table.nova td.bar i{display:block; height:9px; border-radius:5px;
  background:linear-gradient(90deg, color-mix(in srgb,var(--mcol) 55%, var(--brass)), var(--mcol));
  min-width:3px}
table.nova td.n{font-family:"JetBrains Mono",monospace; font-size:12px; color:var(--ink);
  text-align:right; padding:4px 0 4px 12px; white-space:nowrap; font-variant-numeric:tabular-nums}
table.nova tr:last-child td.n{color:var(--brass); font-weight:700}

ol.sbosses{margin:0; padding:0; list-style:none;
  display:grid; grid-template-columns:repeat(auto-fill,minmax(330px,1fr)); gap:8px}
ol.sbosses a{display:flex; align-items:center; gap:10px; text-decoration:none; height:100%;
  background:var(--surface); border:1px solid var(--line); border-left:3px solid var(--mcol);
  border-radius:var(--radius); padding:8px 11px}
ol.sbosses .sp{width:38px; height:38px; flex:none; display:grid; place-items:center;
  background:var(--slot-bg); border:1px solid var(--slot-line); border-radius:5px}
ol.sbosses .sp img{max-width:30px; max-height:30px; width:auto; height:auto}
ol.sbosses .tx{min-width:0; flex:1}
ol.sbosses .nm{display:block; font-family:"Pixelify Sans",sans-serif; font-size:13px;
  color:var(--ink); line-height:1.25; overflow-wrap:anywhere}
ol.sbosses .sub{display:block; font-size:10.5px; color:var(--ink-3); margin-top:1px}
/* no opacity knock-back here: --ink-3 at .85 lands on 4.2:1 against the card */
ol.sbosses .sub.dim{color:var(--ink-3)}

ul.collect{margin:0; padding:0; list-style:none; display:flex; flex-direction:column; gap:8px}
ul.collect li{display:flex; align-items:center; gap:11px;
  background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
  padding:9px 12px}
ul.collect .sp{width:38px; height:38px; flex:none; display:grid; place-items:center;
  background:var(--slot-bg); border:1px solid var(--slot-line); border-radius:5px}
ul.collect .sp img{max-width:30px; max-height:30px; width:auto; height:auto}
ul.collect .tx{min-width:0; flex:1}
ul.collect .nm{font-family:"Pixelify Sans",sans-serif; font-size:13px; color:var(--ink)}
ul.collect .nm a{color:var(--ink); text-decoration:none}
ul.collect .nm a:hover{color:var(--brass); text-decoration:underline}
ul.collect .mk{display:block; font-family:"JetBrains Mono",monospace; font-size:10.5px;
  color:var(--ink-3); margin-top:2px; line-height:1.45}
ul.collect .mk em{font-style:normal; color:var(--ink-3); opacity:.85}
ul.collect .why{display:block; font-size:12px; color:var(--ink-2); margin-top:3px; line-height:1.45}
@media (max-width:640px){ ul.collect li{flex-wrap:wrap} }

p.srcline{margin:16px 0 0; font-size:12px; color:var(--ink-3); line-height:1.55}
@media (prefers-reduced-motion:no-preference){
  .screen,.step,ol.sbosses a,ul.collect li{transition:border-color .14s ease, transform .13s ease}
  .screen:hover,ol.sbosses a:hover,ul.collect li:hover{border-color:var(--mcol); transform:translateY(-1px)}
  .step .hd .slot img{animation:soul-bob 3.8s ease-in-out infinite}
  table.nova td.bar i{transition:width .4s cubic-bezier(.3,.9,.3,1)}
}
</style>
"""

BODY = """
<header class="masthead slim"><div class="wrap mast-in"><div class="brandline"><div>
  <p class="eyebrow">The Stars Above</p>
  <h1><span class="wm-a">A companion,</span> <span class="wm-b">and a menu</span></h1>
  <p class="tagline">The one mod in the pack that adds a <b>system</b> rather than more things to
  make. It is worth ten minutes before you start, because none of it is discoverable from a
  recipe list. <span class="dim">Every part below says what it does, why you want it, how you get
  it, and when.</span></p>
</div></div></div></header>

<main class="wrap">

  <section class="sec2">
    <h2>The two things you do first</h2>
    <p class="lede">Both happen in your opening minutes, before any boss.</p>
    <div class="firsttwo">

      <article class="step">
        <div class="hd"><span class="slot">@@DISK@@</span>
          <div><h3>1 &middot; The Spatial Disk</h3><p class="tt">&ldquo;@@DISKTT@@&rdquo;</p></div>
          @@WHENPRE@@</div>
        <p>The whole mod lives on this one item. <b>Left-click</b> to talk to your companion,
        <b>right-click</b> to open the menu with everything else in it.</p>
        <p><b>How you get it:</b> you are handed one the moment you enter a world. If you lose
        it, it is <b>@@DISKING@@</b> at @@DISKART@@ <b>@@DISKST@@</b>.</p>
      </article>

      <article class="step">
        <div class="hd">
          <div><h3>2 &middot; Pick a twin</h3><p class="tt">Asphodene, or Eridani</p></div>
          @@WHENPRE2@@</div>
        @@PORTRAIT@@
        @@TWINS@@
        <p>Use the disk and both appear; you choose one. The choice is <b>permanent</b> and sets
        which of the mod's weapons you can use &mdash; so pick the one whose gear you like the
        look of, not the one you think is stronger.</p>
        <p class="tt">Gear marked <b>Spatial</b> works whichever twin you picked.</p>
      </article>

    </div>
  </section>

  <section class="sec2">
    <h2>The four screens behind the right-click</h2>
    <p class="lede">This is the entire mod. Two are open from the start; two unlock early.</p>
    <div class="screens">@@SCREENS@@</div>
  </section>

  <section class="sec2">
    <h2>Your Nova gets stronger on its own</h2>
    <p class="lede">You never upgrade the Nova. Its base damage is set by how far through the
    <i>vanilla</i> bosses you are, so it keeps pace with the run for free &mdash; this is why it
    stays worth pressing all game.</p>
    <table class="nova"><tbody>@@NOVA@@</tbody></table>
  </section>

  <section class="sec2">
    <h2>The nine bosses, in the order the pack fights them</h2>
    <p class="lede">Slotted against the vanilla boss each one follows. Click any of them to open
    the equipment panel for that checkpoint; tick them off on the
    <a href="bosses.html">Boss Order</a> and the rest of the wiki follows you along.</p>
    <ol class="sbosses">@@BOSSES@@</ol>
  </section>

  <section class="sec2">
    <h2>What you will be collecting</h2>
    <p class="lede">The few items worth knowing by name. Everything else the mod adds is in
    <a href="recipes.html">All Recipes</a>.</p>
    <ul class="collect">@@COLLECT@@</ul>
    <p class="srcline">@@SRC@@</p>
  </section>

</main>

<footer><div class="wrap fgrid">
  <div><h2 class="fh">Why this page exists</h2>
    <p>The other pages answer &ldquo;what do I make, wear and fight&rdquo;. The Stars Above also
    asks you to understand a menu, and a recipe list cannot teach that.</p></div>
  <div><h2 class="fh">Offline</h2>
    <p>Sprites and icons are embedded like everywhere else on this site, so this page works with
    the Wi-Fi off.</p></div>
  <div><h2 class="fh">Source</h2>
    <p>The Stars Above's own wiki, starsabovemod.wiki.gg. A fan reference tool, not affiliated
    with Re-Logic or any mod team.</p></div>
</div></footer>
"""

srcbits = ", ".join('<a href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (u, esc(p))
                    for p, u in sorted(SRC.items()))
SRCLINE = ('Summarised from The Stars Above\'s own '
           '<a href="%s" target="_blank" rel="noopener noreferrer">Early Guide</a>, plus %s. '
           'The Nova damage figures are read straight out of that wikitext, and the recipes, '
           'stations and fight order come from the same datasets as the rest of this site. '
           'Nothing here is written from memory.' % (GUIDE_URL, srcbits))

PORTRAIT = ('<figure class="twins"><img src="%s" alt="Asphodene and Eridani">'
            '<figcaption>Asphodene, left. Eridani, right.</figcaption></figure>'
            % SG["twins"]) if SG.get("twins") else ""

for a, b in [("@@DISK@@", sprite("Spatial Disk")), ("@@PORTRAIT@@", PORTRAIT),
             ("@@DISKTT@@", esc(disk_tt)), ("@@DISKING@@", disk_ing or "craftable"),
             ("@@DISKST@@", esc(disk_st or "anvil")),
             ("@@DISKART@@", article(disk_st or "anvil")),
             ("@@WHENPRE@@", when_pill("Minute one", "pre")),
             ("@@WHENPRE2@@", when_pill("Minute one", "pre")),
             ("@@TWINS@@", twin("astral", "Asphodene", "Astral") + twin("umbral", "Eridani", "Umbral")),
             ("@@SCREENS@@", SCREENS), ("@@NOVA@@", novarows),
             ("@@BOSSES@@", BOSSROWS), ("@@COLLECT@@", COLLECT), ("@@SRC@@", SRCLINE)]:
    BODY = BODY.replace(a, b)

HTML = (SC.head('stars.html', 'The Stars Above',
                "The one mod in the pack that adds a system rather than content: the Spatial Disk, "
                "the Starfarer you pick, the four screens behind it, and the nine bosses in order "
                "-- what each does, how you get it, and when.")
        + BASECSS + SC.NAV_CSS + SC.PROGRESS_CSS + EXTRA
        + SC.nav("stars.html", "%d bosses &middot; one system" % len(STARS_BOSSES))
        + SC.runbar() + BODY)
out = os.path.join(ROOT, "stars.html")
open(out, "w", encoding="utf-8").write(HTML + SC.progress_js("stars.html"))
print("wrote stars.html %.0f KB | %d screens | %d nova tiers | %d bosses"
      % (os.path.getsize(out) / 1024, 4, len(NOVA), len(STARS_BOSSES)))
