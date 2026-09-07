"""Builds the boss roster and one merged fight order from the wikis' own Bosses pages.

Two things are read, never invented:
  roster  - each wiki's "Bosses" page, section by section, so a boss carries the tier its
            own wiki files it under (pre-Hardmode / Hardmode / post-Moon Lord / event / mini)
  order   - each wiki's own published progression chart, which already interleaves that mod's
            bosses with the vanilla ones

The charts are merged the way the loadout stages are: vanilla bosses are the anchors every
wiki shares, so a modded boss is placed after the vanilla boss its own wiki puts it after.
Where a wiki publishes no chart, the boss keeps its tier and says the order is unpublished.
"""
import json, os, re, sys
BASE = os.path.dirname(os.path.abspath(__file__))
RAW  = os.path.join(BASE, "bosses_raw")

MODS = ["vanilla", "thorium", "fargo", "spirit", "fables", "stars"]
WIKI = {"vanilla":"Terraria", "thorium":"Thorium", "fargo":"Fargo's Souls",
        "spirit":"Spirit", "fables":"Calamity Fables", "stars":"Stars Above"}
HOST = {"vanilla":"terraria.wiki.gg", "thorium":"thoriummod.wiki.gg",
        "fargo":"fargosmods.wiki.gg", "spirit":"spiritmod.wiki.gg",
        "fables":"calamityfables.wiki.gg", "stars":"starsabovemod.wiki.gg"}

def page(mod, title="Bosses"):
    return (json.load(open(os.path.join(RAW, "pages_%s.json" % mod), encoding="utf-8"))
            .get(title) or "")

def _args(inner):
    """Top-level pipe-separated arguments of a template body."""
    out, buf, d, b = [], [], 0, 0
    for ch in inner:
        if ch == "|" and d == 0 and b == 0: out.append("".join(buf)); buf = []; continue
        buf.append(ch)
        if ch == "{": d += 1
        elif ch == "}": d -= 1
        elif ch == "[": b += 1
        elif ch == "]": b -= 1
    out.append("".join(buf))
    return out

def untemplate(s):
    """Unwrap the templates these wikis use inside prose, innermost first:
    {{item|Slime Crown}} is the item's name, {{modes|a|b|c}} is the classic value."""
    for _ in range(10):
        m = re.search(r"\{\{([^{}]*)\}\}", s)
        if not m: break
        parts = _args(m.group(1))
        head  = parts[0].strip().lower().lstrip(":")
        pos   = [x.strip() for x in parts[1:] if "=" not in x.split("[[")[0]]
        if head in ("item", "npc", "eicons"):
            rep = next((x for x in pos if x and x != "s"), "")
            if rep and any(x == "s" for x in pos): rep += "s"
        elif head in ("modes", "expert", "master", "value", "formatnum", "note", "chance"):
            rep = pos[0] if pos else ""
        else:
            rep = ""
        s = s[:m.start()] + rep + s[m.end():]
    return s

