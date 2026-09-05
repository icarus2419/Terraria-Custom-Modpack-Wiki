import json, os, html
BASE = os.path.dirname(os.path.abspath(__file__))
from gen_css import CSS as BASECSS
import site_common as SC

L  = json.load(open(os.path.join(BASE,"loadouts.json")))
SP = json.load(open(os.path.join(BASE,"loadout_sprites.json")))

STAGES, CLASS_ORDER, CLASS_META, MODS = L["stages"], L["class_order"], L["class_meta"], L["mods"]
DATA = L["data"]
MODCOL = {"vanilla":"#6f7794","thorium":"#3f9e8c","spirit":"#5a80c9","stars":"#c2a1e8"}

payload = json.dumps({"stages":STAGES,"class_order":CLASS_ORDER,"class_meta":CLASS_META,
                      "mods":MODS,"modcol":MODCOL,"data":DATA,"sprites":SP},
                     separators=(",",":")).replace("<","\\u003c")

n_items = sum(len(b["items"]) for s in DATA.values() for c in s.values()
              for m in c.values() for b in m)
n_cls = len({c for s in DATA.values() for c in s})

EXTRA = """
<style>
.lo-layout{display:grid; grid-template-columns:230px minmax(0,1fr); gap:24px; align-items:start; padding:22px 0 60px}
@media (max-width:940px){ .lo-layout{grid-template-columns:minmax(0,1fr)} .stagenav{position:static; max-height:none} }
.stagenav{position:sticky; top:104px; background:var(--surface); border:1px solid var(--line);
  border-radius:var(--radius); box-shadow:var(--shadow); overflow:hidden}
.stagenav h3{margin:0; padding:9px 12px; border-bottom:1px solid var(--line); background:var(--surface-2);
  font-family:"Pixelify Sans",sans-serif; font-size:10px; letter-spacing:.1em; text-transform:uppercase; color:var(--ink-3); font-weight:500}
button.stagebtn{display:flex; align-items:baseline; gap:8px; width:100%; text-align:left; font:inherit;
  font-size:12.5px; background:none; border:0; border-left:3px solid transparent; padding:6px 12px;
  color:var(--ink-2); cursor:pointer}
button.stagebtn:hover{background:var(--surface-2); color:var(--ink)}
button.stagebtn[aria-current="true"]{background:var(--brass-soft); color:var(--brass); border-left-color:var(--brass); font-weight:600}
button.stagebtn .num{font-family:"JetBrains Mono",monospace; font-size:10px; color:var(--ink-3); width:1.2em; flex:none}
button.stagebtn[aria-current="true"] .num{color:var(--brass)}
.hmsplit{padding:7px 12px 3px; font-family:"Pixelify Sans",sans-serif; font-size:9.5px;
  letter-spacing:.09em; text-transform:uppercase; color:var(--hard); border-top:1px solid var(--line); margin-top:4px}

.stagehead{background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
  box-shadow:var(--shadow); padding:16px 18px; margin-bottom:16px}
.stagehead .eyebrow{margin:0 0 3px; font-family:"Pixelify Sans",sans-serif; font-size:10px;
  letter-spacing:.12em; text-transform:uppercase; color:var(--brass)}
.stagehead h2{margin:0 0 5px; font-family:"Pixelify Sans",sans-serif; font-size:26px; line-height:1.1}
.stagehead p{margin:0; color:var(--ink-2); font-size:13.5px; max-width:70ch}
.stagehead .era{margin-left:0; margin-top:9px; display:inline-flex}

.classgrid{display:grid; grid-template-columns:repeat(auto-fill,minmax(310px,1fr)); gap:14px}
.classcard{background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
  box-shadow:var(--shadow); overflow:hidden; display:flex; flex-direction:column}
.classcard > header{padding:10px 14px; border-bottom:1px solid var(--line); border-top:3px solid var(--ccol)}
.classcard h3{margin:0 0 2px; font-family:"Pixelify Sans",sans-serif; font-size:16px; color:var(--ccol)}
.classcard .blurb{margin:0; font-size:11.5px; color:var(--ink-3); line-height:1.4}
.catblock{padding:9px 14px; border-bottom:1px solid var(--line)}
.catblock:last-child{border-bottom:0}
.catblock h4{margin:0 0 6px; font-family:"Pixelify Sans",sans-serif; font-size:9.5px;
  letter-spacing:.09em; text-transform:uppercase; color:var(--ink-3); font-weight:500;
  display:flex; align-items:center; gap:6px}
.catblock h4 .modtag{margin-left:auto; font-family:"JetBrains Mono",monospace; font-size:9px;
  letter-spacing:0; text-transform:none; color:#fff; padding:1px 5px; border-radius:100px}
.gearlist{display:flex; flex-wrap:wrap; gap:5px; margin:0; padding:0; list-style:none}
.gear{display:inline-flex; align-items:center; gap:6px; background:var(--surface-2);
  border:1px solid var(--line); border-radius:100px; padding:3px 10px 3px 3px; font-size:12px; color:var(--ink)}
a.gear{text-decoration:none}
a.gear:hover{border-color:var(--brass); color:var(--brass)}
.gear .gsp{width:24px;height:24px;display:grid;place-items:center;background:var(--slot-bg);
  border:1px solid var(--slot-line); border-radius:3px; flex:none}
.gear .gsp img{max-width:19px;max-height:19px;width:auto;height:auto}
.gear .qual{font-size:9.5px; color:var(--ink-3); font-style:italic}
.acc-block{background:color-mix(in srgb, var(--brass) 7%, transparent)}
.carry-block{background:color-mix(in srgb, var(--brass) 4%, transparent); border-top:1px dashed var(--line-strong)}
.carrynote{margin:0 0 6px; font-size:10.5px; color:var(--ink-3); font-style:italic; line-height:1.4}
.emptyclass{padding:14px; color:var(--ink-3); font-size:12.5px}
.legend{display:flex; gap:14px; flex-wrap:wrap; align-items:center; padding:10px 0 0; font-size:11.5px; color:var(--ink-3)}
.legend span.k{display:inline-flex; align-items:center; gap:5px}
.legend i{width:9px;height:9px;border-radius:2px;display:inline-block}
</style>
"""

