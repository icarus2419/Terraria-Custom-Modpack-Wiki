"""Combat stats for every weapon in the pack, not just the ones a guide happened to name.

`loadout_stats.py` only ever looks up items that appear in `loadouts.json`, and
`loadouts.json` is built from the class-setup guides. Two things fall through that:

  * Mods that publish no class guide. Fargo's Souls is the whole difficulty layer of this
    pack and gets two entries in the loadout panels; its 48 weapons carry no damage
    figure at all, so nothing can rank them.
  * Weapons that are pure boss drops. The item index is built from recipes, so a weapon
    with no recipe never enters the database. The Kamikaze Squirrel Staff, Expixive Staff
    and Decrepit Airstrike Remote -- 60, 47 and 375 summon damage -- were all invisible.

This walks each mod wiki's weapon categories instead, so drop-only items are included,
and fills in any name the stats file is missing. Existing entries are never overwritten:
`corrections.py` owns the hand-verified ones.

    python3 pipeline/weapon_stats_fetch.py          # fetch + merge
    python3 pipeline/weapon_stats_fetch.py --dry    # report what is missing, fetch nothing
"""
import json, os, re, sys, time, urllib.parse, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, BASE)
import items as I
import build_items as B

UA = "ModpackWikiBuilder/1.0 (personal reference tool)"

HOSTS = ["terraria.wiki.gg", "thoriummod.wiki.gg", "fargosmods.wiki.gg",
         "spiritmod.wiki.gg", "starsabovemod.wiki.gg", "calamityfables.wiki.gg"]

# Categories that hold something with combat stats. Not every wiki uses every name;
# missing ones simply return nothing.
CATEGORIES = ["Weapon items", "Minion summon items", "Sentry summon items",
              "Accessory items", "Armor items"]

DMG_TYPE = {"melee": "Melee", "ranged": "Ranged", "magic": "Magic", "summon": "Summon",
            "radiant": "Radiant", "symphonic": "Symphonic", "throwing": "Throwing",
            "thrown": "Throwing", "rogue": "Rogue", "true melee": "Melee"}


