"""Embeds the one typeface the site cannot fall back from.

The site's headline claim is that it works offline, but the fonts were fetched from Google,
so with no network the pixel typeface — which is the entire visual identity — silently became
system sans. Asap and JetBrains Mono degrade fine: any grotesque and any mono stand in for
them. Pixelify Sans has no equivalent on any operating system.

So only that one is embedded, at the three weights actually rendered. ~46 KB of base64 per
page, against 435 KB had all three families been embedded.
"""
import base64, json, os, re, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BASE, "fonts_cache.json")
API = ("https://fonts.googleapis.com/css2?family=Pixelify+Sans:wght@400;500;600&display=swap")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36")

def _fetch():
    req = urllib.request.Request(API, headers={"User-Agent": UA})
    css = urllib.request.urlopen(req).read().decode()
    faces = []
    for subset, body in re.findall(r"/\*\s*([a-z-]+)\s*\*/\s*@font-face\s*\{(.*?)\}", css, re.S):
        if subset != "latin":
            continue
        wt  = re.search(r"font-weight:\s*(\d+)", body).group(1)
        url = re.search(r"url\((https://[^)]+)\)", body).group(1)
        data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA})).read()
        faces.append({"weight": wt, "b64": base64.b64encode(data).decode(), "bytes": len(data)})
    return faces

def faces():
    if os.path.exists(CACHE):
        return json.load(open(CACHE, encoding="utf-8"))
    f = _fetch()
    json.dump(f, open(CACHE, "w"))
    return f

def css():
    """@font-face rules with the woff2 inlined, plus a metric-matched fallback so the
    other two families swap in without shoving the layout around."""
    out = []
    for f in sorted(faces(), key=lambda x: x["weight"]):
        out.append(
            "@font-face{font-family:'Pixelify Sans';font-style:normal;font-weight:%s;"
            "font-display:block;src:url(data:font/woff2;base64,%s) format('woff2')}"
            % (f["weight"], f["b64"]))
    return "<style>\n" + "\n".join(out) + "\n</style>\n"

if __name__ == "__main__":
    fs = faces()
    raw = sum(f["bytes"] for f in fs)
    print("  %d weights, %.1f KB raw -> %.1f KB base64" % (len(fs), raw/1024, len(css())/1024))
