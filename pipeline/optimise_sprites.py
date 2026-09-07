"""Recompresses every embedded sprite, losslessly.

The sprites come straight off the wikis as whatever PNG the uploader happened to save:
mostly full RGBA, often at a compression level nobody chose. They are pixel art with a
handful of colours, so a palette PNG stores them far smaller.

A candidate is only accepted if it decodes to pixel-identical RGBA. Nothing here degrades
an image; if a smaller encoding cannot be proven identical, the original is kept.

Run it over the committed datasets, then re-run the generators.
"""
import base64, io, json, os, sys
from concurrent.futures import ProcessPoolExecutor
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
DATA = os.path.join(ROOT, "data")

def optimise(datauri):
    """Smaller data URI, or the original when nothing provably identical is smaller."""
    try:
        head, b64 = datauri.split(",", 1)
        raw = base64.b64decode(b64)
        im = Image.open(io.BytesIO(raw)).convert("RGBA")
    except Exception:
        return datauri
    ref = list(im.getdata())
    best = raw

    cands = []
    b = io.BytesIO(); im.save(b, format="PNG", optimize=True, compress_level=9)
    cands.append(b.getvalue())
    n = len(set(ref))
    if n <= 256:
        try:
            p = im.quantize(colors=max(2, n), method=Image.FASTOCTREE)
            b2 = io.BytesIO(); p.save(b2, format="PNG", optimize=True)
            cands.append(b2.getvalue())
        except Exception:
            pass

    for c in cands:
        if len(c) < len(best):
            try:
                if list(Image.open(io.BytesIO(c)).convert("RGBA").getdata()) == ref:
                    best = c
            except Exception:
                pass
    if len(best) >= len(raw):
        return datauri
    return "data:image/png;base64," + base64.b64encode(best).decode()

def walk(obj, sink):
    """Collect every data: URI in a nested structure, with a setter for each."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and v.startswith("data:image"):
                sink.append((v, lambda nv, o=obj, kk=k: o.__setitem__(kk, nv)))
            else:
                walk(v, sink)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, str) and v.startswith("data:image"):
                sink.append((v, lambda nv, o=obj, ii=i: o.__setitem__(ii, nv)))
            else:
                walk(v, sink)

FILES = ["full_site_data.json", "site_data.json", "boss_sprites.json", "loadout_sprites.json"]

if __name__ == "__main__":
    grand_before = grand_after = 0
    for name in FILES:
        path = os.path.join(DATA, name)
        if not os.path.exists(path):
            path = os.path.join(BASE, name)
            if not os.path.exists(path):
                print("  %-24s (not found, skipped)" % name); continue
        d = json.load(open(path, encoding="utf-8"))
        sink = []
        walk(d, sink)
        if not sink:
            print("  %-24s no sprites" % name); continue
        uris = [u for u, _ in sink]
        before = sum(len(u) for u in uris)
        # the same sprite often appears many times; optimise each distinct one once
        distinct = list({u for u in uris})
        with ProcessPoolExecutor() as ex:
            done = dict(zip(distinct, ex.map(optimise, distinct, chunksize=24)))
        for u, setter in sink:
            setter(done[u])
        after = sum(len(done[u]) for u in uris)
        json.dump(d, open(path, "w", encoding="utf-8"), separators=(",", ":"))
        grand_before += before; grand_after += after
        print("  %-24s %d sprites (%d distinct)  %.1f KB -> %.1f KB  (-%.0f%%)"
              % (name, len(sink), len(distinct), before/1024, after/1024,
                 (1 - after/before) * 100 if before else 0))
    if grand_before:
        print("  %-24s %.1f MB -> %.1f MB  (-%.0f%%)"
              % ("TOTAL", grand_before/1048576, grand_after/1048576,
                 (1 - grand_after/grand_before) * 100))
