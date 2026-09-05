import json, os, html
BASE = os.path.dirname(os.path.abspath(__file__))
from gen_css import CSS as BASECSS
import site_common as SC

L  = json.load(open(os.path.join(BASE,"loadouts.json")))
SP = json.load(open(os.path.join(BASE,"loadout_sprites.json")))
ICON = json.load(open(os.path.join(BASE,"boss_icons.json")))
STATS = json.load(open(os.path.join(BASE,"loadout_stats.json")))

STAGES, CLASS_ORDER, CLASS_META, MODS = L["stages"], L["class_order"], L["class_meta"], L["mods"]
DATA = L["data"]
MODCOL = {"vanilla":"#6f7794","thorium":"#3f9e8c","spirit":"#5a80c9","stars":"#c2a1e8"}

payload = json.dumps({"stages":STAGES,"class_order":CLASS_ORDER,"class_meta":CLASS_META,
                      "mods":MODS,"modcol":MODCOL,"cat_order":L["cat_order"],"data":DATA,"sprites":SP,
                      "icons":ICON,"stats":STATS},
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
.stagenav h3{margin:0; padding:10px 12px; border-bottom:1px solid var(--line); background:var(--surface-2);
  font-family:"Pixelify Sans",sans-serif; font-size:10px; letter-spacing:.1em; text-transform:uppercase;
  color:var(--ink-3); font-weight:500}
button.stagebtn{display:flex; align-items:center; gap:9px; width:100%; text-align:left; font:inherit;
  background:none; border:0; border-left:3px solid transparent; padding:7px 11px; cursor:pointer;
  color:var(--ink-2); position:relative}
button.stagebtn:hover{background:var(--surface-2)}
button.stagebtn .num{font-family:"JetBrains Mono",monospace; font-size:10px; color:var(--ink-3);
  width:1.4em; flex:none; text-align:right; font-variant-numeric:tabular-nums}
button.stagebtn .bi{width:26px; height:26px; flex:none; display:grid; place-items:center;
  background:var(--slot-bg); border:1px solid var(--slot-line); border-radius:4px}
button.stagebtn .bi img{max-width:18px; max-height:18px; width:auto; height:auto; opacity:.85}
button.stagebtn .txt{min-width:0; display:flex; flex-direction:column; line-height:1.15}
button.stagebtn .pre{font-size:9px; letter-spacing:.09em; text-transform:uppercase; color:var(--ink-3);
  font-family:"Pixelify Sans",sans-serif}
button.stagebtn .boss{font-size:13.5px; font-weight:600; color:var(--ink-2)}
button.stagebtn:hover .boss{color:var(--ink)}
button.stagebtn[aria-current="true"]{background:var(--brass-soft); border-left-color:var(--brass)}
button.stagebtn[aria-current="true"] .boss{color:var(--brass)}
button.stagebtn[aria-current="true"] .pre{color:color-mix(in srgb,var(--brass) 70%, var(--ink-3))}
button.stagebtn[aria-current="true"] .num{color:var(--brass)}
button.stagebtn[aria-current="true"] .bi{border-color:var(--brass); background:color-mix(in srgb,var(--brass) 18%, var(--slot-bg))}
button.stagebtn[aria-current="true"] .bi img{opacity:1}
button.stagebtn[aria-current="true"]::after{content:""; position:absolute; right:9px; top:50%;
  width:6px; height:6px; margin-top:-3px; border-right:2px solid var(--brass);
  border-bottom:2px solid var(--brass); transform:rotate(-45deg)}
.hmsplit{display:flex; align-items:center; gap:7px; padding:9px 12px 5px; margin-top:3px;
  border-top:1px solid var(--line);
  font-family:"Pixelify Sans",sans-serif; font-size:9px; letter-spacing:.1em; text-transform:uppercase;
  color:var(--hard)}
.hmsplit::after{content:""; flex:1; height:1px; background:color-mix(in srgb,var(--hard) 40%, transparent)}
.navfoot{padding:8px 12px; border-top:1px solid var(--line); background:var(--surface-2);
  font-family:"JetBrains Mono",monospace; font-size:10px; color:var(--ink-3)}
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
.catblock h4 .cnt{margin-left:auto; font-family:"JetBrains Mono",monospace; font-size:9.5px;
  letter-spacing:0; text-transform:none; color:var(--ink-3)}
.gearlist{display:flex; flex-wrap:wrap; gap:5px; margin:0; padding:0; list-style:none}
.gear{display:inline-flex; align-items:center; gap:6px;
  background:color-mix(in srgb, var(--src) 24%, var(--surface-2));
  border:1px solid color-mix(in srgb, var(--src) 85%, transparent);
  border-radius:100px; padding:3px 10px 3px 3px; font-size:12px; color:var(--ink)}
a.gear{text-decoration:none}
a.gear:hover{border-color:var(--src); background:color-mix(in srgb, var(--src) 42%, var(--surface-2))}
.gear .gsp{width:24px;height:24px;display:grid;place-items:center;background:var(--slot-bg);
  border:1px solid var(--slot-line); border-radius:3px; flex:none}
.gear .gsp img{max-width:19px;max-height:19px;width:auto;height:auto}
.gear .qual{font-size:9.5px; color:var(--ink-3); font-style:italic}
.gear .qual.best{
  font-style:normal; font-family:"Pixelify Sans",sans-serif; letter-spacing:.05em;
  text-transform:uppercase; font-size:9px; color:var(--brass-bright);
  border:1px solid var(--brass-line); border-radius:100px; padding:0 5px;
}
.gear.is-best{box-shadow:0 0 0 1px color-mix(in srgb,var(--brass) 45%, transparent)}
.catblock h4 .rankhint{margin-left:6px; font-family:"Asap",sans-serif; font-size:9.5px;
  letter-spacing:0; text-transform:none; font-style:italic; color:var(--ink-3)}
.acc-block{background:color-mix(in srgb, var(--brass) 7%, transparent)}
.carry-block{background:color-mix(in srgb, var(--brass) 4%, transparent); border-top:1px dashed var(--line-strong)}
.carrynote{margin:0 0 6px; font-size:10.5px; color:var(--ink-3); font-style:italic; line-height:1.4}
.emptyclass{padding:14px; color:var(--ink-3); font-size:12.5px}
#statcard{
  position:fixed; z-index:200; max-width:300px; pointer-events:none; opacity:0;
  background:var(--tip-bg); color:var(--tip-ink); border:1px solid var(--brass-line);
  border-radius:6px; padding:10px 12px; box-shadow:0 10px 30px -8px rgba(0,0,0,.6);
  transition:opacity .09s ease;
}
#statcard[data-show="1"]{opacity:1}
#statcard .sc-h{display:flex; align-items:center; gap:8px; margin-bottom:7px}
#statcard .sc-sp{width:30px;height:30px;flex:none;display:grid;place-items:center;
  background:rgba(255,255,255,.07); border:1px solid rgba(255,255,255,.15); border-radius:4px}
