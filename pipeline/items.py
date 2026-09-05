import json, os, re, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.abspath(__file__))

def jina(url, tries=4):
    enc = urllib.parse.quote(url, safe='')
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request("https://r.jina.ai/" + enc,
                headers={"x-return-format": "text", "User-Agent": "Mozilla/5.0"})
            return urllib.request.urlopen(req, timeout=180).read().decode("utf-8", "replace")
        except Exception as e:
            last = e; time.sleep(3 + 3*i)
    sys.stderr.write("FAIL %s : %s\n" % (url[:100], last)); return None

def api(host, params):
    url = "https://%s/api.php?%s" % (host, urllib.parse.urlencode(params))
    t = jina(url)
    if t is None: return None
    try: return json.loads(t)
    except Exception: return None

# ---------- build item index from recipes ----------
def norm(s): return re.sub(r"\s+", " ", s or "").strip()

MOD_HOST = {"vanilla":"terraria.wiki.gg","thorium":"thoriummod.wiki.gg","fargo":"fargosmods.wiki.gg",
            "spirit":"spiritmod.wiki.gg","spirit_reforged":"spiritmod.wiki.gg","fables":"calamityfables.wiki.gg"}

def build_index():
    rec = json.load(open(os.path.join(BASE, "recipes_raw.json")))
    idx = {}
    for src, rows in rec.items():
        for r in rows:
            entries = [(r["result"], r["result_url"], r["result_img"])]
            entries += [(i["name"], i["url"], i["img"]) for g in r["ingredients"] for i in g]
            for nm, url, img in entries:
                nm = norm(nm)
                if not nm: continue
                is_vanilla_art = bool(img and "terraria.wiki.gg" in img)
                host = "terraria.wiki.gg" if is_vanilla_art else MOD_HOST[src]
                title = None
                if url:
                    m = re.search(r"/wiki/(.+)$", url)
                    if m: title = urllib.parse.unquote(m.group(1)).replace("_", " ")
                title = title or nm
                key = (host, title)
                e = idx.setdefault(key, {"name": nm, "title": title, "host": host,
                                         "img": img, "mods": set(), "vanilla_art": is_vanilla_art})
                e["mods"].add(src)
                if img and not e["img"]: e["img"] = img
    return idx

# ---------- wikitext extraction ----------
def strip_links(s):
    s = re.sub(r"\[\[([^\]\|]+)\|([^\]]+)\]\]", r"\2", s)
    s = re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)
    return s

def strip_templates(s):
    out, depth = [], 0
    i = 0
    while i < len(s):
        if s.startswith("{{", i): depth += 1; i += 2; continue
        if s.startswith("}}", i) and depth: depth -= 1; i += 2; continue
        if depth == 0: out.append(s[i])
        i += 1
    return "".join(out)

def find_template(text, name):
    """Return inner text of the first {{name ...}} template (brace-balanced)."""
    m = re.search(r"\{\{\s*" + re.escape(name) + r"\s*[\|\}]", text, re.I)
    if not m: return None
    i = m.start(); depth = 0; j = i
    while j < len(text):
        if text.startswith("{{", j): depth += 1; j += 2; continue
        if text.startswith("}}", j):
            depth -= 1; j += 2
            if depth == 0: return text[i+2:j-2]
            continue
        j += 1
    return None

def split_params(s):
    """Split template body on top-level pipes."""
    parts, depth_b, depth_l, cur = [], 0, 0, []
    i = 0
    while i < len(s):
        if s.startswith("{{", i): depth_b += 1; cur.append(s[i:i+2]); i += 2; continue
        if s.startswith("}}", i): depth_b -= 1; cur.append(s[i:i+2]); i += 2; continue
        if s.startswith("[[", i): depth_l += 1; cur.append(s[i:i+2]); i += 2; continue
        if s.startswith("]]", i): depth_l -= 1; cur.append(s[i:i+2]); i += 2; continue
        if s[i] == "|" and depth_b == 0 and depth_l == 0:
            parts.append("".join(cur)); cur = []; i += 1; continue
        cur.append(s[i]); i += 1
    parts.append("".join(cur))
    return parts

def parse_value(tpl):
    """{{value|gold|silver|copper}} -> readable coins (platinum|gold|silver|copper on these wikis)."""
    p = [x.strip() for x in split_params(tpl)][1:]
    names = ["platinum", "gold", "silver", "copper"]
    # {{value|platinum|gold|silver|copper}} is LEFT-aligned: fewer args = higher denominations
    p = (p + ["0"] * 4)[:4]
    bits = []
    for v, n in zip(p, names):
        try: iv = int(re.sub(r"[^\d]", "", v) or 0)
        except: iv = 0
        if iv: bits.append("%d %s" % (iv, n))
    return " ".join(bits) or None

def clean_prose(s):
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    # keep {{item|X}} / {{item|mode=text|X}} names before stripping templates
    def item_sub(m):
        parts = [x.strip() for x in split_params(m.group(1))]
        vals = [x for x in parts[1:] if "=" not in x]
        return vals[0] if vals else ""
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r"\{\{\s*(item\s*\|[^{}]*)\}\}", item_sub, s, flags=re.I)
    s = re.sub(r"\{\{\s*(?:eicons?|eico|desktop|console|mobile|old-gen|3ds)[^{}]*\}\}", "", s, flags=re.I)
    s = strip_templates(s)
    s = strip_links(s)
    s = s.replace("'''", "").replace("''", "")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def lead_paragraph(text):
    body = re.split(r"\n==[^=]", text)[0]
    # drop leading infobox templates
    lines, buf, depth = [], [], 0
    for ch_i, ch in enumerate(body):
        pass
    # remove balanced templates at start
    i = 0
    while i < len(body):
        if body.startswith("{{", i):
            d = 0; j = i
            while j < len(body):
                if body.startswith("{{", j): d += 1; j += 2; continue
                if body.startswith("}}", j):
                    d -= 1; j += 2
                    if d == 0: break
                    continue
                j += 1
            i = j
            while i < len(body) and body[i] in " \n\t": i += 1
            continue
        break
    rest = body[i:]
    paras = [p for p in re.split(r"\n\s*\n", rest) if clean_prose(p)]
    return clean_prose(paras[0]) if paras else ""