def api(host, params):
    params = dict(params, format="json", formatversion="2")
    url = "https://%s/api.php?%s" % (host, urllib.parse.urlencode(params))
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            return json.loads(urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace"))
        except Exception as exc:
            if attempt == 3:
                sys.stderr.write("FAIL %s: %s\n" % (host, exc))
                return None
            time.sleep(2 + 3 * attempt)


def category_members(host, category):
    """Every page in a category, following continuation."""
    out, cont = [], None
    while True:
        p = {"action": "query", "list": "categorymembers", "cmtitle": "Category:" + category,
             "cmlimit": "500", "cmnamespace": "0"}
        if cont:
            p["cmcontinue"] = cont
        d = api(host, p)
        if not d or "query" not in d:
            return out
        out += [m["title"] for m in d["query"]["categorymembers"]]
        cont = (d.get("continue") or {}).get("cmcontinue")
        if not cont:
            return out


def wikitext(host, titles):
    """Wikitext for up to 50 titles, keyed by the title asked for (redirects resolved)."""
    d = api(host, {"action": "query", "prop": "revisions", "rvprop": "content",
                   "rvslots": "main", "titles": "|".join(titles), "redirects": "1"})
    if not d or "query" not in d:
        return {}
    q = d["query"]
    norm = {x["from"]: x["to"] for x in q.get("normalized", [])}
    redir = {x["from"]: x["to"] for x in q.get("redirects", [])}
    back = {}
    for t in titles:
        landed = redir.get(norm.get(t, t), norm.get(t, t))
        back.setdefault(landed, []).append(t)
    out = {}
    for p in q.get("pages", []):
        if p.get("missing"):
            continue
        c = (p.get("revisions") or [{}])[0].get("slots", {}).get("main", {}).get("content", "")
        if not c:
            continue
        for asked in back.get(p["title"], []) + [p["title"]]:
            out[asked] = c
    return out


def speed_word(use):
    try:
        u = float(use)
    except (TypeError, ValueError):
        return None
    for lim, w in ((8, "Insanely fast"), (20, "Very fast"), (25, "Fast"), (30, "Average"),
                   (35, "Slow"), (45, "Very slow"), (55, "Extremely slow")):
        if u < lim:
            return w
    return "Snail"


def num(v):
    m = re.search(r"[\d.]+", re.sub(r"<[^>]+>", "", v or ""))
    return m.group(0) if m else None


def stats_from(wt):
    """Same field mapping loadout_stats.py uses, so both sources agree."""
    ib = I.parse_infobox(wt)
    if not ib:
        return None
    s = {}
    if ib.get("damage"):
        d = num(ib["damage"])
        if d:
            s["damage"] = d
    dt = re.sub(r"[\[\]]", "", (ib.get("damagetype") or ib.get("damage_type") or "")).strip().lower()
    if dt in DMG_TYPE:
        s["dtype"] = DMG_TYPE[dt]
    if ib.get("defense"):
        d = num(ib["defense"])
        if d:
            s["defense"] = d
    for src, dst in (("knockback", "knockback"), ("critical", "crit"),
                     ("mana", "mana"), ("velocity", "velocity")):
        if ib.get(src):
            v = num(ib[src])
            if v:
                s[dst] = v
    u = num(ib.get("use") or ib.get("usetime"))
    if u:
        s["use"] = u
        w = speed_word(u)
        if w:
            s["speed"] = w
    if ib.get("setbonus"):
        s["setbonus"] = re.sub(r"\s+", " ", B.unwrap_templates(B.preclean(ib["setbonus"]))).strip()[:400]
    ty = [ib.get(x) for x in ("type", "type2", "type3") if ib.get(x)]
    if ty:
        s["kind"] = " · ".join(t.strip() for t in ty[:2])
    if ib.get("tooltip"):
        tt = re.sub(r"\s+", " ", B.unwrap_templates(B.preclean(ib["tooltip"]))).strip()
        if tt:
            s["tip"] = tt[:320]
    if "tip" not in s:
        parts = re.split(r"(?<=\.)\s", B.lead(wt) or "")
        if parts and len(parts[0]) > 24:
            sent = parts[0]
            if len(sent) < 70 and len(parts) > 1:
                sent = sent + " " + parts[1]
            s["tip"] = re.sub(r"\s+", " ", sent).strip()[:320]
    return s or None


def load(name):
    for p in (os.path.join(BASE, name), os.path.join(DATA, name)):
        if os.path.exists(p):
            return json.load(open(p, encoding="utf-8"))
    raise SystemExit("missing " + name)


def main():
    dry = "--dry" in sys.argv
    stats = load("loadout_stats.json")
    full = load("full_site_data.json")
    known = {v["n"]: v.get("h") for v in full["items"].values()}

    print("collecting weapon categories from %d wikis..." % len(HOSTS), flush=True)
    targets = {}          # host -> set of titles
    for host in HOSTS:
        names = set()
        for cat in CATEGORIES:
            got = category_members(host, cat)
            if got:
                names |= set(got)
        # anything already in the item database from this host counts too
        names |= {n for n, h in known.items() if h == host}
        missing = {n for n in names if n not in stats}
        targets[host] = missing
        print("  %-24s %5d pages, %4d without stats" % (host, len(names), len(missing)), flush=True)

    total = sum(len(v) for v in targets.values())
    new_to_db = sorted(n for host in targets for n in targets[host] if n not in known)
    print("\n%d names need stats; %d of them are not in the item database at all"
          % (total, len(new_to_db)), flush=True)
    if new_to_db[:15]:
        print("  e.g. " + ", ".join(new_to_db[:15]))
    if dry:
        return

    added, scanned = {}, 0
    for host, names in targets.items():
        batch = sorted(names)
        for i in range(0, len(batch), 50):
            chunk = batch[i:i + 50]
            for title, wt in wikitext(host, chunk).items():
                scanned += 1
                s = stats_from(wt)
                if s and title not in stats:
                    added[title] = s
            time.sleep(0.3)
        print("  %-24s done (%d found so far)" % (host, len(added)), flush=True)

    stats.update(added)
    for path in (os.path.join(BASE, "loadout_stats.json"), os.path.join(DATA, "loadout_stats.json")):
        if os.path.exists(path):
            json.dump(stats, open(path, "w", encoding="utf-8"))

    withdmg = sum(1 for s in added.values() if "damage" in s)
    print("\nscanned %d pages, added %d entries (%d with a damage figure)"
          % (scanned, len(added), withdmg))
    print("stats file now holds %d items" % len(stats))
    json.dump(sorted(added), open(os.path.join(BASE, "weapon_stats_added.json"), "w"), indent=1)
    print("names added listed in pipeline/weapon_stats_added.json")


if __name__ == "__main__":
    main()
