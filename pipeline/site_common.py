"""Shared chrome for every page of the wiki: nav bar + its styles."""

NAV_CSS = """
<style>
.sitenav{
  position:sticky; top:0; z-index:60; background:var(--surface);
  border-bottom:1px solid var(--line); box-shadow:0 1px 0 rgba(0,0,0,.04);
}
.sitenav-in{display:flex; align-items:center; gap:6px; padding:0; flex-wrap:wrap}
.sitenav .brand{
  display:flex; align-items:center; gap:8px; font-family:"Pixelify Sans",sans-serif;
  font-size:14px; font-weight:600; color:var(--ink); text-decoration:none;
  padding:9px 14px 9px 0; margin-right:6px; white-space:nowrap;
}
.sitenav .brand:hover{color:var(--brass)}
.sitenav .brand .dot{width:9px;height:9px;border-radius:2px;background:var(--brass);flex:none}
.sitenav a.tab{
  font-family:"Pixelify Sans",sans-serif; font-size:12.5px; letter-spacing:.03em;
  color:var(--ink-2); text-decoration:none; padding:10px 13px; border-bottom:2px solid transparent;
  white-space:nowrap;
}
.sitenav a.tab:hover{color:var(--ink); background:var(--surface-2)}
.sitenav a.tab[aria-current="page"]{color:var(--brass); border-bottom-color:var(--brass); font-weight:600}
.sitenav .navspacer{flex:1}
.sitenav .navnote{
  font-family:"JetBrains Mono",monospace; font-size:10.5px; color:var(--ink-3);
  padding-right:2px; white-space:nowrap;
}
@media (max-width:700px){ .sitenav .navnote{display:none} .sitenav a.tab{padding:9px 10px} }
</style>
"""

# in the order a player actually needs them: what to fight, what to wear, what to make
TABS = [("index.html",     "Home"),
        ("bosses.html",    "Boss Order"),
        ("loadouts.html",  "Loadouts"),
        ("recipes.html",   "All Recipes"),
        ("tinkerers.html", "Tinkerer's Workshop")]

def nav(active, note=""):
    out = ['<nav class="sitenav"><div class="wrap sitenav-in">',
           '<a class="brand" href="index.html"><span class="dot"></span>Joseph\'s Modpack Wiki</a>']
    for href, label in TABS:
        cur = ' aria-current="page"' if href == active else ""
        out.append('<a class="tab" href="%s"%s>%s</a>' % (href, cur, label))
    out.append('<span class="navspacer"></span>')
    if note: out.append('<span class="navnote">%s</span>' % note)
    out.append("</div></nav>")
    return "".join(out)


# ---------------------------------------------------------------------------
# Shared progression state.
#
# The boss checklist writes which bosses you have beaten into localStorage. Every other
# page reads it back from there, so the whole site knows where you are in the run: which
# checkpoint to gear for, and whether Hardmode content is in reach yet. It never leaves
# the browser.
# ---------------------------------------------------------------------------
import json as _json, os as _os

def _boss_summary():
    """name -> [band, loadout stage, order] for the whole roster; small enough to inline."""
    here = _os.path.dirname(_os.path.abspath(__file__))
    for p in (_os.path.join(here, "bosses.json"),
              _os.path.join(_os.path.dirname(here), "data", "bosses.json")):
        if _os.path.exists(p):
            d = _json.load(open(p, encoding="utf-8"))
            return {b["name"]: [b["band"], b["stage"], b["order"]] for b in d["bosses"]}
    return {}

PROGRESS_CSS = """
<style>
.runbar{background:var(--surface-2); border-bottom:1px solid var(--line)}
.runbar-in{display:flex; align-items:center; gap:10px; flex-wrap:wrap; padding:7px 0; font-size:12.5px}
.runbar .tag{font-family:"Pixelify Sans",sans-serif; font-size:9.5px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--ink-3)}
.runbar .bit{color:var(--ink-2)}
.runbar .bit b{color:var(--ink); font-weight:600}
.runbar .dot{color:var(--line-strong)}
.runbar .era{margin:0}
.runbar .sp{flex:1}
.runbar a.go, .runbar button.go{font:inherit; font-size:11.5px; cursor:pointer; text-decoration:none;
  padding:3px 11px; border-radius:100px; border:1px solid var(--line-strong); color:var(--ink-2);
  background:var(--surface); white-space:nowrap}
.runbar a.go:hover, .runbar button.go:hover{border-color:var(--brass); color:var(--brass)}
.runbar button.go[aria-pressed="true"]{background:var(--brass-soft); border-color:var(--brass);
  color:var(--brass); font-weight:600}
.runbar button.go[disabled]{opacity:.5; cursor:default}
.runbar .track{width:110px; height:6px; border-radius:3px; background:var(--surface-3); overflow:hidden}
.runbar .track i{display:block; height:100%; background:var(--brass)}
@media (max-width:640px){ .runbar .track{display:none} }
</style>
"""