def clean(s):
    s = untemplate(s or "")
    s = re.sub(r"<br\s*/?>", " ", s, flags=re.I)
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]|]+)\]\]", r"\1", s)
    s = re.sub(r"''+", "", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\s+([,.;:])", r"\1", s)
    return re.sub(r"\s+", " ", s).strip()

# ---------------------------------------------------------------- tiers
def tier_of(header):
    h = clean(header).lower()
    if "mini" in h:                                   return "mini"
    if "event" in h:                                  return "event"
    if "seed" in h:                                   return "seed"
    if "post-moon lord" in h or "post moon lord" in h: return "postml"
    if "pre-hardmode" in h or "pre hardmode" in h:    return "pre"
    if "hardmode" in h:                               return "hard"
    return None

def sections(wt):
    """[(header, body)] for every == top-level == section, in page order."""
    parts, cur, buf = [], None, []
    for line in wt.split("\n"):
        m = re.match(r"^==([^=].*?)==\s*$", line)
        if m:
            if cur is not None: parts.append((cur, "\n".join(buf)))
            cur, buf = m.group(1), []
        elif cur is not None:
            buf.append(line)
    if cur is not None: parts.append((cur, "\n".join(buf)))
    return parts

# ---------------------------------------------------------------- roster
BOX  = re.compile(r"\{\{:\{\{BASEPAGENAME\}\}/box\s*\n?\s*\|\s*name\s*=\s*([^\n|]+)")
HEAD = re.compile(r"^===\s*(.+?)\s*===\s*$", re.M)

def roster(mod):
    """Every boss the wiki's own Bosses page lists, with the tier of its section."""
    out = []
    for header, body in sections(page(mod)):
        t = tier_of(header)
        if not t: continue
        names = [clean(n) for n in BOX.findall(body)]
        if not names:
            names = [clean(n) for n in HEAD.findall(body)]
        for n in names:
            if n and not any(n == o["name"] for o in out):
                out.append({"name": n, "tier": t, "mod": mod, "section": clean(header)})
    return out

if __name__ == "__main__":
    total = 0
    for m in MODS:
        r = roster(m)
        total += len(r)
        print("%-8s %2d  %s" % (m, len(r), ", ".join(x["name"] for x in r)))
    print("total listed bosses:", total)

# ---------------------------------------------------------------- progression charts
def tpl_positional(call):
    """First positional argument of a {{item|...}} call -- the name."""
    for part in call.split("|")[1:]:
        part = part.strip()
        if "=" in part.split("]]")[0]: continue
        if part: return clean(part)
    return None

def calls(text, name):
    """Every {{name|...}} call in text, brace-balanced, in order."""
    out, i, tag = [], 0, "{{" + name
    while True:
        j = text.find(tag, i)
        if j < 0: return out
        depth, k = 0, j
        while k < len(text):
            if text.startswith("{{", k): depth += 1; k += 2; continue
            if text.startswith("}}", k):
                depth -= 1; k += 2
                if depth == 0: break
                continue
            k += 1
        out.append(text[j:k]); i = k

def chart_rows(wt):
    """Ordered names out of a two-column progression table (Spirit, Stars Above)."""
    seq = []
    for line in wt.split("\n"):
        h = re.match(r"^!\s*colspan=\"?2\"?\s*\|\s*(.+?)\s*$", line)
        if h:
            t = tier_of(h.group(1))
            if t: seq.append(("__tier__", t))
            continue
        if not line.startswith("|"): continue
        names = [tpl_positional(c) for c in calls(line, "item")]
        if not names:
            names = [clean(x) for x in re.findall(r"\[\[(?!File:)([^\]|]+)", line)]
        for n in names:
            if n: seq.append(("boss", n))
    return seq

def chart_fables(wt):
    seq = []
    for c in calls(wt, "BossProgIcon"):
        m = re.search(r"\|\s*(?:boss|bossvanilla)\s*=\s*([^|}\n]+)", c)
        if m: seq.append(("boss", clean(m.group(1))))
    return seq

def chart_thorium(wt):
    """Thorium draws its chart as an ASCII diagram of keys, defined underneath."""
    defs = {}
    for m in re.finditer(r"^\|\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*(\{\{item\b.*)$", wt, re.M):
        n = tpl_positional(m.group(2))
        if n: defs[m.group(1).rstrip("_")] = n
    seq, seen = [], set()
    for m in re.finditer(r"^\|.*\|#\s*$", wt, re.M):
        for tok in re.findall(r"\|\s{2,}([A-Za-z][A-Za-z0-9_]*)\s{2,}\|", m.group(0)):
            k = tok.rstrip("_")
            if k in defs and defs[k] not in seen:
                seen.add(defs[k]); seq.append(("boss", defs[k]))
    return seq

def progression(mod):
    if mod == "vanilla":
        return [("boss", b["name"]) for b in roster("vanilla")]
    if mod == "thorium":
        return chart_thorium(page("thorium", "Bosses/Progression"))
    body = ""
    for header, b in sections(page(mod)):
        if "progression" in clean(header).lower(): body = b; break
    if not body: return []
    return chart_fables(body) if mod == "fables" else chart_rows(body)

# ---------------------------------------------------------------- per-boss detail
def detail_pages(mod):
    p = os.path.join(RAW, "detail_%s.json" % mod)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}