BODY = """
<header class="masthead"><div class="wrap mast-in">
  <div class="brandline"><div>
    <p class="eyebrow">Class setups &middot; every boss checkpoint</p>
    <h1>Loadouts</h1>
    <p class="tagline">What to wear and carry for each class before each boss &mdash; <b>armour, accessories,
    weapons and buffs</b> &mdash; merged from the class-setup guides of Terraria, Thorium, Spirit and
    The Stars Above onto one timeline.</p>
  </div></div>
  <dl class="meta">
    <div><dt>Stages</dt><dd>@@NST@@</dd></div>
    <div><dt>Classes</dt><dd>@@NCL@@</dd></div>
    <div><dt>Gear entries</dt><dd>@@NIT@@</dd></div>
  </dl>
</div></header>

<main class="wrap lo-layout">
  <nav class="stagenav" id="stagenav"><h3>Progression</h3></nav>
  <section>
    <div class="stagehead" id="stagehead"></div>
    <div class="classgrid" id="classgrid"></div>
    <div class="legend">
      <span class="k"><i style="background:#6f7794"></i>Terraria</span>
      <span class="k"><i style="background:#3f9e8c"></i>Thorium</span>
      <span class="k"><i style="background:#5a80c9"></i>Spirit</span>
      <span class="k"><i style="background:#c2a1e8"></i>Stars Above</span>
      <span>Each block is credited to the wiki it came from. Accessory blocks are tinted.</span>
    </div>
  </section>
</main>

<footer><div class="wrap fgrid">
  <div><h4>Where these come from</h4>
    <p>Parsed from each wiki's own <code>Guide:Class setups</code> page &mdash; terraria.wiki.gg,
    thoriummod.wiki.gg, spiritmod.wiki.gg and starsabovemod.wiki.gg. Nothing here is invented;
    every item is what that wiki recommends at that point in progression.</p></div>
  <div><h4>How the stages line up</h4>
    <p>Each mod names its checkpoints differently &mdash; Thorium's <em>Pre-Eater of Worlds / Brain of
    Cthulhu</em>, Spirit's <em>Pre-Evil Boss</em>, Stars Above's <em>Pre-The Vagrant of Space and
    Time</em> all sit at the same point. They are mapped onto one timeline, and each block still
    shows the stage name its own wiki used.</p></div>
  <div><h4>Reading it</h4>
    <p>Pick your stage on the left, then your class. Armour and accessories come first in each card,
    then weapons, then buffs. Bard and Healer are Thorium classes &mdash; Healer only functions in
    multiplayer, and Bard buffs scale with party size.</p></div>
</div></footer>

<script id="loadouts" type="application/json">@@PAYLOAD@@</script>
"""

for a, b in [("@@NST@@", str(len(STAGES))), ("@@NCL@@", str(n_cls)),
             ("@@NIT@@", str(n_items)), ("@@PAYLOAD@@", payload)]:
    BODY = BODY.replace(a, b)

HTML = ('<meta charset="utf-8">\n' + BASECSS + SC.NAV_CSS + EXTRA
        + SC.nav("loadouts.html", str(len(STAGES)) + " stages &middot; " + str(n_cls) + " classes")
        + BODY)
HTML = HTML.replace("<title>Joseph's Modpack Wiki</title>", "<title>Loadouts by Boss</title>", 1)

