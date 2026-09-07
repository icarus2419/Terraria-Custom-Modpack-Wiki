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

# A soulfire flame, in the crimson the rest of the site runs on, so the mark belongs to the
# palette rather than competing with it. The pale core keeps it reading as fire at 16px --
# a flat crimson blob does not.
INK = {"F": "#c96a7e",   # flame
       "y": "#f0c4ce",   # hot core
       "S": "#4f3239",   # handle
       "d": "#2b1c21"}   # handle shadow

# No tile behind the mark: a solid ground reads as a black box in the browser tab.
# The flame is mid-orange, so it holds up on light and dark chrome without one.

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

def _png(size):
    """A transparent PNG of the mark at `size` px. The grid is 16 wide, so any multiple of
    16 is an exact nearest-neighbour scale and stays perfectly sharp."""
    from PIL import Image
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = im.load()
    for y, row in enumerate(GRID):
        for x, c in enumerate(row):
            if c == ".": continue
            h = INK[c].lstrip("#")
            px[x, y] = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
    if size != 16:
        im = im.resize((size, size), Image.NEAREST)
    import io
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return buf.getvalue()

def png_datauri(size):
    return "data:image/png;base64," + base64.b64encode(_png(size)).decode()

def head_links():
    """Transparent PNGs at the sizes a browser actually asks for."""
    return ('<link rel="icon" type="image/png" sizes="16x16" href="%s">\n'
            '<link rel="icon" type="image/png" sizes="32x32" href="%s">\n'
            '<link rel="apple-touch-icon" sizes="180x180" href="%s">\n'
            '<meta name="theme-color" content="#0a070c">\n'
            % (png_datauri(16), png_datauri(32), png_datauri(176)))

BRAND_CSS = """
<style>
.sitenav .brand .brandmark{flex:none; display:block}
</style>
"""
