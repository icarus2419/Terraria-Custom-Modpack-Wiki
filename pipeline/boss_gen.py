"""Builds bosses.html -- every boss in the pack, in one fight order, as a checklist."""
import json, os
BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
from gen_css import CSS as BASECSS
import site_common as SC

def load(name):
    for p in (os.path.join(BASE, name), os.path.join(ROOT, "data", name)):
        if os.path.exists(p): return json.load(open(p, encoding="utf-8"))
    raise SystemExit("missing data file: " + name)

D  = load("bosses.json")
SP = load("boss_sprites.json")

MODCOL = SC.MODCOL
BOSSES = D["bosses"]
n_mod  = sum(1 for b in BOSSES if b["mod"] != "vanilla")

payload = json.dumps({"bands":D["bands"], "bosses":BOSSES, "wiki":D["wiki"],
                      "modcol":MODCOL, "sprites":SP},
                     separators=(",", ":")).replace("<", "\\u003c")

EXTRA = """
<style>
.bs-main{padding:18px 0 60px}
.toolbar{position:sticky; top:var(--navh,42px); z-index:50; background:var(--surface);
  border-bottom:1px solid var(--line); box-shadow:0 10px 22px -20px rgba(0,0,0,.8)}
.toolbar-in{display:flex; align-items:center; gap:10px; flex-wrap:wrap; padding:9px 0}
.toolbar .lbl{font-family:"Pixelify Sans",sans-serif; font-size:9.5px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--ink-3)}
button.modchip{display:inline-flex; align-items:center; gap:6px; font:inherit; font-size:12px;
  cursor:pointer; padding:3px 11px; border-radius:100px; color:var(--ink-2);
  background:var(--surface-2); border:1px solid var(--line-strong)}
button.modchip i{width:8px; height:8px; border-radius:50%; background:var(--mcol); flex:none}
button.modchip[aria-pressed="true"]{background:color-mix(in srgb,var(--mcol) 22%, var(--surface));
  border-color:var(--mcol); color:var(--ink); font-weight:600}
button.modchip[aria-pressed="false"]{opacity:.4}
.toolbar .spacer{flex:1}
button.tbtn{font:inherit; font-size:12px; cursor:pointer; padding:4px 12px; border-radius:100px;
  background:var(--surface-2); border:1px solid var(--line-strong); color:var(--ink-2)}
button.tbtn:hover{border-color:var(--brass); color:var(--brass)}
button.tbtn[aria-pressed="true"]{background:var(--brass-soft); border-color:var(--brass); color:var(--brass)}

.summary{display:grid; grid-template-columns:minmax(0,2fr) minmax(0,3fr); gap:14px; margin-bottom:16px}
@media (max-width:820px){ .summary{grid-template-columns:minmax(0,1fr)} }
.card{background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
  box-shadow:var(--shadow); padding:15px 18px}
.card h2{margin:0 0 8px; font-family:"Pixelify Sans",sans-serif; font-size:15px}
.bigprog{display:flex; align-items:baseline; gap:10px; margin-bottom:8px}
.bigprog .n{font-family:"JetBrains Mono",monospace; font-size:32px; font-weight:700; color:var(--ink);
  font-variant-numeric:tabular-nums; line-height:1}
.bigprog .of{font-family:"JetBrains Mono",monospace; font-size:13px; color:var(--ink-3)}
.track{height:8px; border-radius:4px; background:var(--surface-3); overflow:hidden}
.track .fill{height:100%; background:var(--brass); transition:width .18s ease}
.bandbars{display:flex; flex-direction:column; gap:6px; margin-top:11px}
.bandbar{display:grid; grid-template-columns:150px minmax(0,1fr) auto; gap:9px; align-items:center;
  font-size:11.5px; color:var(--ink-2)}
.bandbar .t{height:6px; border-radius:3px; background:var(--surface-3); overflow:hidden}
.bandbar .t i{display:block; height:100%; background:var(--bcol,var(--brass))}
.bandbar .c{font-family:"JetBrains Mono",monospace; font-size:10.5px; color:var(--ink-3)}

.nextup{border-top:3px solid var(--brass)}
.nextup .row{display:flex; align-items:center; gap:14px}
.nextup .sp{width:74px; height:74px; flex:none; display:grid; place-items:center;
  background:var(--slot-bg); border:1px solid var(--brass-line); border-radius:6px;
  box-shadow:inset 0 1px 0 var(--slot-in)}
.nextup .sp img{max-width:60px; max-height:60px; width:auto; height:auto}
.nextup h3{margin:0 0 3px; font-family:"Pixelify Sans",sans-serif; font-size:22px; line-height:1.1}
.nextup h3 a{color:var(--ink); text-decoration:none}
.nextup h3 a:hover{color:var(--brass)}
.nextup p{margin:0 0 3px; font-size:12.5px; color:var(--ink-2)}
.nextup .acts{display:flex; gap:8px; margin-top:9px; flex-wrap:wrap}
.nextup .acts a, .nextup .acts button{font:inherit; font-size:12px; cursor:pointer;
  text-decoration:none; padding:5px 13px; border-radius:100px; border:1px solid var(--brass-line);
  background:var(--brass-soft); color:var(--brass)}
.nextup .acts a:hover, .nextup .acts button:hover{border-color:var(--brass); color:var(--brass-bright)}
.nextup .acts .ghost{background:var(--surface-2); border-color:var(--line-strong); color:var(--ink-2)}

.band{margin-top:22px}
.band > header{display:flex; align-items:baseline; gap:10px; flex-wrap:wrap; margin-bottom:9px;
  padding-bottom:7px; border-bottom:2px solid var(--bcol)}
.band > header h2{margin:0; font-family:"Pixelify Sans",sans-serif; font-size:19px; color:var(--bcol)}
.band > header p{margin:0; font-size:12.5px; color:var(--ink-3)}
.band > header .cnt{margin-left:auto; font-family:"JetBrains Mono",monospace; font-size:11px;
  color:var(--ink-3)}
.list{display:flex; flex-direction:column; gap:5px}
.boss{display:grid; grid-template-columns:auto 52px minmax(0,1fr) auto; gap:12px; align-items:center;
  background:var(--surface); border:1px solid var(--line); border-left:3px solid var(--mcol);
  border-radius:var(--radius); padding:8px 13px 8px 10px; box-shadow:var(--shadow)}
.boss:hover{border-color:var(--brass-line); border-left-color:var(--mcol)}
.boss .tick{width:24px; height:24px; flex:none; border-radius:5px; cursor:pointer; padding:0;
  background:var(--slot-bg); border:2px solid var(--slot-line); display:grid; place-items:center;
  color:transparent; font-size:14px; line-height:1}
.boss .tick:hover{border-color:var(--brass)}
.boss .sp{width:52px; height:52px; display:grid; place-items:center; background:var(--slot-bg);
  border:1px solid var(--slot-line); border-radius:5px; box-shadow:inset 0 1px 0 var(--slot-in)}
.boss .sp img{max-width:42px; max-height:42px; width:auto; height:auto}
.boss .nm{min-width:0}
.boss .nm .top{display:flex; align-items:baseline; gap:8px; flex-wrap:wrap}
/* light mode lifts toward a dark ink, where the neutral Terraria grey has far less room
   than the saturated mods, so it needs to travel further to clear 4.5:1 */
:root[data-theme="light"] .modtag{color:color-mix(in srgb, var(--mcol) 50%, var(--ink))}
.boss .nm a.name{font-family:"Pixelify Sans",sans-serif; font-size:15.5px; color:var(--ink);
  text-decoration:none}
.boss .nm a.name:hover{color:var(--brass)}
.boss .nm .sub{font-size:11.5px; color:var(--ink-3); margin-top:2px; line-height:1.45}
.boss .nm .sub b{color:var(--ink-2); font-weight:600}
.boss .nm .why{font-size:11px; color:var(--ink-3); line-height:1.45; margin-top:3px;
  font-style:italic; max-width:88ch}
.boss .nm .why .howtag{font-family:"Pixelify Sans",sans-serif; font-style:normal; font-size:8.5px;
  letter-spacing:.07em; text-transform:uppercase; color:var(--pre); border:1px solid var(--pre-line);
  border-radius:100px; padding:1px 6px; margin-right:5px}
.boss .nm .why.guessy .howtag{color:var(--ink-3); border-color:var(--line-strong)}
.boss .side{display:flex; align-items:center; gap:8px; flex-wrap:wrap; justify-content:flex-end}
.boss .side a.gear{font-size:11px; text-decoration:none; padding:3px 10px; border-radius:100px;
  border:1px solid var(--line-strong); color:var(--ink-2); white-space:nowrap}
.boss .side a.gear:hover{border-color:var(--brass); color:var(--brass)}
.boss .side .life{font-family:"JetBrains Mono",monospace; font-size:11px; color:var(--ink-3);
  white-space:nowrap}
.modtag{font-family:"Pixelify Sans",sans-serif; font-size:9px; letter-spacing:.07em;
  text-transform:uppercase;
  /* 9px text needs 4.5:1; the raw mod colours sit between 3.8 and 4.4 on this ground, so the
     text is lifted 30% toward the ink while the border keeps the identity colour intact */
  color:color-mix(in srgb, var(--mcol) 70%, var(--ink));
  border:1px solid color-mix(in srgb,var(--mcol) 60%, transparent);
  border-radius:100px; padding:1px 7px; white-space:nowrap}
.boss.done{opacity:.5}
.boss.done .tick{background:var(--brass); border-color:var(--brass); color:var(--surface)}
.boss.done .nm a.name{text-decoration:line-through}
.boss.next{border-color:var(--brass); box-shadow:0 0 0 1px var(--brass-line), var(--shadow)}
.unord{margin:10px 0 5px; font-size:11.5px; color:var(--ink-3); font-style:italic;
  border-top:1px dashed var(--line-strong); padding-top:9px}
.emptyband{font-size:12.5px; color:var(--ink-3); padding:8px 2px}
@media (max-width:700px){
  .toolbar{position:static}
  .boss{grid-template-columns:auto 44px minmax(0,1fr); row-gap:7px}
  .boss .sp{width:44px; height:44px}
  .boss .side{grid-column:1 / -1; justify-content:flex-start}
  .bandbar{grid-template-columns:110px minmax(0,1fr) auto}
}
</style>
"""

