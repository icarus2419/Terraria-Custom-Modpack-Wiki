import base64, json, os, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
BASE = os.path.dirname(os.path.abspath(__file__))
idx = json.load(open(os.path.join(BASE, "full_index.json")))
SP  = os.path.join(BASE, "full_sprites.json")
sp  = json.load(open(SP)) if os.path.exists(SP) else {}
# seed from the v1 sprite set where the identity matches
old = json.load(open(os.path.join(BASE, "sprites.json")))
for k, v in old.items():
    if k in idx and k not in sp: sp[k] = v

need = [(k, v["img"]) for k, v in idx.items() if v.get("img") and k not in sp]
print("sprites: have %d, need %d" % (len(sp), len(need)), flush=True)

def get(kv):
    k, u = kv
    for a in range(3):
        try:
            req = urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
            with urllib.request.urlopen(req, timeout=40) as r:
                b = r.read(); ct = r.headers.get("Content-Type","image/png").split(";")[0].strip()
            if len(b) > 200000: return k, None
            return k, "data:%s;base64,%s" % (ct, base64.b64encode(b).decode())
        except Exception:
            if a == 2:
                try:                                    # stale ?hash -> try bare filename
                    u2 = u.split("?")[0]
                    req = urllib.request.Request(u2, headers={"User-Agent":"Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=40) as r:
                        b = r.read()
                    return k, "data:image/png;base64," + base64.b64encode(b).decode()
                except Exception: return k, None
    return k, None

done = 0
with ThreadPoolExecutor(max_workers=14) as ex:
    for k, d in ex.map(get, need):
        done += 1
        if d: sp[k] = d
        if done % 400 == 0:
            json.dump(sp, open(SP, "w")); print("  %d/%d" % (done, len(need)), flush=True)
json.dump(sp, open(SP, "w"))
tot = sum(len(v) for v in sp.values())
print("sprites %d/%d | payload %.1f MB" % (len(sp), len(idx), tot/1048576), flush=True)
