import json, os, html
BASE = os.path.dirname(os.path.abspath(__file__))
from gen_css import CSS as BASECSS
import site_common as SC

D = json.load(open(os.path.join(BASE, "full_site_data.json")))
MODS, ORDER, ST, I, R = D["mods"], D["order"], D["stations"], D["items"], D["recipes"]
MODCOL = {"vanilla":"#6f7794","thorium":"#3f9e8c","fargo":"#c9552f","spirit_reforged":"#7a5cc4",
          "spirit":"#5a80c9","stars":"#c2a1e8","fables":"#c98a24"}

EXTRA = """
<style>
.layout3{display:grid; grid-template-columns:224px minmax(0,1fr) 372px; gap:20px; align-items:start; padding:20px 0 60px}
@media (max-width:1300px){ .layout3{grid-template-columns:200px minmax(0,1fr)} .detail{grid-column:1/-1} }
@media (max-width:900px){ .layout3{grid-template-columns:minmax(0,1fr)} .stationnav{max-height:220px} }
.stationnav{position:sticky; top:64px; max-height:calc(100vh - 84px); overflow-y:auto;
  background:var(--surface); border:1px solid var(--line); border-radius:var(--radius); box-shadow:var(--shadow)}
.snav-h{padding:9px 12px; border-bottom:1px solid var(--line); background:var(--surface-2);
  font-family:"Pixelify Sans",sans-serif; font-size:10px; letter-spacing:.1em; text-transform:uppercase; color:var(--ink-3)}
.snav-mod{padding:7px 12px 3px; font-family:"Pixelify Sans",sans-serif; font-size:10.5px;
  letter-spacing:.07em; text-transform:uppercase; color:var(--ink-2); display:flex; align-items:center; gap:6px}
.snav-mod .sw{width:8px;height:8px;border-radius:2px;flex:none}
button.snav{display:flex; width:100%; align-items:center; gap:7px; text-align:left; font:inherit;
  font-size:12.5px; background:none; border:0; padding:4px 12px; color:var(--ink-2); cursor:pointer; border-left:3px solid transparent}
button.snav:hover{background:var(--surface-2); color:var(--ink)}
button.snav[aria-current="true"]{background:var(--brass-soft); color:var(--brass); border-left-color:var(--brass); font-weight:600}
button.snav .c{margin-left:auto; font-family:"JetBrains Mono",monospace; font-size:10.5px; color:var(--ink-3); font-variant-numeric:tabular-nums}
button.snav[aria-current="true"] .c{color:var(--brass)}
.tablehead{display:flex; align-items:center; gap:10px; padding:11px 14px; border-bottom:1px solid var(--line);
  background:linear-gradient(180deg,var(--surface-2),var(--surface))}
.tablehead h2{margin:0; font-family:"Pixelify Sans",sans-serif; font-size:16px; font-weight:600}
.tablehead .sub{margin-left:auto; font-family:"JetBrains Mono",monospace; font-size:11.5px; color:var(--ink-3)}
.srcpill{font-family:"Pixelify Sans",sans-serif; font-size:9.5px; letter-spacing:.05em; text-transform:uppercase;
  padding:2px 7px; border-radius:100px; color:#fff}
.more{padding:12px 14px; text-align:center; font-size:12.5px; color:var(--ink-3); border-top:1px solid var(--line)}
.more button{font:inherit; font-size:12.5px; background:var(--surface-2); border:1px solid var(--line-strong);
  border-radius:var(--radius); padding:6px 14px; cursor:pointer; color:var(--ink)}
.more button:hover{border-color:var(--brass); color:var(--brass)}
.stat-line{font-family:"JetBrains Mono",monospace; font-size:11px; color:var(--ink-3)}
</style>
"""

def chips():
    per = {m: sum(1 for r in R if r["m"] == m) for m in ORDER}
    out = []
    for m in ORDER:
        if not per.get(m): continue
        out.append('<button class="chip" type="button" data-src="%s" aria-pressed="true">'
                   '<span class="swatch" style="width:8px;height:8px;border-radius:2px;display:inline-block;background:%s"></span>'
                   '%s<span class="n">%d</span></button>' % (m, MODCOL[m], html.escape(MODS[m]["short"]), per[m]))
    return "".join(out)

npre  = sum(1 for r in R if r["phm"] is True)
nhard = sum(1 for r in R if r["phm"] is False)
nmod  = sum(1 for v in I.values() if v["own"] != "vanilla")