_PROGRESS_TPL = """
<script id="bosssummary" type="application/json">__SUMMARY__</script>
<script>
(function(){
"use strict";
var SUM=JSON.parse(document.getElementById("bosssummary").textContent);
var KEY="bosses.done.v1";
function read(){ try{ return JSON.parse(localStorage.getItem(KEY)||"{}"); }catch(e){ return {}; } }

function state(){
  var done=read(), names=Object.keys(SUM);
  var live=names.filter(function(n){ var b=SUM[n][0]; return b!=="mini" && b!=="seed"; });
  live.sort(function(a,b){ return SUM[a][2]-SUM[b][2]; });
  var beaten=names.filter(function(n){ return done[n]; }).length;
  // where you are is the furthest boss you have beaten, not the first you have not:
  // skipping an optional modded boss should not drag the whole site back to the start
  var far=-1;
  names.forEach(function(n){ if(done[n] && SUM[n][2]>far) far=SUM[n][2]; });
  var next=null;
  for(var i=0;i<live.length;i++){ if(!done[live[i]] && SUM[live[i]][2]>far){ next=live[i]; break; } }
  if(!next) for(var j=0;j<live.length;j++){ if(!done[live[j]]){ next=live[j]; break; } }
  return {done:done, beaten:beaten, total:names.length, next:next,
          stage: next ? SUM[next][1] : "endgame",
          hardmode: !!done["Wall of Flesh"],
          started: beaten>0};
}
function el(t,c,x){var e=document.createElement(t); if(c)e.className=c; if(x!=null)e.textContent=x; return e;}

window.PackProgress={state:state, summary:SUM, key:KEY, page:"__PAGE__"};

window.PackProgress.mountBar=function(host, extra){
  var s=state();
  host.textContent="";
  var wrap=el("div","wrap runbar-in");
  wrap.appendChild(el("span","tag","Your run"));
  if(!s.started){
    var p=el("span","bit");
    p.appendChild(document.createTextNode("No bosses ticked off yet \\u2014 "));
    var a=el("a",null,"start the checklist"); a.href="bosses.html";
    p.appendChild(a);
    p.appendChild(document.createTextNode(", and every page follows along."));
    wrap.appendChild(p);
  } else {
    var t=el("span","track"), i=el("i");
    i.style.width=(s.beaten/s.total*100)+"%"; t.appendChild(i);
    wrap.appendChild(t);
    var b1=el("span","bit");
    b1.appendChild(el("b",null,String(s.beaten)));
    b1.appendChild(document.createTextNode(" of "+s.total+" bosses beaten"));
    wrap.appendChild(b1);
    wrap.appendChild(el("span","dot","\\u00b7"));
    var b2=el("span","bit");
    b2.appendChild(document.createTextNode("next up "));
    b2.appendChild(el("b",null, s.next || "nothing left"));
    wrap.appendChild(b2);
    wrap.appendChild(el("span","era "+(s.hardmode?"hard":"pre"),
                        s.hardmode?"hardmode":"pre-hardmode"));
  }
  wrap.appendChild(el("span","sp"));
  if(extra) extra(wrap, s);
  if(window.PackProgress.page!=="bosses.html"){
    var g=el("a","go","Boss order \\u2192"); g.href="bosses.html"; wrap.appendChild(g);
  }
  host.appendChild(wrap);
  return s;
};

/* A page that wants its own control in the bar sets window.RUNBAR_EXTRA before this runs. */
function boot(){
  var h=document.getElementById("runbar");
  if(h) window.PackProgress.mountBar(h, window.RUNBAR_EXTRA||null);
}
window.PackProgress.refresh=boot;
if(document.readyState==="loading") document.addEventListener("DOMContentLoaded", boot);
else boot();
})();
</script>
"""

def progress_js(page):
    summary = _json.dumps(_boss_summary(), separators=(",", ":")).replace("<", "\\u003c")
    return _PROGRESS_TPL.replace("__SUMMARY__", summary).replace("__PAGE__", page)

def runbar():
    return '<div class="runbar" id="runbar"></div>'
