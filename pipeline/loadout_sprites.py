import base64, json, os, urllib.request
from concurrent.futures import ThreadPoolExecutor
BASE = os.path.dirname(os.path.abspath(__file__))
L   = json.load(open(os.path.join(BASE,"loadouts.json")))
sp  = json.load(open(os.path.join(BASE,"full_sprites.json")))
idx = json.load(open(os.path.join(BASE,"full_index.json")))
OUT = os.path.join(BASE,"loadout_sprites.json")
have = json.load(open(OUT)) if os.path.exists(OUT) else {}

# reuse sprites already downloaded for the recipe browser, matched by item name
byname = {}
for k,v in idx.items():
    if k in sp: byname.setdefault(v["name"], sp[k])

need = {}
for st,cls in L["data"].items():
    for cl,mods in cls.items():
        for m,boxes in mods.items():
            for b in boxes:
                for it in b["items"]:
                    n = it["name"]
                    if n in have: continue
                    if n in byname: have[n] = byname[n]; continue
                    if it.get("img"): need[n] = it["img"]
print("reused %d | to fetch %d" % (len(have), len(need)), flush=True)

def get(kv):
    n,u = kv
    for a in range(3):
        try:
            req = urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
            with urllib.request.urlopen(req, timeout=40) as r:
                b = r.read(); ct = r.headers.get("Content-Type","image/png").split(";")[0].strip()
            if len(b) > 200000: return n, None
            return n, "data:%s;base64,%s" % (ct, base64.b64encode(b).decode())
        except Exception:
            if a == 2:
                try:
                    req = urllib.request.Request(u.split("?")[0], headers={"User-Agent":"Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=40) as r: b = r.read()
                    return n, "data:image/png;base64," + base64.b64encode(b).decode()
                except Exception: return n, None
    return n, None

done=0
with ThreadPoolExecutor(max_workers=12) as ex:
    for n,d in ex.map(get, need.items()):
        done+=1
        if d: have[n]=d
        if done % 200 == 0: json.dump(have, open(OUT,"w")); print("  %d/%d"%(done,len(need)), flush=True)
json.dump(have, open(OUT,"w"))
print("loadout sprites: %d | %.1f MB" % (len(have), sum(len(v) for v in have.values())/1048576), flush=True)
