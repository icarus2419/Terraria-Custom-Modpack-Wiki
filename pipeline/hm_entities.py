"""Resolve the NPCs/bosses an item drops from, and decide if they are Hardmode.

Catches items the wikis forget to tag - e.g. Soul of Might carries no `hardmode`
tag even though every other Soul does, but it only drops from The Destroyer.
"""
import json, os, re, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import items as I
BASE = os.path.dirname(os.path.abspath(__file__))

wt   = json.load(open(os.path.join(BASE, "wikitext_cache.json")))
raw  = json.load(open(os.path.join(BASE, "items.json")))
D    = json.load(open(os.path.join(BASE, "site_data.json")))

SRC_PAT = re.compile(
    r"(?:dropped by|drops? from|dropped from|obtained from|harvested from|summoned by)\s+"
    r"((?:(?:the|all|most|any)\s+)?(?:\[\[[^\]]+\]\][ ,/or]*){1,6})", re.I)
LINK = re.compile(r"\[\[([^\]|#]+)")

def entities_for(host, title):
    t = wt.get("%s|%s" % (host, title)) or ""
    lead = re.split(r"\n\s*==[^=]", t)[0]
    out = []
    for m in SRC_PAT.finditer(lead):
        for l in LINK.findall(m.group(1)):
            l = l.strip()
            if l and l.lower() not in ("enemies", "npcs", "bosses", "hardmode", "pre-hardmode"):
                out.append(l)
    return out

# --- collect candidate entities per host ---
cand = {}
for k, v in raw.items():
    for e in entities_for(v["host"], v["title"]):
        cand.setdefault(v["host"], set()).add(e)
print("candidate source entities:", {h: len(s) for h, s in cand.items()})

def batch(host, titles):
    out = {}
    params = {"action":"query","prop":"categories|revisions","cllimit":"max","rvprop":"content",
              "rvslots":"main","titles":"|".join(titles),"format":"json","formatversion":"2",
              "redirects":"1"}
    pages = {}
    for _ in range(20):
        d = I.api(host, params)
        if not d: break
        q = d.get("query", {})
        for p in q.get("pages", []):
            if p.get("missing"): continue
            rec = pages.setdefault(p["title"], {"cats": [], "wt": ""})
            for c in (p.get("categories") or []):
                t = c["title"].replace("Category:", "")
                if t not in rec["cats"]: rec["cats"].append(t)
            r = (p.get("revisions") or [{}])[0].get("slots", {}).get("main", {}).get("content", "")
            if r: rec["wt"] = r
        if "continue" in d: params.update(d["continue"])
        else: break
    for ttl, rec in pages.items():
        cats = " ".join(rec["cats"]).lower()
        body = rec["wt"]
        tags = re.search(r"\|\s*tags\s*=\s*([^\n|}]*)", body)
        tagl = (tags.group(1) if tags else "").lower()
        head = re.split(r"\n\s*==[^=]", body)[0][:900]
        strong = ("hardmode" in re.split(r"[/,]", tagl).__str__().lower() and
                  any(x.strip() == "hardmode" for x in re.split(r"[/,]", tagl)))
        catsig = [x for x in rec["cats"] if re.search(r"hardmode", x, re.I)]
        firstsent = re.split(r"(?<=\.)\s", re.sub(r"\{\{[^{}]*\}\}", " ", head))[0]
        leadhm = bool(re.search(r"\bis an? \[?\[?hardmode", firstsent, re.I))
        leadpre = bool(re.search(r"pre-\[?\[?hardmode", firstsent, re.I))
        out[ttl] = {"tags": tagl.strip(), "cats_hm": catsig, "strong_tag": strong,
                    "lead_hm": leadhm, "lead_pre": leadpre,
                    "hm": bool(strong or catsig or (leadhm and not leadpre))}
    return out

jobs = []
for host, s in cand.items():
    t = sorted(s)
    for i in range(0, len(t), 12): jobs.append((host, t[i:i+12]))

resolved = {}
def run(j):
    host, titles = j
    r = batch(host, titles)
    sys.stderr.write("  %s +%d\n" % (host, len(r)))
    return host, r
with ThreadPoolExecutor(max_workers=4) as ex:
    for host, r in ex.map(run, jobs):
        for k, v in r.items(): resolved["%s|%s" % (host, k)] = v

hm_ents = sorted(k for k, v in resolved.items() if v["hm"])
json.dump({"resolved": resolved,
           "item_sources": {k: entities_for(v["host"], v["title"]) for k, v in raw.items()}},
          open(os.path.join(BASE, "hm_entities.json"), "w"), indent=1)
print("resolved %d entities | Hardmode: %d" % (len(resolved), len(hm_ents)))
print("sample Hardmode entities:", [k.split("|")[1] for k in hm_ents[:14]])
