import json, os, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_css import CSS
from gen_js import JS
import site_common as SC

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
D = json.load(open(os.path.join(BASE, "site_data.json")))
sprites = json.load(open(os.path.join(BASE, "sprites.json")))

# merge the Hardmode verdicts computed by hardmode.py
HM = json.load(open(os.path.join(BASE, "hardmode.json")))
for k, v in D["items"].items():
    v.pop("_ikey", None)
    v["phm"] = HM["verdict"].get(k)
    v["pw"]  = HM["why"].get(k)
for i, r in enumerate(D["recipes"]):
    st = HM["recipes"][i]
    r["phm"] = st["phm"]
    r["blk"] = st["blockers"][:4]

# attach sprite for the station
STATION = sprites.get("__station__", "")

MODCOL = {"vanilla":"#6f7794","thorium":"#3f9e8c","fargo":"#c9552f",
          "spirit_reforged":"#7a5cc4","spirit":"#5a80c9","fables":"#c98a24"}

I, R, MODS, ORDER = D["items"], D["recipes"], D["mods"], D["order"]
per = {m: sum(1 for r in R if r["src"] == m) for m in ORDER}
n_changed = sum(1 for r in R if r.get("chg"))
n_mod_items = sum(1 for v in I.values() if v["own"] != "vanilla")
n_pre = sum(1 for r in D["recipes"] if r["phm"] is True)
n_hard = sum(1 for r in D["recipes"] if r["phm"] is False)

initial = None
for k, v in I.items():
    if v["n"] == "Terraspark Boots": initial = int(k); break
if initial is None: initial = int(next(iter(I)))

# JS fix: tree root
js = JS.replace(
  '      var root=el("ul","tree"); root.appendChild(treeFor(ri,0,[id]));\n      g.appendChild(root.firstChild ? root : root);',
  '      var root=treeFor(ri,0,[id]); root.className="tree";\n      g.appendChild(root);')
assert 'root.className="tree"' in js

payload = json.dumps(D, separators=(",", ":")).replace("<", "\\u003c").replace("\u2028"," ").replace("\u2029"," ")

chips = []
for m in ORDER:
    chips.append(
      '<button class="chip" type="button" data-src="%s" aria-pressed="true">'
      '<span class="swatch" style="width:8px;height:8px;border-radius:2px;display:inline-block;background:%s"></span>'
      '%s<span class="n">%d</span></button>' % (m, MODCOL[m], html.escape(MODS[m]["short"]), per[m]))

changed_list = "".join(
  "<li><b>%s</b> — %s</li>" % (html.escape(n), ", ".join(MODS[s]["short"] for s in v))
  for n, v in sorted(D["changed"].items()))

HTML = ('<meta charset="utf-8">\n' + CSS + SC.NAV_CSS + SC.PROGRESS_CSS
        + SC.nav("tinkerers.html", "accessory combinations") + SC.runbar() + """
<header class="masthead"><div class="wrap mast-in">
  <div class="brandline">
    <div>
      <p class="eyebrow">Terraria &middot; tModLoader 1.4.4 &middot; Covenant Route</p>
      <h1>Tinkerer's Workshop</h1>
      <p class="tagline">Every accessory combination in the pack, <b>modded and vanilla together</b> — Thorium, Fargo's Souls, Spirit Reforged, Spirit Classic and Calamity Fables alongside base Terraria. Click any item for how to get it.</p>
    </div>
  </div>
  <dl class="meta">
    <div><dt>Combinations</dt><dd>%(nrec)d</dd></div>
    <div><dt>Items</dt><dd>%(nitem)d</dd></div>
    <div><dt>Modded items</dt><dd>%(nmod)d</dd></div>
    <div><dt>Pre-Hardmode</dt><dd>%(npre)d</dd></div>
    <div><dt>Hardmode only</dt><dd>%(nhard)d</dd></div>
  </dl>
</div></header>

<div class="controls"><div class="wrap ctl-in">
  <div class="search">
    <input id="q" type="search" placeholder="Search any item — result or ingredient" autocomplete="off" aria-label="Search items">
    <button class="clearx" id="clearq" type="button" aria-label="Clear search">&times;</button>
  </div>
  <div class="chips">%(chips)s</div>
  <span class="chipsep" aria-hidden="true"></span>
  <div class="chips">
    <button class="chip phmchip" type="button" data-era="pre" aria-pressed="true">Pre-Hardmode<span class="n">%(npre)d</span></button>
    <button class="chip hmchip" type="button" data-era="hard" aria-pressed="true">Hardmode<span class="n">%(nhard)d</span></button>
  </div>
  <button class="chip flagchip" id="chgtoggle" type="button" aria-pressed="false">Only mod-changed<span class="n">%(nchg)d</span></button>
  <span class="spacer"></span>
  <span class="count" id="count"></span>
</div></div>

<main class="wrap layout">
  <section class="tablecard">
    <div class="sectionbar">
      <div class="sbsp"><img src="%(station)s" class="px" alt=""></div>
      <h2>Tinkerer's Workshop</h2>
      <span class="sbnote">%(nrec)d combinations &middot; %(nmodrec)d added or changed by mods</span>
    </div>
    <div class="tscroll">
      <table class="crafts">
        <thead><tr><th class="c-res">Result</th><th>Ingredients</th></tr></thead>
        <tbody id="tbody"></tbody>
      </table>
    </div>
  </section>
  <aside class="detail" id="detail"></aside>
</main>

<footer><div class="wrap fgrid">
  <div>
    <h4>Where this came from</h4>
    <p>Recipes were read straight off each mod's own <code>Recipes/Tinkerer's Workshop</code> page and parsed, not written from memory — terraria.wiki.gg, thoriummod.wiki.gg, fargosmods.wiki.gg, spiritmod.wiki.gg and calamityfables.wiki.gg, on 5 September 2026. Item descriptions, drop rates and prices come from the same wikis' item pages.</p>
  </div>
  <div>
    <h4>Recipes the mods change</h4>
    <p>Where a mod redefines a vanilla combination, the mod's version is what the game uses. The vanilla row is kept so you can see what moved.</p>
    <ul>%(changed)s</ul>
  </div>
  <div>
    <h4>Not covered</h4>
    <p class="note-warn"><b>The Stars Above</b> adds no Tinkerer's Workshop recipes at all — its stations are the Iron Anvil, Celestriad Root, Loom and Work Bench. Nothing is missing from this table on its account.</p>
    <p>Spirit Reforged and Spirit Classic are listed separately because they are separate wikis with separate content; the pack runs Reforged, with Classic added last.</p>
  </div>
</div></footer>

<script id="dataset" type="application/json">%(payload)s</script>
<script>window.__INITIAL__=%(initial)d;</script>
""" % {"station": STATION, "nrec": len(R), "nitem": len(I), "nmod": n_mod_items,
       "nchg": n_changed, "chips": "".join(chips), "changed": changed_list,
       "nmodrec": sum(1 for r in R if r["src"] != "vanilla"),
       "npre": n_pre, "nhard": n_hard,
       "payload": payload, "initial": initial}) + js

out = os.path.join(ROOT, "tinkerers.html")
HTML = HTML.replace("<title>Joseph's Modpack Wiki</title>", "<title>Tinkerer's Workshop</title>", 1)
open(out, "w", encoding="utf-8").write(HTML + SC.progress_js("tinkerers.html"))
print("wrote %s — %.0f KB" % (out, os.path.getsize(out)/1024))
print("initial item id:", initial, I[str(initial)]["n"])
print("chips:", per, "| changed rows:", n_changed)