payload = json.dumps(D, separators=(",", ":")).replace("<", "\\u003c")

HTML = '<meta charset="utf-8">\n' + BASECSS + SC.NAV_CSS + EXTRA + SC.nav("recipes.html", "all stations") + """
<header class="masthead"><div class="wrap mast-in">
  <div class="brandline"><div>
    <p class="eyebrow">Terraria &middot; tModLoader 1.4.4 &middot; Covenant Route</p>
    <h1>Joseph's Modpack Wiki</h1>
    <p class="tagline">Every crafting recipe the pack adds, across <b>%(nst)d stations</b> and six mods &mdash;
    Thorium, Fargo's Souls, Spirit Reforged, Spirit Classic, The Stars Above and Calamity Fables,
    plus the vanilla Tinkerer's Workshop. Click any item for how to get it.</p>
  </div></div>
  <dl class="meta">
    <div><dt>Recipes</dt><dd>%(nrec)d</dd></div>
    <div><dt>Items</dt><dd>%(nitem)d</dd></div>
    <div><dt>Modded items</dt><dd>%(nmod)d</dd></div>
    <div><dt>Pre-Hardmode</dt><dd>%(npre)d</dd></div>
    <div><dt>Hardmode only</dt><dd>%(nhard)d</dd></div>
  </dl>
</div></header>

<div class="controls"><div class="wrap ctl-in">
  <div class="search">
    <input id="q" type="search" placeholder="Search every item in the pack" autocomplete="off" aria-label="Search items">
    <button class="clearx" id="clearq" type="button" aria-label="Clear search">&times;</button>
  </div>
  <div class="chips">%(chips)s</div>
  <span class="chipsep" aria-hidden="true"></span>
  <div class="chips">
    <button class="chip phmchip" type="button" data-era="pre" aria-pressed="true">Pre-Hardmode<span class="n">%(npre)d</span></button>
    <button class="chip hmchip" type="button" data-era="hard" aria-pressed="true">Hardmode<span class="n">%(nhard)d</span></button>
  </div>
  <span class="spacer"></span>
  <span class="count" id="count"></span>
</div></div>

<main class="wrap layout3">
  <nav class="stationnav" id="snav"><div class="snav-h">Crafting stations</div></nav>
  <section class="tablecard">
    <div class="tablehead"><h2 id="sttitle">All recipes</h2><span class="sub" id="stsub"></span></div>
    <div class="tscroll">
      <table class="crafts">
        <thead><tr><th class="c-res">Result</th><th>Ingredients</th></tr></thead>
        <tbody id="tbody"></tbody>
      </table>
    </div>
    <div class="more" id="more" hidden></div>
  </section>
  <aside class="detail" id="detail"></aside>
</main>

<footer><div class="wrap fgrid">
  <div><h4>Scope</h4>
    <p>Every recipe the six content mods add, at all %(nst)d stations they use, plus the vanilla
    Tinkerer's Workshop because it is where mod and vanilla accessories meet. Vanilla's other
    3,944 recipes are not duplicated here &mdash; terraria.wiki.gg already covers them.</p></div>
  <div><h4>Where this came from</h4>
    <p>Parsed from each wiki's own generated <code>Recipes/&lt;Station&gt;</code> tables through the
    MediaWiki API &mdash; 161 station pages across seven wikis. Item descriptions, drop rates and
    prices come from the raw wikitext of each item page.</p></div>
  <div><h4>Pre-Hardmode verdicts</h4>
    <p>Each item is classified from the wikis' <code>tags</code> field, the Hardmode-only category,
    mod infobox flags, lead wording, drop-source NPCs, and recipe propagation to a fixed point.
    Items with no Hardmode evidence anywhere are treated as pre-Hardmode, which is these wikis'
    tagging convention; each card shows the basis used.</p></div>
</div></footer>

<script id="dataset" type="application/json">%(payload)s</script>
""" % {"nrec": len(R), "nitem": len(I), "nmod": nmod, "npre": npre, "nhard": nhard,
       "nst": len(ST), "chips": chips(), "payload": payload}

HTML = HTML.replace("<title>Joseph's Modpack Wiki</title>", "<title>All Recipes</title>", 1)
js = open(os.path.join(BASE, "full_wiki_js.html"), encoding="utf-8").read()
open(os.path.join(BASE, "recipes.html"), "w", encoding="utf-8").write(HTML + js)
print("wrote recipes.html %.1f MB" % (os.path.getsize(os.path.join(BASE,"recipes.html"))/1048576))