#statcard .sc-sp img{max-width:24px;max-height:24px;width:auto;height:auto}
#statcard h5{margin:0; font-family:"Pixelify Sans",sans-serif; font-size:14px; line-height:1.15;
  color:#fff}
#statcard .sc-kind{font-size:10px; letter-spacing:.05em; text-transform:uppercase;
  color:color-mix(in srgb,var(--brass-bright) 80%, #fff); font-family:"Pixelify Sans",sans-serif}
#statcard .sc-rows{display:grid; grid-template-columns:auto 1fr; gap:2px 12px; font-size:12px;
  margin-bottom:6px}
#statcard .sc-rows dt{color:rgba(223,227,245,.6); font-size:10.5px; letter-spacing:.04em;
  text-transform:uppercase; font-family:"Pixelify Sans",sans-serif}
#statcard .sc-rows dd{margin:0; font-family:"JetBrains Mono",monospace; font-variant-numeric:tabular-nums;
  color:#fff}
#statcard .sc-rows dd.dmg{color:var(--brass-bright); font-weight:700}
#statcard .sc-tip{font-size:11.5px; line-height:1.45; color:rgba(223,227,245,.85);
  border-top:1px solid rgba(255,255,255,.12); padding-top:6px; margin:0}
#statcard .sc-bonus{font-size:11.5px; line-height:1.45; color:#fff; margin:0 0 4px;
  border-left:2px solid var(--brass); padding-left:7px}
#statcard .sc-none{font-size:11.5px; color:rgba(223,227,245,.6); margin:0}
.keybar{display:flex; gap:8px; flex-wrap:wrap; align-items:center; margin-bottom:14px;
  background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
  box-shadow:var(--shadow); padding:9px 14px}
.keybar .lbl{font-family:"Pixelify Sans",sans-serif; font-size:9.5px; letter-spacing:.09em;
  text-transform:uppercase; color:var(--ink-3); margin-right:2px}
.keybar .k{display:inline-flex; align-items:center; gap:6px; font-size:11.5px; color:var(--ink);
  background:color-mix(in srgb, var(--src) 24%, var(--surface-2));
  border:1px solid color-mix(in srgb, var(--src) 85%, transparent);
  border-radius:100px; padding:2px 10px}