def infobox(wt):
    """Fields of the {{npc infobox}} -- every one of the six wikis uses the same template."""
    if not wt: return {}
    i = wt.lower().find("{{npc infobox")
    if i < 0: return {}
    depth, k, j = 0, i, i
    while k < len(wt):
        if wt.startswith("{{", k): depth += 1; k += 2; continue
        if wt.startswith("}}", k):
            depth -= 1; k += 2
            if depth == 0: break
            continue
        k += 1
    body, out, buf, d, b = wt[i+2:k-2], {}, [], 0, 0
    for ch in body:                      # split on top-level pipes only
        if body[max(0,len(buf)-1):]: pass
        if ch == "|" and d == 0 and b == 0: buf.append("\x00"); continue
        buf.append(ch)
        if ch == "{": d += 1
        elif ch == "}": d -= 1
        elif ch == "[": b += 1
        elif ch == "]": b -= 1
    for part in "".join(buf).split("\x00")[1:]:
        if "=" not in part: continue
        key, _, val = part.partition("=")
        key = key.strip().lower()
        if re.match(r"^[a-z][a-z0-9 _]*$", key): out.setdefault(key, val.strip())
    return out

MODES = re.compile(r"\{\{modes\|(.*?)\}\}", re.S)

def life_of(ib):
    v = ib.get("life") or ""
    m = MODES.search(v)
    if m:
        vals = [x.strip() for x in m.group(1).split("|") if "=" not in x or x.strip().startswith("expert=") or x.strip().startswith("master=")]
        vals = [re.sub(r"^(expert|master)=", "", x) for x in vals]
        vals = [x for x in vals if re.match(r"^[\d,]+$", x)]
        if vals: return vals[0]
    m = re.match(r"\s*([\d,]+)", clean(v))
    return m.group(1) if m else None

FILE_IN = re.compile(r"\[\[File:([^\]|]+)", re.I)

def image_of(ib, name):
    for key in ("image", "image2", "imagealt", "image1"):
        v = ib.get(key)
        if not v: continue
        m = FILE_IN.search(v)
        if m: return m.group(1).strip()
        v = clean(v)
        if re.search(r"\.(png|gif|jpg)$", v, re.I): return v
    return None

SUMMON_BOX = re.compile(r"\|\s*summoned\s*=\s*(.+?)(?=\n\s*\||\n\s*\}\}|\n\n)", re.S)

def summons(mod):
    """The 'summoned =' line each wiki writes into its own Bosses-page box."""
    out = {}
    wt = page(mod)
    for blk in calls(wt, ":{{BASEPAGENAME}}/box"):
        n = re.search(r"\|\s*name\s*=\s*([^\n|]+)", blk)
        s = SUMMON_BOX.search(blk)
        if n and s: out[clean(n.group(1))] = clean(s.group(1))
    return out

LEAD_SUMMON = re.compile(r"summoned[^.\[]{0,45}\[\[([^\]|]+)", re.I)
NATURAL     = re.compile(r"(appears?|spawns?)[^.]{0,60}naturally", re.I)

def section_body(mod, name):
    """The block the wiki's own Bosses page gives this boss, for the wikis that use
    === headings === instead of boxes."""
    wt, short = page(mod), name.split(" (")[0]
    m = re.search(r"^===\s*\[?\[?%s[^\n=]*===\s*$(.*?)(?=^==)" % re.escape(short),
                  wt, re.M | re.S)
    return m.group(1) if m else ""

def summon_of(mod, name, boxes, wt):
    if name in boxes: return boxes[name]
    for text in (section_body(mod, name), (wt or "")[:4000]):
        if not text: continue
        m = LEAD_SUMMON.search(text)
        if m:
            item = clean(m.group(1))
            art  = "" if re.match(r"^(the|a|an)\b", item, re.I) else "a "
            return "Summoned with " + art + item
        if NATURAL.search(text): return "Spawns naturally"
    return None

def image_from_section(mod, name):
    for f in FILE_IN.findall(section_body(mod, name)):
        f = f.strip()
        if re.search(r"(trophy|relic|mask|map[ _]icon)", f, re.I): continue
        return f
    return None

