"""Downloads a sprite for every boss and embeds it, so the page still works offline."""
import base64, json, os, re, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boss_fetch as F, bosses as B
BASE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(BASE, "boss_sprites.json")

D    = json.load(open(os.path.join(BASE, "bosses.json"), encoding="utf-8"))
have = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}

# a boss with no image on its page: try the obvious file names before giving up
def candidates(b):
    c = [b["img"]] if b["img"] else []
    for ext in (".png", ".gif"):
        c.append(b["name"] + ext)
        c.append(b["name"] + " (Map icon)" + ext)
    return [x for x in c if x]

want = [b for b in D["bosses"] if b["name"] not in have]
print("%d bosses | %d already have a sprite | resolving %d" % (
      len(D["bosses"]), len(have), len(want)), flush=True)

urls, cache_p = {}, os.path.join(F.OUT, "imageurls.json")
cache = json.load(open(cache_p, encoding="utf-8")) if os.path.exists(cache_p) else {}
for mod in B.MODS:
    host  = B.HOST[mod]
    files = []
    for b in want:
        if b["mod"] != mod: continue
        files += [f for f in candidates(b) if (host + "|" + f) not in cache]
    files = sorted(set(files))
    if files:
        got = F.batched_imageinfo(host, files)
        for f, u in got.items(): cache[host + "|" + f] = u
        json.dump(cache, open(cache_p, "w", encoding="utf-8"))
for b in want:
    got = [cache.get(b["host"] + "|" + f) for f in candidates(b)]
    got = [u for u in got if u]
    if got: urls[b["name"]] = got
print("resolved image URLs for %d/%d" % (len(urls), len(want)), flush=True)

def get(kv):
    """Walk the candidates in order -- the headline art for a few bosses is a multi-megabyte
    animation, so fall through to the map icon rather than shipping nothing."""
    n, opts = kv
    for u in opts:
        for _ in range(2):
            try:
                req = urllib.request.Request(u, headers={"User-Agent":
                      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
                with urllib.request.urlopen(req, timeout=40) as r:
                    raw = r.read()
                    ct  = r.headers.get("Content-Type", "image/png").split(";")[0].strip()
                if len(raw) > 400000: break
                return n, "data:%s;base64,%s" % (ct, base64.b64encode(raw).decode())
            except Exception:
                pass
    return n, None

with ThreadPoolExecutor(max_workers=10) as ex:
    for n, d in ex.map(get, urls.items()):
        if d: have[n] = d
json.dump(have, open(OUT, "w"))
missing = [b["name"] for b in D["bosses"] if b["name"] not in have]
print("boss sprites: %d/%d | %.1f MB" % (len(have), len(D["bosses"]),
      sum(len(v) for v in have.values())/1048576))
if missing: print("no sprite:", missing)