BODY = """
<header class="masthead slim"><div class="wrap mast-in">
  <div class="brandline"><div>
    <h1>Boss Checklist</h1>
    <p class="tagline">Every boss in the pack, in one fight order. Tick as you go and the rest of
    the wiki follows.
    <span class="dim">@@NB@@ bosses, @@NM@@ of them from mods &middot;
    <span id="metadone">0</span> beaten.</span></p>
  </div></div>
</div></header>

<div class="toolbar"><div class="wrap toolbar-in">
  <span class="lbl">Show</span>
  <span id="modchips" style="display:flex; gap:6px; flex-wrap:wrap"></span>
  <span class="spacer"></span>
  <button class="tbtn" id="hidedone" type="button" aria-pressed="false">Hide beaten</button>
  <button class="tbtn" id="reset" type="button">Reset ticks</button>
</div></div>

<main class="wrap bs-main">
  <div class="summary">
    <div class="card">
      <h2>Progress</h2>
      <div class="bigprog"><span class="n" id="pdone">0</span>
        <span class="of" id="pof">of @@NB@@ bosses beaten</span></div>
      <div class="track"><div class="fill" id="pfill" style="width:0%"></div></div>
      <div class="bandbars" id="bandbars"></div>
    </div>
    <div class="card nextup" id="nextup"></div>
  </div>
  <!-- height reserved from the known row count so the footer does not jump when the
       list renders; the JS clears it once the real content is in -->
  <div id="bands" style="min-height:@@BANDSMIN@@px"></div>
</main>

<footer><div class="wrap fgrid">
  <div><h2 class="fh">Where the order comes from</h2>
    <p>Thorium, Spirit, The Stars Above and Calamity Fables each publish a boss progression chart on
    their own wiki that already interleaves their bosses with the vanilla ones. Those charts are
    merged here on the vanilla bosses they share &mdash; so &ldquo;after Skeletron&rdquo; is that
    wiki's own placement, not a guess. Vanilla's order is its own Bosses page.</p></div>
  <div><h2 class="fh">Where it does not exist</h2>
    <p>Fargo's Souls publishes no chart &mdash; but its boss pages say in words where each fight
    belongs (<em>&ldquo;intended to be fought before the mechanical bosses&rdquo;</em>), so those
    are placed from their own sentences, quoted on the row. A placement read that way is held to
    the tier its wiki files the boss under, so a post-Moon Lord superboss cannot drift into
    pre-Hardmode. Mini-bosses are the only ones left unordered: no wiki sequences them, and
    guessing would be worse than saying so.</p></div>
  <div><h2 class="fh">Reading a row</h2>
    <p>The colour down the left is the mod that adds the boss. <b>Summoned with</b> is the item you
    need to start the fight, quoted from that wiki. <b>Gear up</b> jumps to the Loadouts checkpoint
    you want to be equipped for. Tick a boss and it greys out; the next unbeaten one is called out
    at the top.</p></div>
</div></footer>

<script id="bossdata" type="application/json">@@PAYLOAD@@</script>
"""