JS = r"""
<script>
(function(){
"use strict";
var D=JSON.parse(document.getElementById("loadouts").textContent);
var STAGES=D.stages, CO=D.class_order, CM=D.class_meta, MODS=D.mods, MC=D.modcol, DATA=D.data, SP=D.sprites;
function el(t,c,x){var e=document.createElement(t); if(c)e.className=c; if(x!=null)e.textContent=x; return e;}
var VALID={}; STAGES.forEach(function(s){VALID[s[0]]=1;});
var cur=(location.hash||"").replace(/^#/,"");
if(!VALID[cur]) cur=STAGES[0][0];

var nav=document.getElementById("stagenav");
STAGES.forEach(function(s,i){
  if(s[3] && (i===0 || !STAGES[i-1][3])) nav.appendChild(el("div","hmsplit","Hardmode"));
  var b=el("button","stagebtn"); b.type="button"; b.dataset.k=s[0];
  b.appendChild(el("span","num",String(i+1)));
  b.appendChild(document.createTextNode(s[1]));
  nav.appendChild(b);
});
nav.addEventListener("click",function(e){
  var b=e.target.closest("button.stagebtn"); if(!b) return;
  cur=b.dataset.k;
  if(history.replaceState) history.replaceState(null,"","#"+cur);
  render();
  if(window.matchMedia("(max-width:940px)").matches)
    document.getElementById("stagehead").scrollIntoView({behavior:"smooth",block:"start"});
});

var head=document.getElementById("stagehead"), grid=document.getElementById("classgrid");
function render(){
  nav.querySelectorAll("button.stagebtn").forEach(function(b){
    b.setAttribute("aria-current", b.dataset.k===cur?"true":"false");
  });
  var st=null,idx=0;
  STAGES.forEach(function(s,i){ if(s[0]===cur){st=s;idx=i;} });
  head.textContent="";
  head.appendChild(el("p","eyebrow","Stage "+(idx+1)+" of "+STAGES.length));
  head.appendChild(el("h2",null,st[1]));
  head.appendChild(el("p",null,"Gear up for: "+st[2]));
  var era=el("span","era "+(st[3]?"hard":"pre"), st[3]?"hardmode":"pre-hardmode");
  head.appendChild(era);

  grid.textContent="";
  var classes=DATA[cur]||{};
  var keys=Object.keys(classes).sort(function(a,b){
    var ia=CO.indexOf(a), ib=CO.indexOf(b);
    return (ia<0?99:ia)-(ib<0?99:ib);
  });
  if(!keys.length){ grid.appendChild(el("div","emptyclass","No published setups for this stage.")); return; }
  keys.forEach(function(cl){
    var meta=CM[cl]||["#7d85ab",""];
    var card=el("div","classcard"); card.style.setProperty("--ccol",meta[0]);
    var h=el("header");
    h.appendChild(el("h3",null,cl));
    h.appendChild(el("p","blurb",meta[1]));
    card.appendChild(h);
    var mods=classes[cl];
    Object.keys(mods).sort(function(a,b){
      return (a==="_carry"?1:0)-(b==="_carry"?1:0);       // carried-forward blocks last
    }).forEach(function(m){
      mods[m].forEach(function(box){
        var isAcc=/accessor/i.test(box.t);
        var isCarry=(m==="_carry");
        var blk=el("div","catblock"+(isAcc?" acc-block":"")+(isCarry?" carry-block":""));
        var h4=el("h4",null,box.t);
        if(!isCarry){
          var tag=el("span","modtag",MODS[m]||m); tag.style.background=MC[m]||"#888";
          h4.appendChild(tag);
        }
        blk.appendChild(h4);
        if(isCarry) blk.appendChild(el("p","carrynote",
          "The guides list no new accessories here \u2014 keep what you had at " + box.src + "."));
        var ul=el("ul","gearlist");
        box.items.forEach(function(it){
          var node = it.url ? el("a","gear") : el("span","gear");
          if(it.url){ node.href=it.url; node.target="_blank"; node.rel="noopener noreferrer"; }
          var sp=SP[it.name];
          if(sp){ var b2=el("span","gsp"); var im=new Image(); im.src=sp; im.alt=""; im.className="px"; im.loading="lazy"; b2.appendChild(im); node.appendChild(b2); }
          node.appendChild(document.createTextNode(it.name));
          if(it.note) node.appendChild(el("span","qual",it.note));
          var li=el("li"); li.appendChild(node); ul.appendChild(li);
        });
        blk.appendChild(ul);
        card.appendChild(blk);
      });
    });
    grid.appendChild(card);
  });
}
window.addEventListener("hashchange",function(){
  var k=(location.hash||"").replace(/^#/,"");
  if(VALID[k]&&k!==cur){ cur=k; render(); }
});
render();
})();
</script>
"""

open(os.path.join(BASE,"loadouts.html"),"w",encoding="utf-8").write(HTML+JS)
print("wrote loadouts.html %.2f MB | %d gear entries | %d stages"
      % (os.path.getsize(os.path.join(BASE,"loadouts.html"))/1048576, n_items, len(STAGES)))