def parse_drops(text):
    inner = find_template(text, "item drops infobox")
    if not inner: return []
    parts = [p.strip() for p in split_params(inner)][1:]
    parts = [p for p in parts if p and "=" not in p.split("|")[0][:20] or "|" in p]
    rows, cur = [], []
    for p in parts:
        cur.append(p)
        if len(cur) == 3:
            rows.append({"source": clean_prose(cur[0]), "qty": clean_prose(cur[1]),
                         "rate": clean_prose(cur[2])})
            cur = []
    if cur and cur[0].strip():
        rows.append({"source": clean_prose(cur[0]), "qty": "", "rate": ""})
    return [r for r in rows if r["source"]]

def parse_infobox(text):
    inner = find_template(text, "item infobox")
    if not inner: return {}
    out = {}
    for p in split_params(inner)[1:]:
        if "=" not in p: continue
        k, v = p.split("=", 1)
        out[k.strip().lower()] = v.strip()
    return out

def extract(title, host, wikitext):
    ib = parse_infobox(wikitext)
    tooltip = clean_prose(re.sub(r"<br\s*/?>", " · ", ib.get("tooltip", "")))
    types = [ib.get(k, "").strip() for k in ("type", "type2", "type3", "type4") if ib.get(k)]
    buy = sell = None
    if ib.get("buy"):
        t = find_template(ib["buy"], "value")
        buy = parse_value(t) if t else clean_prose(ib["buy"])
    if ib.get("sell"):
        t = find_template(ib["sell"], "value")
        sell = parse_value(t) if t else clean_prose(ib["sell"])
    lead = lead_paragraph(wikitext)
    drops = parse_drops(wikitext)
    craftable = bool(re.search(r"\{\{\s*recipes\s*\|\s*result", wikitext, re.I)) or \
                bool(re.search(r"\{\{\s*crafting recipe", wikitext, re.I))
    cats = re.findall(r"\[\[Category:([^\]\|]+)", wikitext)
    return {"tooltip": tooltip or None, "types": types,
            "rare": ib.get("rare"), "hardmode": (ib.get("hardmode","").lower() in ("yes","y","true")),
            "buy": buy, "sell": sell, "lead": lead or None,
            "drops": drops, "craftable": craftable,
            "categories": [c.strip() for c in cats][:8]}

def fetch_batch(host, titles):
    d = api(host, {"action":"query","prop":"revisions","rvprop":"content","rvslots":"main",
                   "titles":"|".join(titles),"format":"json","formatversion":"2",
                   "redirects":"1"})
    out = {}
    if not d: return out
    q = d.get("query", {})
    norm_map = {n["from"]: n["to"] for n in q.get("normalized", [])}
    redir_map = {r["from"]: r["to"] for r in q.get("redirects", [])}
    resolved = {}
    for t in titles:
        t2 = norm_map.get(t, t); t2 = redir_map.get(t2, t2)
        resolved.setdefault(t2, []).append(t)
    for p in q.get("pages", []):
        if p.get("missing"): continue
        c = (p.get("revisions") or [{}])[0].get("slots", {}).get("main", {}).get("content", "")
        if not c: continue
        try: info = extract(p["title"], host, c)
        except Exception as e:
            sys.stderr.write("extract err %s: %s\n" % (p.get("title"), e)); continue
        for orig in resolved.get(p["title"], [p["title"]]):
            out[orig] = info
        out[p["title"]] = info
    return out

if __name__ == "__main__":
    idx = build_index()
    by_host = {}
    for (host, title), e in idx.items():
        by_host.setdefault(host, []).append(title)
    jobs = []
    for host, titles in by_host.items():
        titles = sorted(set(titles))
        for i in range(0, len(titles), 40):
            jobs.append((host, titles[i:i+40]))
    print("hosts:", {h: len(set(t)) for h, t in by_host.items()}, "| batches:", len(jobs))
    results = {}
    def run(job):
        host, titles = job
        r = fetch_batch(host, titles)
        sys.stderr.write("  %s +%d/%d\n" % (host, len(r), len(titles)))
        return host, r
    with ThreadPoolExecutor(max_workers=4) as ex:
        for host, r in ex.map(run, jobs):
            results.setdefault(host, {}).update(r)
    data = {}
    for (host, title), e in idx.items():
        info = results.get(host, {}).get(title)
        data["%s|%s" % (host, title)] = {
            "name": e["name"], "title": title, "host": host, "img": e["img"],
            "mods": sorted(e["mods"]), "vanilla_art": e["vanilla_art"],
            "url": "https://%s/wiki/%s" % (host, urllib.parse.quote(title.replace(" ", "_"))),
            "info": info}
    json.dump(data, open(os.path.join(BASE, "items.json"), "w"), indent=1)
    got = sum(1 for v in data.values() if v["info"])
    print("items: %d | with data: %d | missing: %d" % (len(data), got, len(data)-got))