# ---------------------------------------------------------------- prose placement
# Fargo's Souls publishes no progression chart, but its boss pages say in words where each
# fight belongs -- "intended to be fought before the mechanical bosses". Read those sentences
# rather than leaving a third of the pack sitting in an unordered heap. Every placement made
# this way carries the sentence it came from, and is clamped to the tier the wiki files the
# boss under, so a post-Moon Lord superboss can never land in pre-Hardmode.
GROUP_ALIAS = {
    "mechanical boss": ("Wall of Flesh", "Skeletron Prime"),   # (before -> this, after -> this)
    "mech boss":       ("Wall of Flesh", "Skeletron Prime"),
}
START = "__start__"

def lead_prose(wt):
    """The article text, with the infobox and any leading templates dropped."""
    if not wt: return ""
    i = wt.lower().find("{{npc infobox")
    if i >= 0:
        depth, k = 0, i
        while k < len(wt):
            if wt.startswith("{{", k): depth += 1; k += 2; continue
            if wt.startswith("}}", k):
                depth -= 1; k += 2
                if depth == 0: break
                continue
            k += 1
        wt = wt[k:]
    wt = re.split(r"\n==", wt)[0]          # stop at the first section heading
    return clean(wt)[:2500]

def tier_bounds(tier, vorder):
    ix = {n: i for i, n in enumerate(vorder)}
    if tier == "pre":    return (-1, ix.get("Skeletron", 6))
    if tier == "hard":   return (ix.get("Wall of Flesh", 7), ix.get("Lunatic Cultist", 16))
    if tier == "postml": return (ix.get("Moon Lord", 17), ix.get("Moon Lord", 17))
    return None

def prose_anchor(wt, vorder):
    """(anchor name or START, the sentence it came from) or (None, None)."""
    text = lead_prose(wt)
    if not text: return None, None
    vset = {v.lower(): v for v in vorder}
    for sent in re.split(r"(?<=\.)\s+", text):
        low = sent.lower()
        if not re.search(r"\b(fought|defeat\w*|confront\w*|recommend\w*|intend\w*|challenge)\b", low):
            continue
        for word, is_after in (("after", True), ("before", False)):
            m = re.search(r"\b%s\b(.{0,70}?)(?=[,.;]|$)" % word, low)
            if not m: continue
            tail = m.group(1)
            hit = None
            for alias, (b_anchor, a_anchor) in GROUP_ALIAS.items():
                if alias in tail: hit = a_anchor if is_after else b_anchor; break
            if not hit:
                for low_name, real in vset.items():
                    if low_name in tail:
                        if is_after: hit = real
                        else:
                            j = vorder.index(real)
                            hit = vorder[j-1] if j > 0 else START
                        break
            if hit: return hit, sent.strip()
    return None, None

def place_by_prose(mod, bosses, det, vorder):
    """{name: (anchor, evidence, how)} -- 'stated' from the page's own words, 'inferred' from
    the position its Bosses page gives it between two stated ones. Mini-bosses are left out:
    no wiki orders them, and pretending otherwise would be a guess."""
    ix = {n: i for i, n in enumerate(vorder)}
    def idx(a): return -1 if a == START else ix.get(a, -1)
    def clamp(a, tier):
        b = tier_bounds(tier, vorder)
        if not b: return a, False
        lo, hi = b
        j = idx(a)
        if j < lo: return (START if lo < 0 else vorder[lo]), True
        if j > hi: return vorder[hi], True
        return a, False

    order = [b["name"] for b in roster(mod)]
    want  = {b["name"]: b for b in bosses if b["tier"] != "mini"}
    out   = {}
    for name, b in want.items():
        a, why = prose_anchor(det.get(name), vorder)
        if not a: continue
        a2, moved = clamp(a, b["tier"])
        if moved:
            why = (why or "") + " (its wiki files it under %s, so it is held to that tier.)" % b["section"]
        out[name] = (a2, why, "stated")

    for i, name in enumerate(order):
        if name in out or name not in want: continue
        tier = want[name]["tier"]
        prev = next((out[order[j]][0] for j in range(i-1, -1, -1)
                     if order[j] in out and want.get(order[j], {}).get("tier") == tier), None)
        nxt  = next((order[j] for j in range(i+1, len(order))
                     if order[j] in out and want.get(order[j], {}).get("tier") == tier), None)
        if prev is None and nxt is None:
            b = tier_bounds(tier, vorder)
            if not b: continue
            anchor = START if b[0] < 0 else vorder[b[0]]
            why = "%s files it under %s; its wiki gives no finer placement." % (WIKI[mod], want[name]["section"])
        elif prev is None:
            anchor = START if tier == "pre" else clamp(START, tier)[0]
            why = "%s lists it before %s on its Bosses page, and gives no other placement." % (
                  WIKI[mod], nxt)
        else:
            anchor = prev
            why = "%s lists it just after %s on its Bosses page, which it places %s." % (
                  WIKI[mod],
                  next(order[j] for j in range(i-1, -1, -1) if order[j] in out),
                  "at the start" if prev == START else "after " + prev)
        out[name] = (clamp(anchor, tier)[0], why, "inferred")
    return out

