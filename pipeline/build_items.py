import json, os, re, sys, urllib.parse
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import items as I

BASE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BASE, "wikitext_cache.json")

MOD_HOST = I.MOD_HOST

def clean_title(t):
    t = t.split("?")[0].split("#")[0]
    return urllib.parse.unquote(t).replace("_", " ").strip()

def build_index():
    rec = json.load(open(os.path.join(BASE, "recipes_raw.json")))
    idx = {}
    for src, rows in rec.items():
        for r in rows:
            ents = [(r["result"], r["result_url"], r["result_img"], True)]
            ents += [(i["name"], i["url"], i["img"], False) for g in r["ingredients"] for i in g]
            for nm, url, img, is_res in ents:
                nm = I.norm(nm)
                if not nm: continue
                vanilla_art = bool(img and "terraria.wiki.gg" in img)
                host = "terraria.wiki.gg" if vanilla_art else MOD_HOST[src]
                title = nm
                if url:
                    m = re.search(r"/wiki/(.+)$", url)
                    if m:
                        c = clean_title(m.group(1))
                        if c and not c.startswith("Special:"): title = c
                key = (host, title)
                e = idx.setdefault(key, {"name": nm, "title": title, "host": host,
                                         "img": img, "mods": set(), "vanilla_art": vanilla_art})
                e["mods"].add(src)
                if img and not e["img"]: e["img"] = img
    return idx

# ---------------- fetch phase ----------------
def fetch_all(idx):
    cache = {}
    if os.path.exists(CACHE):
        cache = json.load(open(CACHE))
    need = {}
    for (host, title) in idx:
        if "%s|%s" % (host, title) not in cache:
            need.setdefault(host, []).append(title)
    jobs = []
    for host, titles in need.items():
        titles = sorted(set(titles))
        for i in range(0, len(titles), 40):
            jobs.append((host, titles[i:i+40]))
    if not jobs:
        print("cache complete (%d entries)" % len(cache)); return cache
    print("fetching %d batches" % len(jobs))
    def run(job):
        host, titles = job
        d = I.api(host, {"action":"query","prop":"revisions","rvprop":"content","rvslots":"main",
                         "titles":"|".join(titles),"format":"json","formatversion":"2","redirects":"1"})
        out = {}
        if not d: return out
        q = d.get("query", {})
        nm = {n["from"]: n["to"] for n in q.get("normalized", [])}
        rd = {r["from"]: r["to"] for r in q.get("redirects", [])}
        res = {}
        for t in titles:
            t2 = rd.get(nm.get(t, t), nm.get(t, t))
            res.setdefault(t2, []).append(t)
        for p in q.get("pages", []):
            if p.get("missing"): continue
            c = (p.get("revisions") or [{}])[0].get("slots", {}).get("main", {}).get("content", "")
            if not c: continue
            for orig in res.get(p["title"], []) + [p["title"]]:
                out["%s|%s" % (host, orig)] = c
        sys.stderr.write("  %s +%d\n" % (host, len(out)))
        return out
    with ThreadPoolExecutor(max_workers=4) as ex:
        for r in ex.map(run, jobs):
            cache.update(r)
    json.dump(cache, open(CACHE, "w"))
    return cache

# ---------------- improved extraction ----------------
KEEP_INNER = ("chance", "expert", "master", "duration", "value", "note", "small",
              "sub", "sup", "tooltip", "eicons", "nowrap", "gameText", "GameText")

def preclean(s):
    s = re.sub(r"<ref[^>]*/>", "", s)
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"<[^>]+>", "", s)
    return s

