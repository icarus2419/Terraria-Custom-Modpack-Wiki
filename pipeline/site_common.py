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

TABS = [("index.html",     "Home"),
        ("tinkerers.html", "Tinkerer's Workshop"),
        ("recipes.html",   "All Recipes"),
        ("loadouts.html",  "Loadouts")]

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