# ---------------------------------------------------------------- merged order
ALIAS = {"Mechanical bosses": "Skeletron Prime"}   # Stars Above anchors on the trio as one

BANDS = [("pre",    "Pre-Hardmode",   "Everything before the Wall of Flesh."),
         ("hard",   "Hardmode",       "Wall of Flesh is down and the world has changed."),
         ("postml", "Post-Moon Lord", "Past the end of the vanilla game."),
         ("event",  "Event bosses",   "Fought during an invasion or event, not in the main line."),
         ("mini",   "Mini-bosses and optional fights",
                    "Listed by their wikis outside the progression charts."),
         ("seed",   "Secret world seeds", "Only in a special seed.")]

def build():
    van    = roster("vanilla")
    vorder = [b["name"] for b in van]
    vindex = {n: i for i, n in enumerate(vorder)}
    vtier  = {b["name"]: b["tier"] for b in van}

    placed, unplaced, why = {}, [], {}
    for mod in MODS:
        if mod == "vanilla": continue
        ros  = {b["name"]: b for b in roster(mod)}
        seen, cur, pos = set(), -1, 0
        for kind, nm in progression(mod):
            if kind != "boss": continue
            nm = ALIAS.get(nm, nm)
            if nm in vindex: cur = vindex[nm]; continue
            if nm in ros and nm not in seen:
                seen.add(nm); pos += 1
                placed[(mod, nm)] = (cur, pos)
        # anything the chart missed: read the boss page's own wording
        rest = [b for nm, b in ros.items() if nm not in seen]
        if rest:
            byprose = place_by_prose(mod, rest, detail_pages(mod), vorder)
            for nm, (anchor, evidence, how) in byprose.items():
                pos += 1
                placed[(mod, nm)] = (-1 if anchor == START else vindex.get(anchor, -1), pos)
                why[(mod, nm)] = (evidence, how)
                seen.add(nm)
        for nm, b in ros.items():
            if nm not in seen: unplaced.append(b)

    # a boss sits in the band of the vanilla boss it follows; anything after Moon Lord
    # starts the post-Moon Lord band
    def band_for(anchor_idx):
        if anchor_idx < 0: return "pre"
        n = vorder[anchor_idx]
        if n == "Moon Lord":     return "postml"   # anything after it is post-Moon Lord
        if n == "Wall of Flesh": return "hard"     # the Wall is the gate, not the last of pre
        return vtier.get(n, "pre")

    rows = []
    def add(b, band, anchor, order, unordered=False):
        ev, how = why.get((b["mod"], b["name"]), (None, None))
        rows.append({"name": b["name"], "mod": b["mod"], "tier": b["tier"],
                     "section": b["section"], "band": band, "anchor": anchor,
                     "order": order, "unordered": unordered,
                     "evidence": ev, "how": how or ("charted" if not unordered else None)})

    # vanilla bosses in their own order, each followed by whatever anchors to it
    byanchor = {}
    for (mod, nm), (a, p) in placed.items():
        byanchor.setdefault(a, []).append((mod, nm, p))
    for mod, nm, p in sorted(byanchor.get(-1, []), key=lambda x: (x[2], x[0])):
        add(next(b for b in roster(mod) if b["name"] == nm), "pre", None, len(rows))
    for i, b in enumerate(van):
        add(b, b["tier"], None, len(rows))
        for mod, nm, p in sorted(byanchor.get(i, []), key=lambda x: (x[2], x[0])):
            src = next(x for x in roster(mod) if x["name"] == nm)
            add(src, band_for(i), b["name"], len(rows))
    for b in unplaced:
        band = "mini" if b["tier"] == "mini" else b["tier"]
        add(b, band, None, len(rows), unordered=True)
    return rows