def unwrap_templates(s):
    """Replace {{tpl|a|b}} with the most useful inner text, repeatedly."""
    def rep(m):
        body = m.group(1)
        parts = [p.strip() for p in I.split_params(body)]
        name = parts[0].strip().lower()
        args = [p for p in parts[1:] if "=" not in p.split("=")[0][:0] or True]
        pos = [p for p in parts[1:] if not re.match(r"^\s*\w[\w\s]*=", p)]
        if name in ("item", "item link", "il"):
            return pos[0] if pos else ""
        if name in ("chance", "expert", "master", "duration", "value2", "note", "small",
                    "nowrap", "tooltip", "sub", "sup", "hoverlink"):
            return pos[0] if pos else ""
        if name == "value":
            return I.parse_value("value|" + "|".join(pos)) or ""
        if name.startswith("iteminfo"):
            return ""
        if name in ("key",):
            return pos[0] if pos else ""
        if name in ("pc", "desktop", "console", "mobile", "old-gen", "3ds", "eicons",
                    "eico", "source code ref", "ref", "legacy nav tab", "quotation",
                    "float file box", "drop infobox", "infobox wrapper", "history",
                    "master template equipables", "stub", "clear"):
            return ""
        return pos[0] if len(pos) == 1 else ""
    prev = None
    for _ in range(12):
        prev = s
        s = re.sub(r"\{\{([^{}]*)\}\}", rep, s)
        if s == prev: break
    return I.strip_templates(s)

def strip_leading_blocks(body):
    """Remove leading templates, file links, quotations and blank lines."""
    i = 0
    while i < len(body):
        j = i
        while j < len(body) and body[j] in " \n\t": j += 1
        if j >= len(body): return ""
        if body.startswith("{{", j):
            d = 0; k = j
            while k < len(body):
                if body.startswith("{{", k): d += 1; k += 2; continue
                if body.startswith("}}", k):
                    d -= 1; k += 2
                    if d == 0: break
                    continue
                k += 1
            i = k; continue
        if re.match(r"\[\[\s*(File|Image)\s*:", body[j:], re.I):
            d = 0; k = j
            while k < len(body):
                if body.startswith("[[", k): d += 1; k += 2; continue
                if body.startswith("]]", k):
                    d -= 1; k += 2
                    if d == 0: break
                    continue
                k += 1
            i = k; continue
        if body[j] in "*:;#|" or body.startswith("{|", j):
            k = body.find("\n", j)
            if k < 0: return ""
            i = k; continue
        return body[j:]
    return ""

def lead(text):
    body = re.split(r"\n\s*==[^=]", text)[0]
    body = preclean(body)
    rest = strip_leading_blocks(body)
    paras = [p for p in re.split(r"\n\s*\n", rest)]
    out = []
    for p in paras:
        # a wiki bullet block reads as prose once the markers become separators
        lines = p.split("\n")
        if any(re.match(r"\s*\*+\s", l) for l in lines):
            head = [l for l in lines if not re.match(r"\s*\*+\s", l)]
            bul  = [re.sub(r"^\s*\*+\s*", "", l).strip().rstrip(".")
                    for l in lines if re.match(r"\s*\*+\s", l)]
            bul  = [x for x in bul if x]
            p = " ".join(head).strip()
            if bul: p = (p + " " if p else "") + "; ".join(bul) + "."
        c = unwrap_templates(p)
        c = I.strip_links(c).replace("'''", "").replace("''", "")
        c = re.sub(r"\s+", " ", c).strip()
        c = re.sub(r"\s+([,.;:])", r"\1", c)
        c = re.sub(r"\s+([.,;:])", r"\1", c)
        c = re.sub(r"\bfor\s*\.", ".", c)
        c = re.sub(r"\(\s*,", "(", c)
        c = re.sub(r"(\d)(ticks?|seconds?|minutes?|tiles?|blocks?|feet)\b", r"\1 \2", c)
        c = re.sub(r"\s+([.,;:!?])", r"\1", c)
        c = re.sub(r"[;,]\s*\.", ".", c)
        c = re.sub(r"\s{2,}", " ", c).strip()
        c = re.sub(r"\(\s*\)", "", c)
        c = re.sub(r"\s{2,}", " ", c).strip()
        if len(c) > 25: out.append(c)
        if sum(len(x) for x in out) > 520: break
    return " ".join(out)[:900] or None

