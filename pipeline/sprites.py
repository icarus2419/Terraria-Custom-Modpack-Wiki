import base64, json, os, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
BASE = os.path.dirname(os.path.abspath(__file__))
items = json.load(open(os.path.join(BASE, "items.json")))
urls = {}
for k, v in items.items():
    if v.get("img"): urls[k] = v["img"]
print("sprites to fetch:", len(urls))

def get(kv):
    k, u = kv
    for attempt in range(3):
        try:
            req = urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
            with urllib.request.urlopen(req, timeout=45) as r:
                b = r.read()
                ct = r.headers.get("Content-Type","image/png").split(";")[0].strip()
            if len(b) > 220000: return k, None
            return k, "data:%s;base64,%s" % (ct, base64.b64encode(b).decode())
        except Exception as e:
            if attempt == 2:
                sys.stderr.write("fail %s\n" % u[:90])
    return k, None

out = {}
with ThreadPoolExecutor(max_workers=12) as ex:
    for k, d in ex.map(get, urls.items()):
        if d: out[k] = d
json.dump(out, open(os.path.join(BASE, "sprites.json"), "w"))
tot = sum(len(v) for v in out.values())
print("got %d/%d | payload %.1f KB" % (len(out), len(urls), tot/1024))