.keybar .k i{width:8px;height:8px;border-radius:50%;display:inline-block;background:var(--src)}
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
  <nav class="stagenav" id="stagenav"><h3>Gear up before\u2026</h3></nav>
  <section>
    <div class="stagehead" id="stagehead"></div>
    <div class="keybar">
      <span class="lbl">Gear colour = source</span>
      <span class="k" style="--src:#6f7794"><i></i>Terraria</span>
      <span class="k" style="--src:#3f9e8c"><i></i>Thorium</span>
      <span class="k" style="--src:#5a80c9"><i></i>Spirit</span>
      <span class="k" style="--src:#c2a1e8"><i></i>Stars Above</span>
    </div>
    <div class="classgrid" id="classgrid"></div>
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
var STAGES=D.stages, CO=D.class_order, CM=D.class_meta, MODS=D.mods, MC=D.modcol,
    CATO=D.cat_order, DATA=D.data, SP=D.sprites, ICON=D.icons||{}, STATS=D.stats||{};
function el(t,c,x){var e=document.createElement(t); if(c)e.className=c; if(x!=null)e.textContent=x; return e;}
var VALID={}; STAGES.forEach(function(s){VALID[s[0]]=1;});
var cur=(location.hash||"").replace(/^#/,"");
if(!VALID[cur]) cur=STAGES[0][0];

var nav=document.getElementById("stagenav");
STAGES.forEach(function(s,i){
  if(s[3] && (i===0 || !STAGES[i-1][3])) nav.appendChild(el("div","hmsplit","Hardmode"));
  var b=el("button","stagebtn"); b.type="button"; b.dataset.k=s[0];
  b.appendChild(el("span","num",String(i+1)));
  var bi=el("span","bi");
  if(ICON[s[0]]){ var im=new Image(); im.src=ICON[s[0]]; im.alt=""; im.className="px"; bi.appendChild(im); }
  b.appendChild(bi);
  var t=el("span","txt");
  t.appendChild(el("span","pre", s[0]==="endgame" ? "after" : "before"));
  t.appendChild(el("span","boss", s[4]||s[1]));
  b.appendChild(t);
  nav.appendChild(b);
});
nav.appendChild(el("div","navfoot","11 checkpoints \u00b7 5 pre-Hardmode"));
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
    // one block per category, pills coloured by the wiki they came from
    var mods=classes[cl], byCat={}, carry={};
    Object.keys(mods).forEach(function(m){
      mods[m].forEach(function(box){
        var arr = byCat[box.t] || (byCat[box.t]=[]);
        box.items.forEach(function(it){
          if(!arr.some(function(x){return x.it.name===it.name;})) arr.push({it:it, mod:m});
        });
        if(m==="_carry"||m==="_tharmour") carry[box.t]={src:box.src, kind:m};
      });
    });
    // The vanilla guide marks its picks "Best" / "Second Best"; lead with those and keep
    // each wiki's own listing order underneath. Mods that publish no ranking stay as listed.
    function rank(note){
      var n=(note||"").toLowerCase();
      if(n==="best") return 0;
      if(n==="second best") return 1;
      return 2;
    }
    Object.keys(byCat).forEach(function(k){
      byCat[k].forEach(function(row,i){ row._i=i; });
      byCat[k].sort(function(a,b){
        var d=rank(a.it.note)-rank(b.it.note);
        return d!==0 ? d : a._i-b._i;
      });
    });
    Object.keys(byCat).sort(function(a,b){
      var ia=CATO.indexOf(a), ib=CATO.indexOf(b);
      return (ia<0?99:ia)-(ib<0?99:ib);
    }).forEach(function(catName){
      var list=byCat[catName], isAcc=/accessor/i.test(catName);
      var cinfo=carry[catName]||null, isCarry=!!cinfo;
      var blk=el("div","catblock"+(isAcc?" acc-block":"")+(isCarry?" carry-block":""));
      var h4=el("h4",null,catName);
      if(list.some(function(r){ return rank(r.it.note)<2; }))
        h4.appendChild(el("span","rankhint","best first"));
      h4.appendChild(el("span","cnt",String(list.length)));
      blk.appendChild(h4);
      if(isCarry){
        var only = list.every(function(r){ return r.mod===cinfo.kind; });
        var txt;
        if(cinfo.kind==="_tharmour"){
          txt = "Thorium sets here come from " + cinfo.src + " \u2014 its class guide skips armour at this stage.";
        } else {
          txt = (only ? "The guides list no new " : "No new ") + catName.toLowerCase()
              + " here \u2014 the " + (only ? "" : "greyed ") + "sets carry over from " + cinfo.src + ".";
        }
        blk.appendChild(el("p","carrynote", txt));
      }
      var ul=el("ul","gearlist");
      list.forEach(function(row){
        var it=row.it, srcMod=(row.mod==="_carry"?"vanilla":(row.mod==="_tharmour"?"thorium":row.mod));
        var node = it.url ? el("a","gear") : el("span","gear");
        node.style.setProperty("--src", MC[srcMod]||"#7d85ab");
        node.dataset.item = it.name;
        if(it.url){ node.href=it.url; node.target="_blank"; node.rel="noopener noreferrer"; }
        var sp=SP[it.name];
        if(sp){ var b2=el("span","gsp"); var im=new Image(); im.src=sp; im.alt=""; im.className="px"; im.loading="lazy"; b2.appendChild(im); node.appendChild(b2); }
        node.appendChild(document.createTextNode(it.name));
        if(it.note){
          var r=rank(it.note);
          node.appendChild(el("span", r<2 ? "qual best" : "qual", it.note));
          if(r<2) node.classList.add("is-best");
        }
        var li=el("li"); li.appendChild(node); ul.appendChild(li);
      });
      blk.appendChild(ul);
      card.appendChild(blk);
    });
    grid.appendChild(card);
  });
}
/* ---------- hover stat card ---------- */
var SC=el("div"); SC.id="statcard"; SC.setAttribute("data-show","0"); document.body.appendChild(SC);