def drops(text):
    inner = I.find_template(text, "item drops infobox")
    if not inner: return []
    parts = [p.strip() for p in I.split_params(inner)][1:]
    parts = [p for p in parts if not re.match(r"^\s*(style|class|title)\s*=", p)]
    rows, cur = [], []
    for p in parts:
        cur.append(p)
        if len(cur) == 3:
            src = re.sub(r"\s+", " ", I.strip_links(unwrap_templates(preclean(cur[0])))).strip()
            rows.append({"source": src,
                         "qty": re.sub(r"\s+"," ",unwrap_templates(preclean(cur[1]))).strip(),
                         "rate": re.sub(r"\s+"," ",unwrap_templates(preclean(cur[2]))).strip()})
            cur = []
    return [r for r in rows if r["source"]]

def coins(value):
    if not value: return None
    v = int(value)
    p, v = divmod(v, 1000000); g, v = divmod(v, 10000); s, c = divmod(v, 100)
    bits = [(p,"platinum"),(g,"gold"),(s,"silver"),(c,"copper")]
    out = " ".join("%d %s" % (n,u) for n,u in bits if n)
    return out or None

RARE_NAMES = {-1:"Gray",0:"White",1:"Blue",2:"Green",3:"Orange",4:"Light Red",5:"Pink",
              6:"Light Purple",7:"Lime",8:"Yellow",9:"Cyan",10:"Red",11:"Purple",
              -11:"Quest",-12:"Rainbow",-13:"Fiery Red"}

def extract(host, title, wt, vdb):
    ib = I.parse_infobox(wt)
    tooltip = re.sub(r"\s+", " ", unwrap_templates(preclean(ib.get("tooltip", "")))).strip() or None
    types = [ib[k].strip() for k in ("type","type2","type3","type4") if ib.get(k)]
    tags = [t.strip() for t in re.split(r"[/,]", ib.get("tags","")) if t.strip()]
    buy = sell = None
    if ib.get("buy"):
        t = I.find_template(ib["buy"], "value"); buy = I.parse_value(t) if t else None
    if ib.get("sell"):
        t = I.find_template(ib["sell"], "value"); sell = I.parse_value(t) if t else None
    rare = ib.get("rare")
    hardmode = ib.get("hardmode","").lower() in ("yes","y","true")
    defense = ib.get("defense")
    vd = vdb.get(title) or vdb.get(I.norm(title))
    if vd:
        if rare is None and vd.get("rare") is not None: rare = str(vd["rare"])
        if sell is None and vd.get("value"): sell = coins(int(vd["value"])//5)
        if buy is None and vd.get("value") and any("vendor" in t.lower() for t in tags):
            buy = coins(int(vd["value"]))
        if defense is None and vd.get("defense"): defense = str(vd["defense"])
        if not types and vd.get("accessory"): types = ["Accessory"]
    try: rare_i = int(rare) if rare is not None else None
    except: rare_i = None
    return {"tooltip": tooltip, "types": types, "tags": tags,
            "rare": rare_i, "rare_name": RARE_NAMES.get(rare_i),
            "hardmode": hardmode, "defense": defense,
            "buy": buy, "sell": sell, "lead": lead(wt), "drops": drops(wt),
            "craftable": bool(re.search(r"\{\{\s*recipes\s*\|\s*result|\{\{\s*crafting recipe", wt, re.I))}

if __name__ == "__main__":
    idx = build_index()
    cache = fetch_all(idx)
    vdb = json.load(open(os.path.join(BASE, "vanilla_itemdb.json")))
    out = {}
    for (host, title), e in idx.items():
        k = "%s|%s" % (host, title)
        wt = cache.get(k)
        info = extract(host, title, wt, vdb) if wt else None
        out[k] = {"name": e["name"], "title": title, "host": host, "img": e["img"],
                  "mods": sorted(e["mods"]), "vanilla_art": e["vanilla_art"],
                  "url": "https://%s/wiki/%s" % (host, urllib.parse.quote(title.replace(" ", "_"))),
                  "info": info}
    json.dump(out, open(os.path.join(BASE, "items.json"), "w"), indent=1)
    got = sum(1 for v in out.values() if v["info"])
    lead_ok = sum(1 for v in out.values() if v["info"] and v["info"]["lead"])
    print("items %d | data %d | lead %d | missing %s" %
          (len(out), got, lead_ok, [k for k,v in out.items() if not v["info"]][:12]))
