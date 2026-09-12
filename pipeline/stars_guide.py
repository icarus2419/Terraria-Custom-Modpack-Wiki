"""The Stars Above's own Early Guide, and the icons its menu uses.

The Stars Above is the one mod in the pack that adds a system rather than just content:
a companion, a menu bound to an item, and four screens behind it. None of that is
discoverable from a recipe list, so the home page explains it -- and this fetches what
that explanation is built from, rather than anyone writing it from memory.

  python3 stars_guide.py        # -> ../data/stars_guide.json

The prose on the page is a plain-English summary of the wikitext this pulls; the page
links to the guide so the summary can be checked against its source.
"""
import base64, json, os, urllib.parse, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(os.path.dirname(BASE), "data", "stars_guide.json")
WIKI = "starsabovemod.wiki.gg"
API  = "https://%s/api.php?" % WIKI
UA   = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

# the four menu screens, plus the two permanent choices the disk makes you pick between
ICONS = ["Umbral_Icon.png", "Astral_Icon.png", "Stellar_Array_Icon.png",
         "Stellar_Nova_Icon.png", "Voyage_Icon.png", "Archive_Icon.png"]

def _get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        return r.read()

def wikitext(page):
    q = urllib.parse.urlencode({"action": "parse", "page": page,
                                "prop": "wikitext", "format": "json"})
    return json.loads(_get(API + q))["parse"]["wikitext"]["*"]

def icon(fname):
    q = urllib.parse.urlencode({"action": "query", "format": "json", "prop": "imageinfo",
                                "iiprop": "url", "titles": "File:" + fname})
    pages = json.loads(_get(API + q))["query"]["pages"]
    info = list(pages.values())[0].get("imageinfo")
    if not info: return None
    raw = _get(info[0]["url"])
    return "data:image/png;base64," + base64.b64encode(raw).decode()

# the pages the explainer's "how you get it" and "when" lines are drawn from
SYSTEM_PAGES = ["Stellar Array", "Stellar Novas", "Cosmic Voyages", "Key Items",
                "Essences", "Aspects"]

def portrait(fname, width=320, colors=128):
    """The twins, downscaled for the page.

    Nearest-neighbour because it is pixel art -- a smooth resample turns a 34 KB sprite into
    a 60 KB blur. FASTOCTREE because it is the one Pillow quantiser that keeps the alpha
    channel, and two thirds of this image is transparent.
    """
    import io
    from PIL import Image
    q = urllib.parse.urlencode({"action": "query", "format": "json", "prop": "imageinfo",
                                "iiprop": "url", "titles": "File:" + fname})
    pages = json.loads(_get(API + q))["query"]["pages"]
    info = list(pages.values())[0].get("imageinfo")
    if not info: return None
    im = Image.open(io.BytesIO(_get(info[0]["url"]))).convert("RGBA")
    h = round(im.height * width / im.width)
    im = im.resize((width, h), Image.NEAREST).quantize(colors=colors, method=Image.FASTOCTREE)
    buf = io.BytesIO(); im.save(buf, format="PNG", optimize=True)
    print("  %-24s %dx%d  %d B" % (fname, width, h, len(buf.getvalue())))
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def main():
    guide = wikitext("Early Guide")
    systems = {}
    for p in SYSTEM_PAGES:
        try:
            systems[p] = wikitext(p)
            print("  %-24s %d chars" % (p, len(systems[p])))
        except Exception as e:
            print("  %-24s FAILED %s" % (p, str(e)[:60]))
    icons = {}
    for f in ICONS:
        d = icon(f)
        key = f.replace("_Icon.png", "").lower()
        if d: icons[key] = d
        print("  %-24s %s" % (f, "%d B" % (len(d) * 3 // 4) if d else "MISSING"))
    twins = None
    try:
        twins = portrait("Familiar_Eridani_and_Asphodene.png")
    except Exception as e:
        print("  twins portrait FAILED %s" % str(e)[:60])
    out = {"source": "https://%s/wiki/Early_Guide" % WIKI,
           "twins": twins,
           "wiki": WIKI,
           "headings": [l.strip("= ").strip() for l in guide.splitlines()
                        if l.startswith("==") and l.strip().endswith("==")],
           "wikitext": guide,
           "systems": systems,
           "system_sources": {p: "https://%s/wiki/%s" % (WIKI, p.replace(" ", "_"))
                              for p in systems},
           "icons": icons}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)
    print("wrote %s | %d icons | guide %d chars | %d system pages"
          % (os.path.relpath(OUT, BASE), len(icons), len(guide), len(systems)))

if __name__ == "__main__":
    main()