function buildStat(name){
  var s=STATS[name]||{};
  SC.textContent="";
  var h=el("div","sc-h");
  var sp=SP[name];
  if(sp){ var box=el("span","sc-sp"); var im=new Image(); im.src=sp; im.alt=""; im.className="px"; box.appendChild(im); h.appendChild(box); }
  var t=el("div");
  t.appendChild(el("h5",null,name));
  if(s.kind) t.appendChild(el("div","sc-kind",s.kind));
  h.appendChild(t); SC.appendChild(h);

  var rows=[];
  if(s.damage) rows.push(["Damage", s.damage + (s.dtype ? "  " + s.dtype : ""), true]);
  if(s.defense) rows.push(["Defense", s.defense, false]);
  if(s.speed) rows.push(["Speed", s.speed + (s.use ? "  (" + s.use + ")" : ""), false]);
  else if(s.use) rows.push(["Use time", s.use, false]);
  if(s.knockback) rows.push(["Knockback", s.knockback, false]);
  if(s.crit) rows.push(["Crit", s.crit, false]);
  if(s.mana) rows.push(["Mana", s.mana, false]);
  if(s.velocity) rows.push(["Velocity", s.velocity, false]);
  if(rows.length){
    var dl=el("dl","sc-rows");
    rows.forEach(function(r){
      var dd=el("dd",null,String(r[1]));
      if(r[2]) dd.className="dmg";
      dl.appendChild(el("dt",null,r[0])); dl.appendChild(dd);
    });
    SC.appendChild(dl);
  }
  if(s.setbonus) SC.appendChild(el("p","sc-bonus","Set bonus: "+s.setbonus));
  if(s.tip) SC.appendChild(el("p","sc-tip",s.tip));
  if(!rows.length && !s.tip && !s.setbonus)
    SC.appendChild(el("p","sc-none","No stats published on the source wiki."));
}

function placeStat(x,y){
  var pad=14, w=SC.offsetWidth, h=SC.offsetHeight;
  var lx=x+pad, ly=y+pad;
  if(lx+w>window.innerWidth-8) lx=Math.max(8, x-w-pad);
  if(ly+h>window.innerHeight-8) ly=Math.max(8, y-h-pad);
  SC.style.left=lx+"px"; SC.style.top=ly+"px";
}
document.addEventListener("mouseover",function(ev){
  var t=ev.target.closest && ev.target.closest(".gear");
  if(!t||!t.dataset.item) return;
  buildStat(t.dataset.item); placeStat(ev.clientX,ev.clientY);
  SC.setAttribute("data-show","1");
});
document.addEventListener("mousemove",function(ev){
  if(SC.getAttribute("data-show")!=="1") return;
  var t=ev.target.closest && ev.target.closest(".gear");
  if(t) placeStat(ev.clientX,ev.clientY); else SC.setAttribute("data-show","0");
});
document.addEventListener("scroll",function(){ SC.setAttribute("data-show","0"); }, true);
// keyboard: focusing a linked pill shows the same card
document.addEventListener("focusin",function(ev){
  var t=ev.target.closest && ev.target.closest(".gear");
  if(!t||!t.dataset.item) return;
  var r=t.getBoundingClientRect();
  buildStat(t.dataset.item); placeStat(r.left, r.bottom-14);
  SC.setAttribute("data-show","1");
});
document.addEventListener("focusout",function(){ SC.setAttribute("data-show","0"); });

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
