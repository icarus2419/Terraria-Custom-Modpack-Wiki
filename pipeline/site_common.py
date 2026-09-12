"""Shared chrome for every page of the wiki: nav bar, theme toggle, and their styles."""

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
.sitenav .brand .brandmark{flex:none; display:block; margin-right:1px}
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
/* ---- the theme toggle ----
   It is the two items the palette is sampled from, not a sun and a moon: the soul you
   are looking at is the soul the page is currently made of. Both sprites are always in
   the DOM and cross-fade, so there is no flash of a swapped src on click. */
.themetoggle{
  display:inline-flex; align-items:center; gap:7px; flex:none; cursor:pointer;
  font-family:"Pixelify Sans",sans-serif; font-size:11.5px; letter-spacing:.04em;
  color:var(--ink-2); background:var(--surface-2);
  border:1px solid var(--line-strong); border-radius:100px;
  padding:4px 11px 4px 6px; margin-left:10px; white-space:nowrap;
}
.themetoggle:hover{color:var(--brass); border-color:var(--brass); box-shadow:var(--glow-soft)}
.themetoggle .soulwrap{position:relative; width:16px; height:16px; flex:none; display:block}
.themetoggle .soul{
  position:absolute; inset:0; width:16px; height:16px; display:block;
  image-rendering:pixelated; image-rendering:crisp-edges;
}
.themetoggle .soul.light{opacity:0}
:root[data-theme="light"] .themetoggle .soul.night{opacity:0}
:root[data-theme="light"] .themetoggle .soul.light{opacity:1}
@media (prefers-reduced-motion:no-preference){
  .themetoggle{transition:color .14s ease, border-color .14s ease, box-shadow .14s ease}
  .themetoggle .soul{transition:opacity .26s ease}
}
@media (max-width:700px){ .sitenav .navnote{display:none} .sitenav a.tab{padding:9px 10px} }
@media (max-width:460px){ .themetoggle .tlabel{display:none} .themetoggle{padding:4px 6px} }
</style>
"""

# in the order a player actually needs them: what to fight, what to wear, what to make
TABS = [("index.html",     "Home"),
        ("bosses.html",    "Boss Order"),
        ("loadouts.html",  "Loadouts"),
        ("recipes.html",   "All Recipes"),
        ("tinkerers.html", "Tinkerer's Workshop"),
        ("stars.html",     "Stars Above")]

def nav(active, note=""):
    import logo
    out = ['<nav class="sitenav"><div class="wrap sitenav-in">',
           '<a class="brand" href="index.html">' + logo.mark(20)
           + 'Joseph\'s Modpack Wiki</a>']
    for href, label in TABS:
        cur = ' aria-current="page"' if href == active else ""
        out.append('<a class="tab" href="%s"%s>%s</a>' % (href, cur, label))
    out.append('<span class="navspacer"></span>')
    if note: out.append('<span class="navnote">%s</span>' % note)
    out.append(theme_button())
    out.append("</div></nav>")
    return "".join(out)


def theme_button():
    """Sits last in the nav, so it lands top right on every page."""
    import souls
    return ('<button class="themetoggle" type="button" id="themetoggle" '
            'aria-pressed="false" aria-label="Switch theme" title="Switch theme">'
            '<span class="soulwrap">'
            + souls.img("night", 16, "soul night")
            + souls.img("light", 16, "soul light")
            + '</span><span class="tlabel">Night</span></button>')


# The theme, decided before the stylesheet is parsed so the page never paints the wrong
# one and then corrects itself. Dark is the CSS default and needs no attribute; only a
# stored preference for light sets one. Nothing here touches the network or the server.
THEME_BOOT = """
<script>
(function(){
"use strict";
var K="theme", R=document.documentElement;
try{ if(localStorage.getItem(K)==="light") R.setAttribute("data-theme","light"); }catch(e){}
function cur(){ return R.getAttribute("data-theme")==="light" ? "light" : "dark"; }
function paint(){
  var b=document.getElementById("themetoggle"); if(!b) return;
  var t=cur();
  b.setAttribute("aria-pressed", t==="light" ? "true" : "false");
  b.setAttribute("aria-label", "Switch to the "+(t==="dark"?"light":"dark")+" theme");
  b.title = t==="dark" ? "Soul of Night \u2014 switch to the light theme"
                       : "Soul of Light \u2014 switch to the dark theme";
  var l=b.querySelector(".tlabel"); if(l) l.textContent = t==="dark" ? "Night" : "Light";
}
function boot(){
  var b=document.getElementById("themetoggle"); if(!b) return;
  b.addEventListener("click", function(){
    var next = cur()==="dark" ? "light" : "dark";
    R.classList.add("theming");
    if(next==="light") R.setAttribute("data-theme","light");
    else R.removeAttribute("data-theme");
    try{ localStorage.setItem(K, next); }catch(e){}
    paint();
    setTimeout(function(){ R.classList.remove("theming"); }, 320);
  });
  paint();
}
if(document.readyState==="loading") document.addEventListener("DOMContentLoaded", boot);
else boot();
})();
</script>
"""


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


# ---------------------------------------------------------------------------
# Per-page head: language, description, and the tags that build a link preview
# when someone drops the URL into Discord or a chat. Without these a shared link
# is a bare URL with no title, which is most of how this site gets passed around.
# ---------------------------------------------------------------------------
SITE = "https://josephwiki.pages.dev"

def head(page, title, description):
    """Everything above the stylesheet. Emits the doctype and <html lang> too, which
    no page had -- a screen reader could not tell what language it was reading."""
    url = SITE + ("" if page == "index.html" else "/" + page.replace(".html", ""))
    esc = lambda t: (t.replace("&", "&amp;").replace("<", "&lt;")
                      .replace('"', "&quot;"))
    t, d = esc(title), esc(description)
    return ('<!doctype html>\n<html lang="en">\n'
            '<meta charset="utf-8">\n'
            '<meta name="description" content="%s">\n'
            '<meta property="og:type" content="website">\n'
            '<meta property="og:site_name" content="Joseph\'s Modpack Wiki">\n'
            '<meta property="og:title" content="%s">\n'
            '<meta property="og:description" content="%s">\n'
            '<meta property="og:url" content="%s">\n'
            '<meta name="twitter:card" content="summary">\n'
            '<meta name="twitter:title" content="%s">\n'
            '<meta name="twitter:description" content="%s">\n'
            % (d, t, d, url, t, d)) + THEME_BOOT


# ---------------------------------------------------------------------------
# The one place the mod palette is defined.
#
# It used to be declared in six files. Two of them drifted into meaning something
# else entirely (#3f9e8c was both Thorium and the All Recipes card), and a seventh
# copy inside full_wiki_js.html was missed when the rest were corrected. Colour is
# the only thing on this site that carries data, so it gets a single source.
#
# Chosen by measurement, not taste: every pair is >=124 apart perceptually, nothing
# is within 173 of the brass the UI uses for its own voice, and each clears 3.5:1 on
# the surface it sits on. Terraria is neutral because it is the base game, not a mod
# competing for a hue.
# ---------------------------------------------------------------------------
MODCOL = {
    "vanilla":         "#989ea3",   # neutral: the base game
    "thorium":         "#3f9e8c",   # teal
    "fargo":           "#c9552f",   # rust
    "spirit":          "#5a80c9",   # blue
    "spirit_reforged": "#7a5cc4",   # violet
    "fables":          "#b8518d",   # rose
    "stars":           "#c2a1e8",   # lilac
}

def modcol_js(name="MODCOL"):
    """The same palette as a JS declaration, so no page hand-copies it."""
    import json as _j
    return "var %s=%s;" % (name, _j.dumps(MODCOL, separators=(",", ":")))
