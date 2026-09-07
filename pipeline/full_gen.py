import json, os, html
BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
from gen_css import CSS as BASECSS
import site_common as SC

D = json.load(open(os.path.join(BASE, "full_site_data.json")))
MODS, ORDER, ST, I, R = D["mods"], D["order"], D["stations"], D["items"], D["recipes"]
MODCOL = SC.MODCOL

EXTRA = """
<style>
.layout3{display:grid; grid-template-columns:minmax(0,1fr) 352px; gap:16px; align-items:start;
  padding:14px 0 56px}
@media (max-width:980px){
  .layout3{grid-template-columns:minmax(0,1fr)}
  .detail{position:static; max-height:none}
  /* one column: results come first, but once you pick an item its card moves above them
     rather than sitting 13,000px below a 250-row table */
  .layout3.picked .detail{order:-1}
}
/* denser rows: the same information, less air */
.layout3 table.crafts td{padding:7px 14px}
.layout3 .it .sp{width:30px; height:30px}
.layout3 .it .sp img{max-width:23px; max-height:23px}
.layout3 ul.ing{gap:2px 4px}
.masthead.slim .tagline .dim{color:var(--ink-3)}
/* the station picker, now a select rather than a 200px column of 130 buttons */
.stationpick{display:flex; align-items:center; gap:7px}
.stationpick select{font:inherit; font-size:12.5px; max-width:270px; padding:5px 9px;
  border-radius:100px; border:1px solid var(--line-strong); background:var(--surface);
  color:var(--ink); cursor:pointer}
.stationpick select:hover{border-color:var(--brass)}
.stationpick .lbl{font-family:"Pixelify Sans",sans-serif; font-size:9.5px; letter-spacing:.09em;
  text-transform:uppercase; color:var(--ink-3)}
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

TPL = """
<header class="masthead slim"><div class="wrap mast-in">
  <div class="brandline"><div>
    <h1>All Recipes</h1>
    <p class="tagline">Search any item, or pick a station. Click a result for how to get it.
    <span class="dim">%(nrec)d recipes &middot; %(nitem)d items &middot; %(nst)d stations.</span></p>
  </div></div>
</div></header>

<div class="controls"><div class="wrap ctl-in">
  <div class="search">
    <input id="q" type="search" placeholder="Search every item in the pack" autocomplete="off" aria-label="Search items">
    <button class="clearx" id="clearq" type="button" aria-label="Clear search">&times;</button>
  </div>
  <div class="stationpick">
    <span class="lbl">Station</span>
    <select id="stationsel" aria-label="Filter by crafting station"></select>
  </div>
  <span class="chipsep" aria-hidden="true"></span>
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
  <div><h2 class="fh">Scope</h2>
    <p>Every recipe the six content mods add, at all %(nst)d stations they use, plus the vanilla
    Tinkerer's Workshop because it is where mod and vanilla accessories meet. Vanilla's other
    3,944 recipes are not duplicated here &mdash; terraria.wiki.gg already covers them.</p></div>
  <div><h2 class="fh">Where this came from</h2>
    <p>Parsed from each wiki's own generated <code>Recipes/&lt;Station&gt;</code> tables through the
    MediaWiki API &mdash; 161 station pages across seven wikis. Item descriptions, drop rates and
    prices come from the raw wikitext of each item page.</p></div>
  <div><h2 class="fh">Pre-Hardmode verdicts</h2>
    <p>Each item is classified from the wikis' <code>tags</code> field, the Hardmode-only category,
    mod infobox flags, lead wording, drop-source NPCs, and recipe propagation to a fixed point.
    Items with no Hardmode evidence anywhere are treated as pre-Hardmode, which is these wikis'
    tagging convention; each card shows the basis used.</p></div>
</div></footer>

<script id="dataset" type="application/json">%(payload)s</script>
"""

# the % formatting binds to the template alone -- the shared CSS is full of "100%"
BODY = TPL % {"nrec": len(R), "nitem": len(I), "nmod": nmod, "npre": npre, "nhard": nhard,
              "nst": len(ST), "chips": chips(), "payload": payload}
HTML = (SC.head('recipes.html', 'All Recipes', 'Every crafting recipe the six mods add, across all 130 stations, with how to get each item and whether you can make it before Hardmode.') + BASECSS + SC.NAV_CSS + SC.PROGRESS_CSS + EXTRA
        + SC.nav("recipes.html", "{:,} recipes".format(len(R))) + SC.runbar() + BODY)

HTML = HTML.replace("<title>Joseph's Modpack Wiki</title>", "<title>All Recipes</title>", 1)
js = open(os.path.join(BASE, "full_wiki_js.html"), encoding="utf-8").read()
assert "@@MODCOL@@" in js, "full_wiki_js.html lost its palette placeholder"
js = js.replace("@@MODCOL@@", SC.modcol_js())
out = os.path.join(ROOT, "recipes.html")
open(out, "w", encoding="utf-8").write(HTML + SC.progress_js("recipes.html") + js)
print("wrote recipes.html %.1f MB" % (os.path.getsize(out)/1048576))
