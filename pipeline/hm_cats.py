import json, os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import items as I
BASE=os.path.dirname(os.path.abspath(__file__))
raw=json.load(open(os.path.join(BASE,"items.json")))

by_host={}
for k,v in raw.items():
    by_host.setdefault(v["host"],[]).append(v["title"])

jobs=[]
for host,titles in by_host.items():
    t=sorted(set(titles))
    for i in range(0,len(t),12): jobs.append((host,t[i:i+12]))

def run(job):
    host,titles=job
    params={"action":"query","prop":"categories","cllimit":"max","titles":"|".join(titles),
            "format":"json","formatversion":"2","redirects":"1"}
    pages={}; q={}
    for _ in range(30):                      # follow continuation, else pages come back empty
        d=I.api(host,params)
        if not d: break
        q=d.get("query",{}) or q
        for p2 in q.get("pages",[]):
            if p2.get("missing"): continue
            cur=pages.setdefault(p2["title"],[])
            for c in (p2.get("categories") or []):
                t=c["title"].replace("Category:","")
                if t not in cur: cur.append(t)
        if "continue" in d: params.update(d["continue"])
        else: break
    out={}
    nm={n["from"]:n["to"] for n in q.get("normalized",[])}
    rd={r["from"]:r["to"] for r in q.get("redirects",[])}
    res={}
    for t in titles:
        t2=rd.get(nm.get(t,t),nm.get(t,t)); res.setdefault(t2,[]).append(t)
    for ttl,cs in pages.items():
        for orig in res.get(ttl,[])+[ttl]:
            out["%s|%s"%(host,orig)]=cs
    sys.stderr.write("  %s +%d\n"%(host,len(out)))
    return host,out

allc={}
with ThreadPoolExecutor(max_workers=4) as ex:
    for host,out in ex.map(run,jobs): allc.update(out)
json.dump(allc,open(os.path.join(BASE,"item_categories.json"),"w"))
hm=[k for k,v in allc.items() if any("Hardmode-only" in c for c in v)]
print("categories fetched for %d/%d items" % (len(allc), len(raw)))
print("tagged 'Hardmode-only items': %d" % len(hm))
