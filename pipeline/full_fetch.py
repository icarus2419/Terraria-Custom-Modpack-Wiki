import json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import items as I
BASE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(BASE, "stations"); os.makedirs(OUT, exist_ok=True)

WIKIS = {"vanilla":"terraria.wiki.gg","thorium":"thoriummod.wiki.gg","fargo":"fargosmods.wiki.gg",
         "spirit":"spiritmod.wiki.gg","fables":"calamityfables.wiki.gg","stars":"starsabovemod.wiki.gg"}
LANG = {"cs","it","ja","nl","no","tr","yue","de","fr","es","pl","pt","ru","uk","zh","ko","hu","vi"}
SKIP = re.compile(r"/(register|Register|tabber|doc)$")

def clean(titles, pfx="Recipes/"):
    out=[]
    for t in titles:
        if not t.startswith(pfx): continue
        if SKIP.search(t): continue
        seg=t.split("/")[-1]
        if seg in LANG: continue
        out.append(t)
    return sorted(set(out))

def discover(host):
    d=I.api(host,{"action":"query","list":"prefixsearch","pssearch":"Recipes/","pslimit":"200",
                  "format":"json","formatversion":"2"})
    a=[p["title"] for p in (d or {}).get("query",{}).get("prefixsearch",[])]
    d2=I.api(host,{"action":"query","list":"allpages","apprefix":"Recipes/","aplimit":"200",
                   "format":"json","formatversion":"2"})
    b=[p["title"] for p in (d2 or {}).get("query",{}).get("allpages",[])]
    res=clean(a+b)
    sr=[]
    if host=="spiritmod.wiki.gg":
        d3=I.api(host,{"action":"query","list":"allpages","apprefix":"Spirit Reforged/Recipes/",
                       "aplimit":"200","format":"json","formatversion":"2"})
        sr=clean([p["title"] for p in (d3 or {}).get("query",{}).get("allpages",[])],
                 "Spirit Reforged/Recipes/")
    return res, sr

def fetch(job):
    mod, host, title = job
    safe = re.sub(r"[^A-Za-z0-9]+","_", "%s__%s" % (mod, title))
    path = os.path.join(OUT, safe + ".json")
    if os.path.exists(path):
        return (mod, host, title, path, "cached")
    time.sleep(0.8)
    d = I.api(host, {"action":"parse","page":title,"prop":"text","formatversion":"2","format":"json"})
    if not d or "parse" not in d: return (mod, host, title, None, "fail")
    json.dump(d, open(path,"w"))
    return (mod, host, title, path, "ok")

if __name__ == "__main__":
    plan=[]
    for mod, host in WIKIS.items():
        res, sr = discover(host)
        for t in res: plan.append((mod, host, t))
        for t in sr:  plan.append(("spirit_reforged", host, t))
        sys.stderr.write("%s: %d stations (+%d reforged)\n" % (mod, len(res), len(sr)))
    json.dump([{"mod":m,"host":h,"title":t} for m,h,t in plan],
              open(os.path.join(BASE,"station_plan.json"),"w"), indent=1)
    print("total station pages to fetch:", len(plan))
    done=0
    import time
    with ThreadPoolExecutor(max_workers=2) as ex:
        for mod,host,title,path,st in ex.map(fetch, plan):
            done+=1
            if st=="fail": sys.stderr.write("  FAIL %s %s\n"%(mod,title))
            if done%20==0: sys.stderr.write("  ...%d/%d\n"%(done,len(plan)))
    print("fetched into", OUT)