if __name__ == "__main__" and "--order" in sys.argv:
    for r in build():
        print("%-8s %-6s %-34s %s" % (r["band"], r["mod"], r["name"],
              ("after " + r["anchor"]) if r["anchor"] else ("unordered" if r["unordered"] else "")))

# ---------------------------------------------------------------- output
# which Loadouts checkpoint you want to be geared for when you fight it
STAGE_OF = {
 "King Slime":"start", "Eye of Cthulhu":"eye", "Eater of Worlds":"evil", "Brain of Cthulhu":"evil",
 "Queen Bee":"skeletron", "Deerclops":"skeletron", "Skeletron":"skeletron",
 "Wall of Flesh":"wof", "Queen Slime":"mech", "The Twins":"mech", "The Destroyer":"mech",
 "Skeletron Prime":"mech", "Plantera":"plantera", "Golem":"golem",
 "Duke Fishron":"cultist", "Empress of Light":"cultist", "Lunatic Cultist":"cultist",
 "Moon Lord":"moonlord",
}
BAND_STAGE = {"pre":"start", "hard":"mech", "postml":"endgame", "event":"endgame",
              "mini":None, "seed":"endgame"}

def dataset():
    rows, det, box, out = build(), {}, {}, []
    for m in MODS:
        det[m], box[m] = detail_pages(m), summons(m)
    # A vanilla boss wants the "Pre-<itself>" checkpoint. A modded boss anchored after a
    # vanilla boss is fought once that one is dead, so it wants the *next* checkpoint along.
    vorder = [b["name"] for b in roster("vanilla")]
    def stage_after(anchor):
        seen = False
        for n in vorder:
            if n == anchor: seen = True; continue
            if seen and n in STAGE_OF: return STAGE_OF[n]
        return None
    for r in rows:
        mod, name = r["mod"], r["name"]
        wt  = det[mod].get(name)
        ib  = infobox(wt)
        img = image_of(ib, name) or image_from_section(mod, name)
        if r["anchor"]:
            stage = stage_after(r["anchor"]) or STAGE_OF.get(r["anchor"])
        else:
            stage = STAGE_OF.get(name)
        stage = stage or BAND_STAGE.get(r["band"])
        if r["band"] == "postml": stage = "endgame"
        out.append({
            "name": name, "mod": mod, "wiki": WIKI[mod], "host": HOST[mod],
            "url": "https://%s/wiki/%s" % (HOST[mod], name.replace(" ", "_")),
            "band": r["band"], "anchor": r["anchor"], "order": r["order"],
            "unordered": r["unordered"], "tier": r["tier"], "section": r["section"],
            "evidence": r["evidence"], "how": r["how"],
            "summon": summon_of(mod, name, box[mod], wt),
            "life": life_of(ib), "env": clean(ib.get("environment") or "") or None,
            "img": img, "stage": stage,
        })
    return {"bands": BANDS, "wiki": WIKI, "host": HOST, "bosses": out}

if __name__ == "__main__" and "--write" in sys.argv:
    d = dataset()
    for p in (os.path.join(BASE, "bosses.json"),
              os.path.join(os.path.dirname(BASE), "data", "bosses.json")):
        json.dump(d, open(p, "w", encoding="utf-8"), indent=1)
    n = len(d["bosses"])
    print("wrote bosses.json — %d bosses" % n)
    for k, lbl, _ in BANDS:
        print("  %-8s %2d" % (k, sum(1 for b in d["bosses"] if b["band"] == k)))
    for f in ("summon", "life", "img"):
        print("  %-8s %2d/%d" % (f, sum(1 for b in d["bosses"] if b[f]), n))

