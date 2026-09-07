"""The site mark: a pixel torch, drawn on the 16x16 grid a Terraria item sprite uses.

Everything else here is embedded rather than fetched, so the mark is too -- the nav gets it
as inline SVG, the tab as a data: URI. No extra files, no requests, still works offline.

The flame is drawn wide and solid on purpose: a torch outline thin enough to look elegant at
96px disappears at 16px, which is the size a favicon actually lives at.
"""
import base64

GRID = [
    "................",
    ".......FF.......",
    "......FFFF......",
    ".....FFyyFF.....",
    "....FFyyyyFF....",
    "....FFyyyyFF....",
    "...FFyyyyyyFF...",
    "...FFyyyyyyFF...",
    "...FFFyyyyFFF...",
    "....FFFFFFFF....",
    ".....FFFFFF.....",
    "......SSSS......",
    "......SSSS......",
    "......SSSS......",
    "......SSSS......",
    "......dddd......",
]

INK = {"F": "#ff8a2b",   # flame
       "y": "#ffe08a",   # hot core
       "S": "#8a5a33",   # handle
       "d": "#4a3120"}   # handle shadow

GROUND = "#12121a"       # the tile behind the mark in the tab icon

def _rects(scale=1, dx=0, dy=0):
    """One rect per horizontal run: small file, hard edges."""
    out = []
    for y, row in enumerate(GRID):
        x = 0
        while x < len(row):
            c = row[x]
            if c == ".":
                x += 1; continue
            run = 1
            while x + run < len(row) and row[x + run] == c: run += 1
            out.append('<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>'
                       % (x * scale + dx, y * scale + dy, run * scale, scale, INK[c]))
            x += run
    return "".join(out)

def mark(size=20, cls="brandmark"):
    """Inline SVG for the nav, transparent so it sits on either theme."""
    return ('<svg class="%s" width="%d" height="%d" viewBox="0 0 16 16" '
            'shape-rendering="crispEdges" aria-hidden="true" focusable="false">%s</svg>'
            % (cls, size, size, _rects()))

def favicon_datauri():
    """Tab icon: the mark on a dark tile, so it reads on light and dark browser chrome."""
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" '
           'shape-rendering="crispEdges">'
           '<rect width="20" height="20" rx="4" fill="%s"/>%s</svg>'
           % (GROUND, _rects(scale=1, dx=2, dy=2)))
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

def head_links():
    d = favicon_datauri()
    return ('<link rel="icon" type="image/svg+xml" href="%s">\n'
            '<link rel="apple-touch-icon" href="%s">\n'
            '<meta name="theme-color" content="#101229">\n' % (d, d))

BRAND_CSS = """
<style>
.sitenav .brand .brandmark{flex:none; display:block}
</style>
"""