# 81px a row on a desktop, ~128px once rows wrap on a phone, plus a header per band.
# Deliberately reserving for the taller case: over-reserving costs one frame of blank
# space, under-reserving costs the layout shift this exists to prevent.
BANDS_MIN = len(BOSSES) * 128 + len({b["band"] for b in BOSSES}) * 70

for a, b in [("@@NB@@", str(len(BOSSES))), ("@@NM@@", str(n_mod)),
             ("@@BANDSMIN@@", str(BANDS_MIN)), ("@@PAYLOAD@@", payload)]:
    BODY = BODY.replace(a, b)

HTML = (SC.head('bosses.html', 'Boss Checklist', "All 87 bosses the modpack adds, merged into a single fight order from each mod's own progression chart, and tickable as you go.") + BASECSS + SC.NAV_CSS + SC.PROGRESS_CSS + EXTRA
        + SC.nav("bosses.html", str(len(BOSSES)) + " bosses &middot; one order")
        + BODY)
HTML = HTML.replace("<title>Joseph's Modpack Wiki</title>", "<title>Boss Checklist</title>", 1)

JS = r"""
<script>
(function(){
"use strict";
var D = JSON.parse(document.getElementById("bossdata").textContent);
var BANDS=D.bands, BOSSES=D.bosses, WIKI=D.wiki, MC=D.modcol, SP=D.sprites;
// Six invented hues replaced by the two the site already uses for exactly this idea:
// --pre and --hard carry the pre-Hardmode / Hardmode split everywhere else. Post-Moon Lord
// is past both, so it takes the brass the site uses for its own emphasis; the optional
// bands stay neutral because they are not points on the progression.
var BANDCOL={pre:"var(--pre)", hard:"var(--hard)", postml:"var(--brass)",
             event:"var(--ink-3)", mini:"var(--ink-3)", seed:"var(--ink-3)"};

function el(t,c,x){var e=document.createElement(t); if(c)e.className=c; if(x!=null)e.textContent=x; return e;}
function sprite(name){
  var s=SP[name]; if(!s) return null;
  var i=new Image(); i.src=s; i.alt=""; i.className="px"; i.loading="lazy"; return i;
}

/* ---------- state ---------- */
var KEY="bosses.done.v1", MKEY="bosses.mods.v1", HKEY="bosses.hidedone.v1";
function read(k,f){ try{ var v=localStorage.getItem(k); return v==null?f:JSON.parse(v); }catch(e){ return f; } }
function write(k,v){ try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){} }
var done = read(KEY, {});
var MODS = []; BOSSES.forEach(function(b){ if(MODS.indexOf(b.mod)<0) MODS.push(b.mod); });
var shown = read(MKEY, null);
if(!shown || !MODS.some(function(m){return shown[m];})){ shown={}; MODS.forEach(function(m){shown[m]=1;}); }
var hideDone = !!read(HKEY, false);

function visible(b){ return !!shown[b.mod]; }
function pool(){ return BOSSES.filter(visible); }

/* ---------- toolbar ---------- */
var chips=document.getElementById("modchips");
MODS.forEach(function(m){
  var b=el("button","modchip"); b.type="button"; b.dataset.m=m;
  b.style.setProperty("--mcol", MC[m]||"#7d85ab");
  b.appendChild(el("i")); b.appendChild(document.createTextNode(WIKI[m]||m));
  chips.appendChild(b);
});
chips.addEventListener("click", function(e){
  var b=e.target.closest("button.modchip"); if(!b) return;
  var on = MODS.filter(function(m){ return shown[m]; });
  if(shown[b.dataset.m] && on.length===1) return;      // never hide everything
  shown[b.dataset.m] = shown[b.dataset.m] ? 0 : 1;
  write(MKEY, shown); render();
});
var hbtn=document.getElementById("hidedone");
hbtn.addEventListener("click", function(){ hideDone=!hideDone; write(HKEY,hideDone); render(); });
document.getElementById("reset").addEventListener("click", function(){
  var n=Object.keys(done).length;
  if(n && !window.confirm("Clear all "+n+" ticks?")) return;
  done={}; write(KEY,done); render();
});

/* ---------- rows ---------- */
function bossRow(b, isNext){
  var row=el("div","boss"+(done[b.name]?" done":"")+(isNext?" next":""));
  row.style.setProperty("--mcol", MC[b.mod]||"#7d85ab");
  row.dataset.name=b.name;

  var t=el("button","tick","✓"); t.type="button";
  t.setAttribute("aria-pressed", done[b.name]?"true":"false");
  t.setAttribute("aria-label", (done[b.name]?"Mark ":"Mark ")+b.name+(done[b.name]?" not beaten":" beaten"));
  t.addEventListener("click", function(){ toggle(b.name); });
  row.appendChild(t);

  var sp=el("div","sp"), im=sprite(b.name);
  if(im) sp.appendChild(im);
  row.appendChild(sp);

  var nm=el("div","nm"), top=el("div","top");
  var a=el("a","name",b.name); a.href=b.url; a.target="_blank"; a.rel="noopener noreferrer";
  top.appendChild(a);
  var tag=el("span","modtag", WIKI[b.mod]||b.mod);
  tag.style.setProperty("--mcol", MC[b.mod]||"#7d85ab");
  top.appendChild(tag);
  nm.appendChild(top);

  var bits=[];
  if(b.summon) bits.push(b.summon);
  if(b.env)    bits.push("In the " + b.env);
  var sub=el("div","sub");
  if(bits.length) sub.appendChild(document.createTextNode(bits.join(" · ")));
  if(b.anchor){
    if(bits.length) sub.appendChild(document.createTextNode(" · "));
    sub.appendChild(el("b", null, WIKI[b.mod]+" puts it after "+b.anchor));
  } else if(b.unordered){
    if(bits.length) sub.appendChild(document.createTextNode(" · "));
    sub.appendChild(el("b", null, WIKI[b.mod]+" publishes no order for it"));
  } else if(b.mod!=="vanilla"){
    if(bits.length) sub.appendChild(document.createTextNode(" · "));
    sub.appendChild(el("b", null, WIKI[b.mod]+" opens the run with it"));
  }
  if(sub.childNodes.length) nm.appendChild(sub);
  // where the placement came from, when it was not a progression chart
  if(b.evidence && (b.how==="stated" || b.how==="inferred")){
    var w=el("div","why"+(b.how==="inferred"?" guessy":""));
    w.appendChild(el("span","howtag", b.how==="stated" ? "its wiki says" : "placed from"));
    w.appendChild(document.createTextNode(" "+b.evidence));
    nm.appendChild(w);
  }
  row.appendChild(nm);

  var side=el("div","side");
  if(b.life) side.appendChild(el("span","life", b.life + " hp"));
  if(b.stage){
    var g=el("a","gear","Gear up →"); g.href="loadouts.html#"+b.stage;
    g.title="Open the Loadouts checkpoint you want to be equipped for";
    side.appendChild(g);
  }
  row.appendChild(side);
  return row;
}

function toggle(name){
  if(done[name]) delete done[name]; else done[name]=1;
  write(KEY, done);
  if(hideDone){ render(); return; }
  // 87 rows do not need rebuilding to tick one box: touch the row, then the counters
  var row=bandsHost.querySelector('.boss[data-name="'+name.replace(/"/g,'\\"')+'"]');
  if(!row){ render(); return; }
  var on=!!done[name];
  row.classList.toggle("done", on);
  var t=row.querySelector(".tick");
  t.setAttribute("aria-pressed", on?"true":"false");
  t.setAttribute("aria-label", "Mark "+name+(on?" not beaten":" beaten"));
  refreshCounts();
}

/* ---------- render ---------- */
var bandsHost=document.getElementById("bands"),
    barsHost=document.getElementById("bandbars"),
    nextHost=document.getElementById("nextup");

/* counters, the next-up card and the current-target outline, without rebuilding the list */
/* The same rule the rest of the site uses: where you are is the furthest boss you have
   beaten, so skipping an optional one does not drag "next up" back to the start. */
function nextUp(list){
  var far=-1;
  list.forEach(function(b){ if(done[b.name] && b.order>far) far=b.order; });
  var main=list.filter(function(b){ return b.band!=="mini" && b.band!=="seed"; });
  return main.filter(function(b){ return !done[b.name] && b.order>far; })[0]
      || main.filter(function(b){ return !done[b.name]; })[0]
      || list.filter(function(b){ return !done[b.name]; })[0] || null;
}
function skippedBefore(list, next){
  if(!next) return 0;
  return list.filter(function(b){
    return !done[b.name] && b.order<next.order && b.band!=="mini" && b.band!=="seed";
  }).length;
}

function refreshCounts(){
  var list = pool().slice().sort(function(a,b){ return a.order-b.order; });
  var nDone = list.filter(function(b){ return done[b.name]; }).length;
  var next  = nextUp(list);
  document.getElementById("pdone").textContent = nDone;
  document.getElementById("pof").textContent   = "of " + list.length + " bosses beaten";
  document.getElementById("pfill").style.width = (list.length ? nDone/list.length*100 : 0) + "%";
  document.getElementById("metadone").textContent = nDone;
  drawBars(list); drawNext(next, skippedBefore(list, next));
  bandsHost.querySelectorAll(".boss").forEach(function(r){
    r.classList.toggle("next", !!next && r.dataset.name===next.name);
  });
  BANDS.forEach(function(bd){
    var inb=list.filter(function(b){ return b.band===bd[0]; });
    var sec=bandsHost.querySelector('section.band[data-band="'+bd[0]+'"] header .cnt');
    if(sec && inb.length){
      sec.textContent = inb.filter(function(b){ return done[b.name]; }).length
                      + " of " + inb.length + " beaten";
    }
  });
}

function render(){
  chips.querySelectorAll("button.modchip").forEach(function(b){
    b.setAttribute("aria-pressed", shown[b.dataset.m] ? "true":"false");
  });
  hbtn.setAttribute("aria-pressed", hideDone?"true":"false");
  hbtn.textContent = hideDone ? "Show beaten" : "Hide beaten";

  var list = pool().slice().sort(function(a,b){ return a.order-b.order; });
  var nDone = list.filter(function(b){ return done[b.name]; }).length;
  var next  = nextUp(list);

  document.getElementById("pdone").textContent = nDone;
  document.getElementById("pof").textContent   = "of " + list.length + " bosses beaten";
  document.getElementById("pfill").style.width = (list.length ? nDone/list.length*100 : 0) + "%";
  document.getElementById("metadone").textContent = nDone;

  drawBars(list);
  drawNext(next, skippedBefore(list, next));

  bandsHost.textContent="";
  bandsHost.style.minHeight="";   // reservation done its job; let the real content size it
  BANDS.forEach(function(bd){
    var inb = list.filter(function(b){ return b.band===bd[0]; });
    if(!inb.length) return;
    var sec=el("section","band"); sec.dataset.band=bd[0];
    sec.style.setProperty("--bcol", BANDCOL[bd[0]]||"var(--brass)");
    var hd=el("header");
    hd.appendChild(el("h2",null,bd[1]));
    hd.appendChild(el("p",null,bd[2]));
    var d=inb.filter(function(b){ return done[b.name]; }).length;
    hd.appendChild(el("span","cnt", d+" of "+inb.length+" beaten"));
    sec.appendChild(hd);
    var ul=el("div","list"), shownAny=false, notedUnordered=false;
    inb.forEach(function(b){
      if(hideDone && done[b.name]) return;
      if(b.unordered && !notedUnordered && inb.some(function(x){ return !x.unordered; })){
        notedUnordered=true;
        ul.appendChild(el("p","unord",
          "Below: bosses whose wiki publishes no position in the order. They belong somewhere in "
          + "this band — exactly where is not written down."));
      }
      ul.appendChild(bossRow(b, next && b.name===next.name));
      shownAny=true;
    });
    if(!shownAny) ul.appendChild(el("p","emptyband","All beaten in this band."));
    sec.appendChild(ul);
    bandsHost.appendChild(sec);
  });
}

function drawBars(list){
  barsHost.textContent="";
  BANDS.forEach(function(bd){
    var inb = list.filter(function(b){ return b.band===bd[0]; });
    if(!inb.length) return;
    var d = inb.filter(function(b){ return done[b.name]; }).length;
    var r = el("div","bandbar");
    r.style.setProperty("--bcol", BANDCOL[bd[0]]||"var(--brass)");
    r.appendChild(el("span",null,bd[1]));
    var t=el("span","t"), i=el("i"); i.style.width=(d/inb.length*100)+"%"; t.appendChild(i);
    r.appendChild(t);
    r.appendChild(el("span","c", d+"/"+inb.length));
    barsHost.appendChild(r);
  });
}

function drawNext(next, skipped){
  nextHost.textContent="";
  if(!next){
    nextHost.appendChild(el("h2",null,"All done"));
    nextHost.appendChild(el("p",null,"Every boss in view is ticked off. Turn a mod back on, or "
      + "clear the ticks to run it again."));
  } else {
    nextHost.appendChild(el("h2",null,"Next up"));
    var row=el("div","row"), sp=el("div","sp"), im=sprite(next.name);
    if(im) sp.appendChild(im);
    row.appendChild(sp);
    var box=el("div");
    var h=el("h3"); var a=el("a",null,next.name);
    a.href=next.url; a.target="_blank"; a.rel="noopener noreferrer"; h.appendChild(a);
    box.appendChild(h);
    box.appendChild(el("p", null, (WIKI[next.mod]||next.mod) + " · "
      + BANDS.filter(function(x){return x[0]===next.band;})[0][1]
      + (next.anchor ? " · after " + next.anchor : "")));
    if(next.summon) box.appendChild(el("p", null, next.summon));
    if(skipped) box.appendChild(el("p", null,
      skipped + (skipped===1 ? " boss earlier in the order is" : " bosses earlier in the order are")
      + " still unticked — optional ones you may have skipped."));
    var acts=el("div","acts");
    var mk=el("button",null,"Mark beaten"); mk.type="button";
    mk.addEventListener("click", function(){ toggle(next.name); });
    acts.appendChild(mk);
    if(next.stage){
      var g=el("a","ghost","Gear up for it →"); g.href="loadouts.html#"+next.stage;
      acts.appendChild(g);
    }
    box.appendChild(acts);
    row.appendChild(box);
    nextHost.appendChild(row);
  }
}

function measure(){
  var nb=document.querySelector(".sitenav");
  document.documentElement.style.setProperty("--navh", (nb?nb.offsetHeight:42)+"px");
}
window.addEventListener("resize", measure);
measure(); render();
})();
</script>
"""

out = os.path.join(ROOT, "bosses.html")
open(out, "w", encoding="utf-8").write(HTML + SC.progress_js("bosses.html") + JS)
print("wrote bosses.html %.2f MB | %d bosses (%d from mods)"
      % (os.path.getsize(out)/1048576, len(BOSSES), n_mod))
