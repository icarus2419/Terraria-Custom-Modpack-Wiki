"""Builds loadouts.html.

The page answers one question at a time: at this boss, playing this class, what do I equip?
It renders that as a Terraria equipment panel -- armour slot, five accessory slots, a weapon
hotbar, ammo and buff rows -- with a single pick per slot. Everything else the guides list is
kept, ranked, and folded away under "all options", so nothing is lost and nothing is invented:
each featured pick states the basis it was chosen on.
"""
import json, os, re
BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
from gen_css import CSS as BASECSS
import site_common as SC

def load(name):
    for p in (os.path.join(BASE, name), os.path.join(ROOT, "data", name)):
        if os.path.exists(p):
            return json.load(open(p, encoding="utf-8"))
    raise SystemExit("missing data file: " + name)

L     = load("loadouts.json")
SP    = load("loadout_sprites.json")
ICON  = load("boss_icons.json")
STATS = load("loadout_stats.json")

# loadout_stats.py used to cut set bonuses at 150 chars and tooltips at 170, mid-word.
# The caps are higher now, but a dataset built under the old ones is still around: end
# those strings on a whole word and mark them as cut rather than printing half a word.
def _untrunc(text, cap):
    if len(text) != cap: return text
    cut = text[:cap].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return (cut or text) + "\u2026"
for _s in STATS.values():
    if _s.get("setbonus"): _s["setbonus"] = _untrunc(_s["setbonus"], 150)
    if _s.get("tip"):      _s["tip"]      = _untrunc(_s["tip"], 170)

STAGES, ORDER = L["stages"], L["order"]
CLASS_META, CATO, DATA = L["class_meta"], L["cat_order"], L["data"]

SHARED  = ["Mixed", "All Classes"]                       # gear the guides mark as class-agnostic
CLASSES = [c for c in L["class_order"] if c not in SHARED]
MODCOL  = {"vanilla":"#6f7794", "thorium":"#3f9e8c", "spirit":"#5a80c9", "stars":"#c2a1e8"}
WIKI    = {"vanilla":"Terraria", "thorium":"Thorium", "spirit":"Spirit", "stars":"Stars Above"}

# ---------------------------------------------------------------- zones
# Every category in cat_order lands in exactly one slot area of the panel.
ZACC  = ["Accessories", "Mobility Accessories", "Offensive Accessories", "Survivability Accessories"]
ZWEP  = ["Weapons", "Single-Target Weapons", "Crowd-Control Weapons", "Support Weapons",
         "Whips", "Minions", "Sentries", "Stellar Novas"]
ZUTIL = ["Techniques", "Glyphs", "Support Tools", "Mounts", "Stellar Array"]
ZONE  = {"Armour":"armour", "Ammunition":"ammo", "Buffs":"buff"}
for c in ZACC:  ZONE[c] = "acc"
for c in ZWEP:  ZONE[c] = "wep"
for c in ZUTIL: ZONE[c] = "util"
missing = [c for c in CATO if c not in ZONE]
if missing: raise SystemExit("categories with no panel zone: %r" % missing)

SLOTS = {"armour":1, "acc":5, "wep":6, "ammo":4, "buff":6, "util":4}

def num(x):
    m = re.match(r"\s*(\d+(?:\.\d+)?)", str(x if x is not None else ""))
    return float(m.group(1)) if m else None

def metric(r):
    s = STATS.get(r["n"]) or {}
    z = ZONE.get(r["c"])
    if z == "armour": return num(s.get("defense"))
    if z == "wep":    return num(s.get("damage"))
    return None

def pri(note):
    """The vanilla guide ranks its own picks. Nothing else does."""
    n = (note or "").strip().lower()
    if n.startswith("best"): return 0
    if n == "second best":   return 1
    return 2

def sortkey(r):
    return (pri(r["note"]), -(metric(r) or 0), r["i"])

def rolekey(r):
    return (r["note"] or r["c"]) if ZONE.get(r["c"]) == "acc" else r["c"]

# ---------------------------------------------------------------- rows
def rows_for(stage, cls):
    out = []
    mods = DATA.get(stage, {}).get(cls)
    if not mods: return out
    for m, boxes in mods.items():
        mod   = "vanilla" if m == "_carry" else ("thorium" if m == "_tharmour" else m)
        carry = "" if m not in ("_carry", "_tharmour") else m
        for b in boxes:
            for it in b["items"]:
                out.append({"n":it["name"], "u":it.get("url") or "", "m":mod, "c":b["t"],
                            "note":it.get("note"), "src":b["src"], "carry":carry})
    return out

def pool(stage, cls):
    """The class's own gear verbatim -- a wiki that lists one item under two roles keeps
    both listings -- then the class-agnostic gear, minus anything already present."""
    own, pairs, res = set(), set(), []
    for r in rows_for(stage, cls):
        key = (r["n"], r["c"])
        if key in pairs: continue
        pairs.add(key); own.add(r["n"])
        r["shared"] = 0; r["i"] = len(res); res.append(r)
    for c in SHARED:
        for r in rows_for(stage, c):
            key = (r["n"], r["c"])
            if key in pairs or r["n"] in own: continue
            pairs.add(key)
            r["shared"] = 1; r["i"] = len(res); res.append(r)
    return res

def uniq(rows):
    """A slot can only hold one of a thing, whatever its role."""
    seen, out = set(), []
    for r in rows:
        if r["n"] in seen: continue
        seen.add(r["n"]); out.append(r)
    return out

def choose(cands, n):
    """Best-marked first, then strongest published stat, then the wiki's own order --
    but cover distinct roles before doubling up, so the hotbar is not six broadswords."""
    ranked, picked, used, taken = sorted(cands, key=sortkey), [], set(), set()
    for r in ranked:
        k = rolekey(r)
        if k in used: continue
        picked.append(r); used.add(k); taken.add(r["n"])
        if len(picked) == n: return picked
    for r in ranked:
        if r["n"] in taken: continue
        picked.append(r); taken.add(r["n"])
        if len(picked) == n: break
    return picked

def basis(r, cands):
    """(short label for the slot, full sentence for the tooltip)."""
    note, p, w = (r["note"] or "").strip(), pri(r["note"]), WIKI.get(r["m"], r["m"])
    if p == 0:
        return ["Best \u00b7 %s" % w, "Marked \u201c%s\u201d by the %s guide" % (note, w)]
    if p == 1:
        return ["2nd best \u00b7 %s" % w, "Marked \u201cSecond Best\u201d by the %s guide" % w]
    mv    = metric(r)
    known = [k for k in (metric(c) for c in cands) if k is not None]
    if mv is not None and len(known) > 1 and mv >= max(known):
        unit = "defence" if ZONE.get(r["c"]) == "armour" else "damage"
        return ["%g %s \u00b7 highest here" % (mv, unit),
                "%g %s \u2014 the highest of the %d listed here with published stats"
                % (mv, unit, len(known))]
    return ["First listed \u00b7 %s" % w,
            "Listed first by the %s guide, under %s" % (w, r["src"])]

# ---------------------------------------------------------------- build
ITEMS = {}
def reg(r):
    if r["n"] not in ITEMS: ITEMS[r["n"]] = [r["u"], r["m"]]

def pack(r, why=None):
    reg(r)
    return [r["n"], r["c"], r["note"] or "", r["new"], r["shared"], r["carry"],
            why[0] if why else "", why[1] if why else ""]

PANEL, ALTS, CARRY, HAS, OWN, UPFROM = {}, {}, {}, {}, {}, {}
LAST = {}      # class -> zone -> (top pick, the checkpoint it was picked at)
for si, st in enumerate(ORDER):
    PANEL[st], ALTS[st], CARRY[st], OWN[st], UPFROM[st] = {}, {}, {}, {}, {}
    for cls in CLASSES:
        p = pool(st, cls)
        if not p: continue
        OWN[st][cls] = 1 if rows_for(st, cls) else 0
        if OWN[st][cls]: HAS.setdefault(cls, []).append(st)
        # "new here" means new since this class last had a published list -- Healer, for one,
        # is absent at Pre-Moon Lord, so comparing against the stage before would call gear
        # new that the guide itself says carries over.
        prev = None
        for j in range(si - 1, -1, -1):
            if rows_for(ORDER[j], cls):
                prev = {x["n"] for x in pool(ORDER[j], cls)}
                break
        for r in p:
            r["new"] = 1 if (prev is not None and not r["carry"] and r["n"] not in prev) else 0

        by = {}
        for r in p: by.setdefault(ZONE[r["c"]], []).append(r)
        zones = {}
        for z, n in SLOTS.items():
            cands = uniq(by.get(z) or [])
            if not cands: continue
            zones[z] = [pack(r, basis(r, cands)) for r in choose(cands, n)]
        PANEL[st][cls] = zones
        # what the top pick in each slot replaces, so the panel shows the upgrade and not
        # just a list. Only compared against checkpoints where this class had its own list.
        ups = {}
        if OWN[st][cls]:
            seen_last = LAST.setdefault(cls, {})
            for z, rows in zones.items():
                was = seen_last.get(z)
                if was and was[0] != rows[0][0]:
                    ups[z] = [was[0], was[1]]
            for z, rows in zones.items():
                seen_last[z] = (rows[0][0], st)
        UPFROM[st][cls] = ups

        cats = {}
        for r in p: cats.setdefault(r["c"], []).append(r)
        ALTS[st][cls] = [[c, [pack(r) for r in sorted(cats[c], key=sortkey)]]
                         for c in CATO if c in cats]

        # "no new armour at this checkpoint -- these carry over from <stage>"
        cn = {}
        for r in p:
            if r["carry"] and r["c"] not in cn: cn[r["c"]] = [r["carry"], r["src"]]
        if cn: CARRY[st][cls] = cn

n_items = sum(len(b["items"]) for s in DATA.values() for c in s.values()
              for m in c.values() for b in m)

payload = json.dumps(
    {"stages":STAGES, "order":ORDER, "classes":CLASSES, "class_meta":CLASS_META,
     "modcol":MODCOL, "wiki":WIKI, "slots":SLOTS, "panel":PANEL, "alts":ALTS,
     "carry":CARRY, "has":HAS, "own":OWN, "upfrom":UPFROM,
     "items":ITEMS, "zone":ZONE, "cat_order":CATO,
     "sprites":SP, "icons":ICON, "stats":STATS},
    separators=(",", ":")).replace("<", "\\u003c")

EXTRA = """
<style>
/* ---------- progression rail: the whole game, left to right ---------- */
.railwrap{position:sticky; top:var(--navh,42px); z-index:50; background:var(--surface);
  border-bottom:1px solid var(--line); box-shadow:0 10px 22px -20px rgba(0,0,0,.8)}
.rail{display:flex; align-items:flex-start; overflow-x:auto; padding:8px 0 2px; scrollbar-width:thin}
.rail::-webkit-scrollbar{height:6px}
.rail::-webkit-scrollbar-thumb{background:var(--line-strong); border-radius:3px}
button.step{position:relative; flex:0 0 auto; min-width:82px; display:flex; flex-direction:column;
  align-items:center; gap:4px; padding:2px 4px 5px; background:none; border:0; cursor:pointer;
  font:inherit; color:var(--ink-3)}
button.step::before{content:""; position:absolute; top:16px; left:0; width:50%; height:2px;
  background:var(--line-strong)}
button.step::after{content:""; position:absolute; top:16px; left:50%; width:50%; height:2px;
  background:var(--line-strong)}
button.step:first-child::before, button.step:last-child::after{display:none}
button.step.done::before, button.step.done::after{background:var(--brass)}
button.step[aria-current="true"]::before{background:var(--brass)}
.step .dot{position:relative; z-index:1; width:32px; height:32px; border-radius:50%; flex:none;
  display:grid; place-items:center; background:var(--slot-bg); border:2px solid var(--line-strong)}
.step .dot img{max-width:19px; max-height:19px; width:auto; height:auto; opacity:.75}
.step .dot .n{font-family:"JetBrains Mono",monospace; font-size:12px; color:var(--ink-3)}
.step .lbl{font-size:11px; line-height:1.2; text-align:center; max-width:92px; color:var(--ink-2)}
.step:hover .dot{border-color:var(--brass-line)}
.step:hover .lbl{color:var(--ink)}
.step.done .dot{border-color:var(--brass-line)}
.step.done .dot img{opacity:.95}
.step[aria-current="true"] .dot{border-color:var(--brass); background:var(--brass-soft);
  box-shadow:0 0 0 4px color-mix(in srgb,var(--brass) 22%, transparent)}
.step[aria-current="true"] .dot img{opacity:1}
.step[aria-current="true"] .lbl{color:var(--brass); font-weight:700}
.step.youarehere .dot{box-shadow:0 0 0 3px color-mix(in srgb,var(--pre) 55%, transparent)}
.step.youarehere::after{content:""}
.railgate{flex:0 0 auto; align-self:stretch; display:flex; flex-direction:column; align-items:center;
  justify-content:flex-start; padding:0 9px; gap:4px}
.railgate .bar{width:0; flex:1; border-left:2px dashed var(--hard-line); min-height:44px}
.railgate span{font-family:"Pixelify Sans",sans-serif; font-size:8.5px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--hard); writing-mode:vertical-rl; text-orientation:mixed}

/* ---------- class strip ---------- */
.classbar{display:flex; align-items:center; gap:6px; overflow-x:auto; padding:0 0 7px;
  scrollbar-width:none}
.classbar::-webkit-scrollbar{display:none}
.classbar .lbl{font-family:"Pixelify Sans",sans-serif; font-size:9.5px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--ink-3); flex:none; padding-right:2px}
button.cchip{flex:0 0 auto; display:inline-flex; align-items:center; gap:6px; font:inherit;
  font-size:12.5px; cursor:pointer; padding:4px 12px; border-radius:100px; color:var(--ink-2);
  background:var(--surface-2); border:1px solid var(--line-strong)}
button.cchip i{width:8px; height:8px; border-radius:50%; background:var(--ccol); flex:none}
button.cchip:hover{border-color:var(--ccol); color:var(--ink)}
button.cchip[aria-pressed="true"]{background:color-mix(in srgb,var(--ccol) 20%, var(--surface));
  border-color:var(--ccol); color:var(--ink); font-weight:700}
button.cchip.none{opacity:.45}

/* ---------- stage header ---------- */
.lo-main{padding:14px 0 56px}
footer b.lg{color:var(--src); font-weight:600}
.stagehead{background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
  box-shadow:var(--shadow); padding:15px 18px; margin-bottom:14px; display:flex; gap:18px;
  align-items:center; flex-wrap:wrap}
.stagehead .bossic{width:54px; height:54px; flex:none; display:grid; place-items:center;
  background:var(--slot-bg); border:1px solid var(--brass-line); border-radius:6px;
  box-shadow:inset 0 1px 0 var(--slot-in)}
.stagehead .bossic img{max-width:36px; max-height:36px; width:auto; height:auto}
.stagehead .txt{min-width:220px; flex:1}
.stagehead .eyebrow{margin:0 0 2px}
.stagehead h2{margin:0 0 4px; font-family:"Pixelify Sans",sans-serif; font-size:25px; line-height:1.1}
.stagehead p{margin:0; color:var(--ink-2); font-size:13px; max-width:74ch}
.stagehead p b{color:var(--ink)}
.progbar{flex:none; width:170px}
.progbar .track{height:6px; border-radius:3px; background:var(--surface-3); overflow:hidden}
.progbar .fill{height:100%; background:var(--brass)}
.progbar .cap{margin:5px 0 0; font-family:"JetBrains Mono",monospace; font-size:10px; color:var(--ink-3)}

/* ---------- the equipment panel ---------- */
.pnl{background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
  box-shadow:var(--shadow); overflow:hidden; margin-bottom:14px}
.pnl > .ph-stage{display:flex; align-items:center; gap:9px; flex-wrap:wrap; padding:8px 15px;
  border-top:3px solid var(--ccol); border-bottom:1px solid var(--line);
  background:linear-gradient(180deg, color-mix(in srgb,var(--brass-soft) 40%, var(--surface-2)), var(--surface-2));
  font-size:12.5px; color:var(--ink-2)}
.ph-stage .sic{width:26px; height:26px; flex:none; display:grid; place-items:center;
  background:var(--slot-bg); border:1px solid var(--brass-line); border-radius:4px}
.ph-stage .sic img{max-width:18px; max-height:18px; width:auto; height:auto}
.ph-stage b{font-family:"Pixelify Sans",sans-serif; font-size:16px; color:var(--ink); font-weight:600}
.ph-stage .era{margin:0}
.ph-stage .ln{color:var(--ink-3); min-width:0}
.ph-stage .cnt{margin-left:auto; font-family:"JetBrains Mono",monospace; font-size:11px;
  color:var(--ink-3); white-space:nowrap}
.pnl > header{display:flex; align-items:baseline; gap:10px; flex-wrap:wrap; padding:9px 15px;
  border-bottom:1px solid var(--line); background:var(--surface-2)}
.pnl > header h3{margin:0; font-family:"Pixelify Sans",sans-serif; font-size:17px; color:var(--ccol)}
.pnl > header .blurb{margin:0; font-size:11.5px; color:var(--ink-3)}
.pnl > header .tagr{margin-left:auto; font-family:"JetBrains Mono",monospace; font-size:10px;
  color:var(--ink-3)}
.equip{display:grid; grid-template-columns:minmax(290px,380px) minmax(0,1fr)}
@media (max-width:900px){ .equip{grid-template-columns:minmax(0,1fr)} .eq-l{border-right:0 !important;
  border-bottom:1px solid var(--line)} }
.eq-l{border-right:1px solid var(--line)}
.eq-l, .eq-r{padding:13px 15px 15px}
.zone + .zone{margin-top:15px; padding-top:13px; border-top:1px dashed var(--line)}
.zh{display:flex; align-items:baseline; gap:8px; margin:0 0 8px;
  font-family:"Pixelify Sans",sans-serif; font-size:10px; letter-spacing:.11em; text-transform:uppercase;
  color:var(--ink-3); font-weight:500}
.zh .of{margin-left:auto; font-family:"JetBrains Mono",monospace; font-size:10px; letter-spacing:0;
  text-transform:none}

.slot{position:relative; width:46px; height:46px; flex:none; display:grid; place-items:center;
  background:var(--slot-bg); border:1px solid var(--slot-line); border-radius:4px;
  box-shadow:inset 0 1px 0 var(--slot-in)}
.slot img{max-width:34px; max-height:34px; width:auto; height:auto}
.slot::after{content:""; position:absolute; left:2px; right:2px; bottom:0; height:3px;
  background:var(--src,transparent); border-radius:2px}
.slot.big{width:64px; height:64px}
.slot.big img{max-width:48px; max-height:48px}
.slot.empty{border-style:dashed; background:transparent; box-shadow:none}
.slot.empty::after{display:none}
.slot .idx{position:absolute; top:1px; left:3px; font-family:"JetBrains Mono",monospace;
  font-size:9.5px; color:var(--ink-3)}
.slot .ph{font-size:15px; color:var(--line-strong)}

.slotrow{display:flex; align-items:center; gap:11px; padding:4px 0}
.slotrow .nm{min-width:0; display:flex; flex-direction:column; line-height:1.3}
.slotrow .nm .top{display:flex; align-items:center; gap:6px; flex-wrap:wrap}
.slotrow .nm a, .slotrow .nm span.pick{font-size:13.5px; font-weight:600; color:var(--ink);
  text-decoration:none}
.slotrow .nm a:hover{color:var(--brass)}
.slotrow .sub{font-size:10.5px; color:var(--ink-3)}
.slotrow.void .nm .pick{color:var(--ink-3); font-weight:400; font-style:italic; font-size:12.5px}
.setb{margin:7px 0 0; font-size:11.5px; color:var(--ink-2); line-height:1.45;
  border-left:2px solid var(--brass); padding-left:8px}

.hotbar{display:grid; grid-template-columns:repeat(auto-fill,minmax(100px,1fr)); gap:9px}
.hb{display:flex; flex-direction:column; align-items:center; gap:5px; text-align:center;
  text-decoration:none; color:inherit}
.hb .slot{width:52px; height:52px}
.hb .slot img{max-width:38px; max-height:38px}
.hb .nm{font-size:11.5px; line-height:1.25; color:var(--ink); font-weight:600}
.hb:hover .nm{color:var(--brass)}
.hb .role{font-family:"Pixelify Sans",sans-serif; font-size:8.5px; letter-spacing:.07em;
  text-transform:uppercase; color:var(--ink-3)}
.hb .hbtags{display:flex; gap:4px; flex-wrap:wrap; justify-content:center}
.slotrow .sub.why{color:var(--brass); opacity:.85; font-style:italic}
.minigrid{display:grid; grid-template-columns:repeat(auto-fill,minmax(88px,1fr)); gap:8px}
.minigrid .hb .slot{width:42px; height:42px}
.minigrid .hb .slot img{max-width:30px; max-height:30px}
.minigrid .hb .nm{font-size:10.5px; font-weight:500}

.tag{font-family:"Pixelify Sans",sans-serif; font-size:8.5px; letter-spacing:.08em;
  text-transform:uppercase; border-radius:100px; padding:1px 6px; white-space:nowrap}
.tag.new{color:var(--pre); border:1px solid var(--pre-line); background:var(--pre-soft)}
.tag.any{color:var(--ink-3); border:1px solid var(--line-strong)}
.tag.best{color:var(--brass-bright); border:1px solid var(--brass-line)}
.tag.rec{color:var(--brass-bright); border:1px solid var(--brass); background:var(--brass-soft);
  font-weight:600}
.slotrow.toppick{background:color-mix(in srgb,var(--brass) 6%, transparent);
  border-radius:6px; margin:0 -6px; padding-left:6px; padding-right:6px}
.slotrow .upfrom{font-size:11px; color:var(--ink-2); margin-top:3px; line-height:1.4}
.slotrow .upfrom b{color:var(--ink); font-weight:600}
.slotrow .upfrom .arrow{color:var(--pre); font-weight:700; margin-right:4px}
.hb .upmini{font-size:9.5px; color:var(--ink-3); line-height:1.3}
.carrynote{margin:0 0 8px; font-size:11px; color:var(--ink-3); font-style:italic; line-height:1.45}

.howto{display:flex; gap:10px; flex-wrap:wrap; margin:10px 0 0}
.howto li{display:flex; align-items:center; gap:7px; font-size:12px; color:var(--ink-2);
  background:color-mix(in srgb,var(--brass) 9%, transparent); border:1px solid var(--brass-line);
  border-radius:100px; padding:3px 12px 3px 4px; list-style:none}
.howto b{display:grid; place-items:center; width:19px; height:19px; border-radius:50%;
  background:var(--brass); color:var(--surface); font-family:"JetBrains Mono",monospace;
  font-size:10.5px; flex:none}

/* ---------- alternatives ---------- */
.altwrap{margin-top:6px}
.altwrap > h3{margin:20px 0 3px; font-family:"Pixelify Sans",sans-serif; font-size:14px}
.altwrap > p.lede{margin:0 0 11px; font-size:12.5px; color:var(--ink-2); max-width:76ch}
details.alt{background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
  box-shadow:var(--shadow); margin-bottom:8px}
details.alt > summary{display:flex; align-items:center; gap:9px; cursor:pointer; padding:9px 14px;
  list-style:none; font-family:"Pixelify Sans",sans-serif; font-size:12.5px; color:var(--ink-2)}
details.alt > summary::-webkit-details-marker{display:none}
details.alt > summary::before{content:"+"; font-family:"JetBrains Mono",monospace; font-size:13px;
  color:var(--brass); width:13px; text-align:center; flex:none}
details.alt[open] > summary::before{content:"\\2212"}
details.alt > summary:hover{color:var(--ink)}
details.alt > summary .cnt{margin-left:auto; font-family:"JetBrains Mono",monospace; font-size:10.5px;
  color:var(--ink-3)}
.altbody{padding:0 14px 12px}
.altcat + .altcat{margin-top:11px}
.altcat h4{margin:0 0 6px; font-family:"Pixelify Sans",sans-serif; font-size:9.5px; letter-spacing:.09em;
  text-transform:uppercase; color:var(--ink-3); font-weight:500; display:flex; gap:7px; align-items:center}
.altcat h4 .cnt{margin-left:auto; font-family:"JetBrains Mono",monospace; font-size:9.5px;
  letter-spacing:0; text-transform:none}
.gearlist{display:flex; flex-wrap:wrap; gap:5px; margin:0; padding:0; list-style:none}
.gear{display:inline-flex; align-items:center; gap:6px;
  background:color-mix(in srgb, var(--src) 24%, var(--surface-2));
  border:1px solid color-mix(in srgb, var(--src) 85%, transparent);
  border-radius:100px; padding:3px 10px 3px 3px; font-size:12px; color:var(--ink); text-decoration:none}
a.gear:hover{border-color:var(--src); background:color-mix(in srgb, var(--src) 42%, var(--surface-2))}
.gear .gsp{width:24px; height:24px; display:grid; place-items:center; background:var(--slot-bg);
  border:1px solid var(--slot-line); border-radius:3px; flex:none}
.gear .gsp img{max-width:19px; max-height:19px; width:auto; height:auto}
.gear .qual{font-size:9.5px; color:var(--ink-3); font-style:italic}
.gear.equipped{box-shadow:0 0 0 1px color-mix(in srgb,var(--brass) 55%, transparent)}
.gear .eq{font-family:"Pixelify Sans",sans-serif; font-size:8.5px; letter-spacing:.06em;
  text-transform:uppercase; color:var(--brass-bright)}

/* ---------- step through ---------- */
.stepnav{display:flex; gap:10px; margin-top:18px; flex-wrap:wrap}
button.bignav{flex:1 1 260px; display:flex; align-items:center; gap:11px; font:inherit; cursor:pointer;
  text-align:left; background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
  box-shadow:var(--shadow); padding:11px 15px; color:var(--ink-2)}
button.bignav:hover{border-color:var(--brass); color:var(--ink)}
button.bignav[disabled]{opacity:.4; cursor:default}
button.bignav.fwd{justify-content:flex-end; text-align:right}
button.bignav .k{font-family:"Pixelify Sans",sans-serif; font-size:9.5px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--ink-3); display:block}
button.bignav .v{font-family:"Pixelify Sans",sans-serif; font-size:15px; color:inherit}
button.bignav .ar{font-size:19px; color:var(--brass)}

.keybar{display:flex; gap:8px; flex-wrap:wrap; align-items:center; margin-bottom:14px;
  background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
  box-shadow:var(--shadow); padding:8px 14px}
.keybar .lbl{font-family:"Pixelify Sans",sans-serif; font-size:9.5px; letter-spacing:.09em;
  text-transform:uppercase; color:var(--ink-3); margin-right:2px}
.keybar .k{display:inline-flex; align-items:center; gap:6px; font-size:11.5px; color:var(--ink);
  background:color-mix(in srgb, var(--src) 24%, var(--surface-2));
  border:1px solid color-mix(in srgb, var(--src) 85%, transparent); border-radius:100px; padding:2px 10px}
.keybar .k i{width:8px; height:8px; border-radius:50%; display:inline-block; background:var(--src)}
.keybar .sep{flex:1}
@media (max-width:760px){
  .railwrap{position:static}
  button.step{min-width:74px}
  .step .lbl{font-size:10px; max-width:78px}
  .stagehead{padding:13px 14px; gap:12px}
  .stagehead h2{font-size:21px}
  .progbar{width:100%}
  .howto{gap:6px}
}

.nodata{background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
  box-shadow:var(--shadow); padding:15px 18px; margin-bottom:14px}
.nodata p{margin:0 0 8px; font-size:13px; color:var(--ink-2); max-width:74ch}
.nodata .jump{display:flex; gap:6px; flex-wrap:wrap}
.nodata button{font:inherit; font-size:12px; cursor:pointer; background:var(--surface-2);
  border:1px solid var(--line-strong); border-radius:100px; padding:3px 12px; color:var(--ink-2)}
.nodata button:hover{border-color:var(--brass); color:var(--brass)}

/* ---------- hover stat card ---------- */
#statcard{position:fixed; z-index:200; max-width:300px; pointer-events:none; opacity:0;
  background:var(--tip-bg); color:var(--tip-ink); border:1px solid var(--brass-line);
  border-radius:6px; padding:10px 12px; box-shadow:0 10px 30px -8px rgba(0,0,0,.6);
  transition:opacity .09s ease}
#statcard[data-show="1"]{opacity:1}
#statcard .sc-h{display:flex; align-items:center; gap:8px; margin-bottom:7px}
#statcard .sc-sp{width:30px; height:30px; flex:none; display:grid; place-items:center;
  background:rgba(255,255,255,.07); border:1px solid rgba(255,255,255,.15); border-radius:4px}
#statcard .sc-sp img{max-width:24px; max-height:24px; width:auto; height:auto}
#statcard h5{margin:0; font-family:"Pixelify Sans",sans-serif; font-size:14px; line-height:1.15; color:#fff}
#statcard .sc-kind{font-size:10px; letter-spacing:.05em; text-transform:uppercase;
  color:color-mix(in srgb,var(--brass-bright) 80%, #fff); font-family:"Pixelify Sans",sans-serif}
#statcard .sc-rows{display:grid; grid-template-columns:auto 1fr; gap:2px 12px; font-size:12px;
  margin-bottom:6px}
#statcard .sc-rows dt{color:rgba(223,227,245,.6); font-size:10.5px; letter-spacing:.04em;
  text-transform:uppercase; font-family:"Pixelify Sans",sans-serif}
#statcard .sc-rows dd{margin:0; font-family:"JetBrains Mono",monospace; font-variant-numeric:tabular-nums;
  color:#fff}
#statcard .sc-rows dd.dmg{color:var(--brass-bright); font-weight:700}
#statcard .sc-tip{font-size:11.5px; line-height:1.45; color:rgba(223,227,245,.85);
  border-top:1px solid rgba(255,255,255,.12); padding-top:6px; margin:0}
#statcard .sc-bonus{font-size:11.5px; line-height:1.45; color:#fff; margin:0 0 4px;
  border-left:2px solid var(--brass); padding-left:7px}
#statcard .sc-none{font-size:11.5px; color:rgba(223,227,245,.6); margin:0}
@media (max-width:620px){ #statcard{display:none} }
</style>
"""

BODY = """
<header class="masthead slim"><div class="wrap mast-in">
  <div class="brandline"><div>
    <h1>Loadouts</h1>
    <p class="tagline">Pick the boss, pick your class, equip what is in the slots.
    <span class="dim">@@NIT@@ gear entries from four wikis on one timeline.</span></p>
  </div></div>
</div></header>

<div class="railwrap"><div class="wrap">
  <div class="rail" id="rail" role="tablist" aria-label="Boss progression"></div>
  <div class="classbar" id="classbar"><span class="lbl">Playing as</span></div>
</div></div>

<main class="wrap lo-main">
  <div id="panelhost"></div>
  <div class="altwrap" id="alts"></div>
  <div class="stepnav" id="stepnav"></div>
</main>

<footer><div class="wrap fgrid">
  <div><h2 class="fh">How a slot is filled</h2>
    <p>The guides list far more gear than you can wear. Each slot takes the first of: something the
    wiki itself marks <em>Best</em>; then the highest published defence or damage; then whatever that
    wiki lists first. Roles are spread before doubling up, so the hotbar is not six broadswords.
    Every pick shows the reason it was chosen, and nothing is invented &mdash; if a wiki publishes no
    ranking and no stats, the slot says so.</p></div>
  <div><h2 class="fh">How the checkpoints line up</h2>
    <p>Each mod names its stages differently &mdash; Thorium's <em>Pre-Eater of Worlds / Brain of
    Cthulhu</em>, Spirit's <em>Pre-Evil Boss</em> and Stars Above's <em>Pre-The Vagrant of Space and
    Time</em> all sit at the same point. They are mapped onto one timeline, and every item still
    shows the wiki and the stage name it came from.</p></div>
  <div><h2 class="fh">Reading the panel</h2>
    <p>The strip under each slot is the wiki that recommends it &mdash;
    <b class="lg" style="--src:#6f7794">Terraria</b>,
    <b class="lg" style="--src:#3f9e8c">Thorium</b>,
    <b class="lg" style="--src:#5a80c9">Spirit</b>,
    <b class="lg" style="--src:#c2a1e8">Stars Above</b>.
    Pick the boss on the timeline, then your class; arrow keys walk the run.</p></div>
  <div><h2 class="fh">What the tags mean</h2>
    <p><b>New here</b> means the gear was not in this class's list at its previous checkpoint &mdash;
    at Pre-Moon Lord the guides publish no Healer list at all, so its next list is compared against
    Pre-Lunatic Cultist rather than pretending everything is new. <b>Any class</b> means the entry
    comes from a guide's mixed-class section, not from this class's own. Gear the guides carry
    forward rather than re-listing says so, and where it carries from.</p></div>
  <div><h2 class="fh">Nothing is hidden</h2>
    <p>The panel is a recommendation, not the whole list. <b>All options</b> underneath holds every
    entry the guides publish for that class at that checkpoint, ranked the same way, with the
    equipped ones marked. Gear tagged <em>any class</em> comes from the guides' own mixed-class
    sections. Hover anything for its stats.</p></div>
</div></footer>

<script id="loadouts" type="application/json">@@PAYLOAD@@</script>
"""

for a, b in [("@@NST@@", str(len(STAGES))), ("@@NCL@@", str(len(CLASSES))),
             ("@@NIT@@", "{:,}".format(n_items)), ("@@PAYLOAD@@", payload)]:
    BODY = BODY.replace(a, b)

HTML = (SC.head('loadouts.html', 'Loadouts by Boss', 'Pick the boss and your class, and get one filled equipment panel: armour, five accessories, a weapon hotbar, ammo and buffs, from four wikis on one timeline.') + BASECSS + SC.NAV_CSS + SC.PROGRESS_CSS + EXTRA
        + SC.nav("loadouts.html", str(len(STAGES)) + " checkpoints &middot; "
                 + str(len(CLASSES)) + " classes")
        + SC.runbar() + BODY)
HTML = HTML.replace("<title>Joseph's Modpack Wiki</title>", "<title>Loadouts by Boss</title>", 1)

JS = r"""
<script>
(function(){
"use strict";
var D = JSON.parse(document.getElementById("loadouts").textContent);
var STAGES=D.stages, ORDER=D.order, CLASSES=D.classes, CM=D.class_meta, MC=D.modcol, WK=D.wiki,
    SLOTS=D.slots, PANEL=D.panel, ALTS=D.alts, CARRY=D.carry, HAS=D.has, OWN=D.own,
    UPFROM=D.upfrom, ITEMS=D.items,
    ZONE=D.zone, SP=D.sprites, ICON=D.icons||{}, STATS=D.stats||{};

/* Left column of the panel mirrors Terraria's equipment area; right column is what you carry. */
var ZL = [["armour","Armour"], ["acc","Accessories"]];
var ZR = [["wep","Hotbar · weapons"], ["ammo","Ammo"], ["buff","Buffs & potions"],
          ["util","Utility"]];
var ZTITLE={armour:"Armour", acc:"Accessories", wep:"Weapons", ammo:"Ammo",
            buff:"Buffs & potions", util:"Utility"};
function isRank(note){
  var n=(note||"").toLowerCase();
  return n.indexOf("best")===0 || n==="second best";
}

function el(t,c,x){var e=document.createElement(t); if(c)e.className=c; if(x!=null)e.textContent=x; return e;}
function sprite(name, cls){
  var s=SP[name]; if(!s) return null;
  var i=new Image(); i.src=s; i.alt=""; i.className="px"; if(cls)i.loading="lazy"; return i;
}
function stageIdx(k){ return ORDER.indexOf(k); }

/* ---------- state: stage + class, in the hash and remembered ---------- */
var VALID={}; ORDER.forEach(function(k){VALID[k]=1;});
function store(k,v){ try{ localStorage.setItem(k,v); }catch(e){} }
function recall(k){ try{ return localStorage.getItem(k); }catch(e){ return null; } }

var cur=ORDER[0], cls=CLASSES[0];
/* the checkpoint the boss checklist says you are on, if it has been used */
function runStage(){
  try{
    var s=window.PackProgress && window.PackProgress.state();
    return (s && s.started && VALID[s.stage]) ? s.stage : null;
  }catch(e){ return null; }
}
(function init(){
  var h=(location.hash||"").replace(/^#/,"").split("/");
  var hs=decodeURIComponent(h[0]||""), hc=decodeURIComponent(h[1]||"");
  var rs=recall("lo.stage"), rc=recall("lo.class");
  cur = VALID[hs] ? hs : (VALID[rs] ? rs : (runStage() || ORDER[0]));
  cls = CLASSES.indexOf(hc)>=0 ? hc : (CLASSES.indexOf(rc)>=0 ? rc : CLASSES[0]);
})();
function setHash(){
  var h="#"+cur+"/"+encodeURIComponent(cls);
  if(history.replaceState) history.replaceState(null,"",h); else location.hash=h;
  store("lo.stage",cur); store("lo.class",cls);
}

/* ---------- the rail: the whole run, left to right ---------- */
var rail=document.getElementById("rail");
STAGES.forEach(function(s,i){
  if(s[3] && i>0 && !STAGES[i-1][3]){
    var g=el("div","railgate"); g.appendChild(el("span",null,"Hardmode"));
    g.appendChild(el("div","bar")); rail.appendChild(g);
  }
  var b=el("button","step"); b.type="button"; b.dataset.k=s[0];
  b.title=s[1]+" — "+s[2];
  var dot=el("span","dot"), im=sprite(s[0]==="__none" ? "" : "");
  var ic=ICON[s[0]];
  if(ic){ var img=new Image(); img.src=ic; img.alt=""; img.className="px"; dot.appendChild(img); }
  else dot.appendChild(el("span","n",String(i+1)));
  b.appendChild(dot);
  b.appendChild(el("span","lbl", s[4]||s[1]));
  rail.appendChild(b);
});
rail.addEventListener("click",function(e){
  var b=e.target.closest("button.step"); if(!b) return;
  cur=b.dataset.k; setHash(); render(); scrollTop();
});

/* ---------- the class strip ---------- */
var cbar=document.getElementById("classbar");
CLASSES.forEach(function(c){
  var m=CM[c]||["#7d85ab",""];
  var b=el("button","cchip"); b.type="button"; b.dataset.c=c;
  b.style.setProperty("--ccol", m[0]); b.title=m[1];
  b.appendChild(el("i")); b.appendChild(document.createTextNode(c));
  cbar.appendChild(b);
});
cbar.addEventListener("click",function(e){
  var b=e.target.closest("button.cchip"); if(!b) return;
  cls=b.dataset.c; setHash(); render();
});
/* the rail scrolls sideways; stepping with the buttons or the arrow keys should not leave
   the current checkpoint off the end of it. Only touches the rail, never the page. */
function keepRailInView(){
  var act=rail.querySelector('button.step[aria-current="true"]');
  if(!act) return;
  var r=act.getBoundingClientRect(), rr=rail.getBoundingClientRect();
  if(r.left < rr.left+8 || r.right > rr.right-8)
    rail.scrollLeft += (r.left - rr.left) - (rr.width - r.width)/2;
}

function scrollTop(){
  var t=document.getElementById("panelhost");
  var y=t.getBoundingClientRect().top+window.scrollY
        - (parseInt(getComputedStyle(document.documentElement).getPropertyValue("--railh"),10)||150);
  window.scrollTo({top:Math.max(0,y), behavior:"smooth"});
}

/* ---------- one gear row: slot + name + why ---------- */
function tag(cl,txt){ return el("span","tag "+cl,txt); }
function slotBox(name, big){
  var s=el("span","slot"+(big?" big":""));
  var meta=ITEMS[name];
  if(meta) s.style.setProperty("--src", MC[meta[1]]||"#7d85ab");
  var im=sprite(name,1);
  if(im) s.appendChild(im); else s.appendChild(el("span","ph","?"));
  return s;
}
function emptySlot(big){
  var s=el("span","slot empty"+(big?" big":""));
  s.appendChild(el("span","ph","–")); return s;
}
function nameNode(name, extraCls){
  var meta=ITEMS[name]||["",""];
  var n = meta[0] ? el("a") : el("span","pick");
  if(meta[0]){ n.href=meta[0]; n.target="_blank"; n.rel="noopener noreferrer"; n.textContent=name; }
  else n.textContent=name;
  return n;
}
/* pack = [name, cat, note, new, shared, carry, whyShort, whyLong] */
function roleOf(p){ return (p[2] && !isRank(p[2])) ? p[2] : p[1]; }
function flagsFor(rows){
  var roles={}, allNew=true, allAny=true;
  rows.forEach(function(p){
    roles[roleOf(p)]=1;
    if(!p[3]) allNew=false;
    if(!p[4]) allAny=false;
  });
  return {role:Object.keys(roles).length>1, "new":!allNew, any:!allAny,
          allNew:allNew && rows.length>1, allAny:allAny && rows.length>1};
}
function gearRow(p, big, f, isTop, up){
  var row=el("div","slotrow"+(isTop?" toppick":""));
  row.appendChild(slotBox(p[0], big));
  var nm=el("div","nm"), top=el("div","top");
  top.appendChild(nameNode(p[0]));
  if(isTop) top.appendChild(tag("rec","recommended"));
  if(p[3] && (!f || f["new"])) top.appendChild(tag("new","new here"));
  if(p[4] && (!f || f.any))    top.appendChild(tag("any","any class"));
  nm.appendChild(top);
  if(!f || f.role) nm.appendChild(el("div","sub", roleOf(p)));
  if(p[6]){
    var w=el("div","sub why", p[6]);
    if(p[7]) w.title=p[7];
    nm.appendChild(w);
  }
  if(isTop && up) nm.appendChild(upgradeNote(up));
  row.appendChild(nm);
  row.dataset.item=p[0];
  return row;
}

/* up = [previous top pick, the checkpoint it was picked at] */
function upgradeNote(up){
  var d=el("div","upfrom");
  d.appendChild(el("span","arrow","\u2191"));
  d.appendChild(document.createTextNode("upgrade from "));
  var b=el("b",null,up[0]);
  d.appendChild(b);
  var st=STAGES[stageIdx(up[1])];
  if(st) d.appendChild(document.createTextNode(" (" + st[1] + ")"));
  return d;
}
function voidRow(msg, big){
  var row=el("div","slotrow void");
  row.appendChild(emptySlot(big));
  var nm=el("div","nm"); nm.appendChild(el("span","pick", msg)); row.appendChild(nm);
  return row;
}
function hotCell(p, i, f, isTop, up){
  var meta=ITEMS[p[0]]||["",""];
  var a = meta[0] ? el("a","hb") : el("div","hb");
  if(meta[0]){ a.href=meta[0]; a.target="_blank"; a.rel="noopener noreferrer"; }
  var s=slotBox(p[0]);
  if(i!=null) s.appendChild(el("span","idx", String(i===9?0:i+1)));
  a.appendChild(s);
  a.appendChild(el("span","nm", p[0]));
  if(f.role) a.appendChild(el("span","role", roleOf(p)));
  var showNew=p[3]&&f["new"], showAny=p[4]&&f.any;
  if(isTop||showNew||showAny){
    var t=el("span","hbtags");
    if(isTop)   t.appendChild(tag("rec","pick"));
    if(showNew) t.appendChild(tag("new","new"));
    if(showAny) t.appendChild(tag("any","any class"));
    a.appendChild(t);
  }
  if(isTop && up) a.appendChild(el("span","upmini","\u2191 from " + up[0]));
  if(p[7]) a.title=p[6]+" — "+p[7];
  a.dataset.item=p[0];
  return a;
}
function zoneHead(title, right){
  var h=el("div","zh"); h.appendChild(el("span",null,title));
  if(right) h.appendChild(el("span","of", right));
  return h;
}
/* how many entries the guides publish per zone, so a slot count reads "6 of 34" */
function zoneTotals(){
  var cats=(ALTS[cur]||{})[cls]||[], t={};
  cats.forEach(function(c){ var z=ZONE[c[0]]||"util"; t[z]=(t[z]||0)+c[1].length; });
  return t;
}

/* ---------- render ---------- */
var host=document.getElementById("panelhost"),
    altwrap=document.getElementById("alts"),
    stepnav=document.getElementById("stepnav");

function render(){
  var i=stageIdx(cur), st=STAGES[i];
  var here=runStage();
  rail.querySelectorAll("button.step").forEach(function(b){
    var bi=stageIdx(b.dataset.k);
    b.setAttribute("aria-current", b.dataset.k===cur ? "true":"false");
    b.classList.toggle("done", bi<i);
    b.classList.toggle("youarehere", here!==null && b.dataset.k===here);
  });
  keepRailInView();
  var zones=(PANEL[cur]||{})[cls];
  cbar.querySelectorAll("button.cchip").forEach(function(b){
    var on=b.dataset.c===cls;
    b.setAttribute("aria-pressed", on?"true":"false");
    b.classList.toggle("none", !((OWN[cur]||{})[b.dataset.c]));
  });

  /* --- the checkpoint line, built here and placed inside the panel below --- */
  function stageStrip(){
    var d=el("div","ph-stage");
    if(ICON[cur]){
      var ic=el("span","sic"); var im=new Image(); im.src=ICON[cur]; im.alt=""; im.className="px";
      ic.appendChild(im); d.appendChild(ic);
    }
    d.appendChild(el("b",null, st[1]));
    d.appendChild(el("span","era "+(st[3]?"hard":"pre"), st[3]?"hardmode":"pre-hardmode"));
    var line;
    if(i===0) line="a fresh world, nothing killed yet";
    else if(i===STAGES.length-1) line="Moon Lord is down \u2014 "+st[2];
    else line=(i>=2 ? "beaten "+STAGES[i-1][2]+", " : "")+"gearing up for "+st[2];
    d.appendChild(el("span","ln", line));
    d.appendChild(el("span","cnt", (i+1)+" / "+STAGES.length));
    return d;
  }

  /* --- the panel --- */
  host.textContent=""; altwrap.textContent="";
  if(!zones){
    host.appendChild(stageStrip());
    var nd=el("div","nodata");
    nd.appendChild(el("p", null, "The guides publish no "+cls+" setup at "+st[1]+
      ". That is a gap in the source wikis, not a gap in the pack — nothing has been invented to fill it."));
    var got=HAS[cls]||[];
    if(got.length){
      nd.appendChild(el("p","", "Nearest checkpoints that do have one:"));
      var j=el("div","jump");
      var before=got.filter(function(k){return stageIdx(k)<i;}).slice(-2);
      var after =got.filter(function(k){return stageIdx(k)>i;}).slice(0,2);
      before.concat(after).forEach(function(k){
        var b=el("button",null,STAGES[stageIdx(k)][1]); b.type="button";
        b.onclick=function(){ cur=k; setHash(); render(); scrollTop(); };
        j.appendChild(b);
      });
      nd.appendChild(j);
    }
    host.appendChild(nd);
  } else {
    if(!((OWN[cur]||{})[cls])){
      var b=el("div","nodata");
      b.appendChild(el("p", null, "The guides publish no "+cls+" setup at "+st[1]+
        ". Everything below is the gear their mixed-class sections recommend for every class at this "+
        "point — nothing "+cls+"-specific has been invented to fill the gap."));
      var g=HAS[cls]||[];
      if(g.length){
        b.appendChild(el("p","","Checkpoints with a published "+cls+" setup nearest to here:"));
        var jj=el("div","jump");
        var bf=g.filter(function(k){return stageIdx(k)<i;}).slice(-2),
            af=g.filter(function(k){return stageIdx(k)>i;}).slice(0,2);
        bf.concat(af).forEach(function(k){
          var bt=el("button",null,STAGES[stageIdx(k)][1]); bt.type="button";
          bt.onclick=function(){ cur=k; setHash(); render(); scrollTop(); };
          jj.appendChild(bt);
        });
        b.appendChild(jj);
      }
      host.appendChild(b);
    }
    var meta=CM[cls]||["#7d85ab",""];
    var pnl=el("div","pnl"); pnl.style.setProperty("--ccol", meta[0]);
    pnl.appendChild(stageStrip());
    var hd=el("header");
    hd.appendChild(el("h3",null,cls));
    hd.appendChild(el("p","blurb", meta[1]));
    var nfill=0; Object.keys(zones).forEach(function(z){ nfill+=zones[z].length; });
    hd.appendChild(el("span","tagr", nfill+" picked · "+countAll()+" listed"));
    pnl.appendChild(hd);

    var TOT=zoneTotals();
    var eq=el("div","equip"), L=el("div","eq-l"), R=el("div","eq-r");
    ZL.forEach(function(z){ var n=zoneBlock(z[0], z[1], TOT); if(n) L.appendChild(n); });
    ZR.forEach(function(z){ var n=zoneBlock(z[0], z[1], TOT); if(n) R.appendChild(n); });
    if(!L.childNodes.length) L.appendChild(el("p","carrynote","No armour or accessories listed here."));
    if(!R.childNodes.length) R.appendChild(el("p","carrynote","No weapons or consumables listed here."));
    eq.appendChild(L); eq.appendChild(R);
    pnl.appendChild(eq);
    host.appendChild(pnl);
    buildAlts();
  }
  buildStepnav(i);

  function countAll(){
    var a=(ALTS[cur]||{})[cls]||[], n=0;
    a.forEach(function(c){ n+=c[1].length; });
    return n;
  }

  function zoneBlock(z, title, TOT){
    var rows=zones[z]; if(!rows||!rows.length) return null;
    var total=TOT[z]||rows.length, wrap=el("div","zone"), right;
    if(z==="armour")   right = "1 of "+total+(total===1?" set":" sets");
    else if(z==="acc") right = rows.length+" of "+SLOTS.acc+" slots";
    else               right = rows.length+" of "+total+" listed";
    wrap.appendChild(zoneHead(title, right));
    var cn=((CARRY[cur]||{})[cls])||{}, note=null;
    rows.forEach(function(p){ if(!note && p[5] && cn[p[1]]) note=cn[p[1]]; });
    if(note){
      wrap.appendChild(el("p","carrynote", note[0]==="_tharmour"
        ? "Thorium's class guide skips armour here; these sets come from its own Armor page ("+note[1]+")."
        : "The guides list nothing new here — this carries over from "+note[1]+"."));
    }
    var f=flagsFor(rows);
    var nb=[];
    if(f.allNew) nb.push("All new at this checkpoint.");
    if(f.allAny) nb.push("All of these come from the guides' any-class sections.");
    if(nb.length) wrap.appendChild(el("p","carrynote", nb.join(" ")));
    var up=((UPFROM[cur]||{})[cls]||{})[z] || null;
    if(z==="armour" || z==="acc"){
      rows.forEach(function(p, ix){
        wrap.appendChild(gearRow(p, z==="armour", f, ix===0, ix===0 ? up : null));
      });
      if(z==="acc"){
        for(var k=rows.length; k<SLOTS.acc; k++)
          wrap.appendChild(voidRow("slot free — the guides name no more here", false));
      }
      if(z==="armour"){
        var st=STATS[rows[0][0]]||{};
        var dfn = st.defense && rows[0][6].indexOf(st.defense)!==0
                  ? st.defense+" defence · fills head, chest and legs"
                  : "Fills the head, chest and legs slots";
        wrap.appendChild(el("p","carrynote", dfn));
        if(st.setbonus) wrap.appendChild(el("p","setb","Set bonus: "+st.setbonus));
      }
    } else {
      var box=el("div", z==="wep" ? "hotbar" : "minigrid");
      rows.forEach(function(p,ix){
        box.appendChild(hotCell(p, z==="wep"?ix:null, f, ix===0, ix===0 ? up : null));
      });
      wrap.appendChild(box);
    }
    return wrap;
  }

  function buildAlts(){
    var cats=(ALTS[cur]||{})[cls]||[]; if(!cats.length) return;
    var equipped={}, topPick={};
    Object.keys(zones).forEach(function(z){
      zones[z].forEach(function(p, ix){ equipped[p[0]]=1; if(ix===0) topPick[p[0]]=1; });
    });
    altwrap.appendChild(el("h3",null,"Everything else the guides list"));
    altwrap.appendChild(el("p","lede",
      "The panel above is one pick per slot. This is the full published list for "+cls+" at "+st[1]+
      ", in the same ranked order, with what is equipped marked."));
    var byZone={};
    cats.forEach(function(c){ (byZone[ZONE[c[0]]||"util"] = byZone[ZONE[c[0]]||"util"]||[]).push(c); });
    ZL.concat(ZR).forEach(function(zd){
      var z=zd[0], group=byZone[z]; if(!group) return;
      var n=0; group.forEach(function(c){ n+=c[1].length; });
      var d=el("details","alt");
      var sm=el("summary");
      sm.appendChild(el("span",null, ZTITLE[z]));
      sm.appendChild(el("span","cnt", n+" listed"));
      d.appendChild(sm);
      var body=el("div","altbody");
      group.forEach(function(c){
        var box=el("div","altcat"), h4=el("h4",null,c[0]);
        h4.appendChild(el("span","cnt", String(c[1].length)));
        box.appendChild(h4);
        var ul=el("ul","gearlist");
        c[1].forEach(function(p){
          var m=ITEMS[p[0]]||["",""];
          var node = m[0] ? el("a","gear") : el("span","gear");
          node.style.setProperty("--src", MC[m[1]]||"#7d85ab");
          if(m[0]){ node.href=m[0]; node.target="_blank"; node.rel="noopener noreferrer"; }
          node.dataset.item=p[0];
          var sp=sprite(p[0],1);
          if(sp){ var b=el("span","gsp"); b.appendChild(sp); node.appendChild(b); }
          node.appendChild(document.createTextNode(p[0]));
          if(p[2]) node.appendChild(el("span","qual", p[2]));
          if(p[3]) node.appendChild(el("span","qual","new"));
          if(topPick[p[0]]){ node.classList.add("equipped"); node.appendChild(el("span","eq","recommended")); }
          else if(equipped[p[0]]){ node.classList.add("equipped"); node.appendChild(el("span","eq","in the panel")); }
          var li=el("li"); li.appendChild(node); ul.appendChild(li);
        });
        box.appendChild(ul); body.appendChild(box);
      });
      d.appendChild(body); altwrap.appendChild(d);
    });
  }

  function buildStepnav(i){
    stepnav.textContent="";
    function mk(j, fwd){
      var b=el("button","bignav"+(fwd?" fwd":"")); b.type="button";
      if(j<0||j>=STAGES.length){ b.disabled=true; b.appendChild(el("span","v", fwd?"End of the run":"Start of the run")); return b; }
      var t=el("span");
      t.appendChild(el("span","k", fwd?"Next checkpoint":"Previous checkpoint"));
      t.appendChild(el("span","v", STAGES[j][1]));
      if(fwd){ b.appendChild(t); b.appendChild(el("span","ar","→")); }
      else   { b.appendChild(el("span","ar","←")); b.appendChild(t); }
      b.onclick=function(){ cur=ORDER[j]; setHash(); render(); scrollTop(); };
      return b;
    }
    stepnav.appendChild(mk(i-1,false));
    stepnav.appendChild(mk(i+1,true));
  }
}

/* ---------- hover stat card ---------- */
var SCARD=el("div"); SCARD.id="statcard"; SCARD.setAttribute("data-show","0");
document.body.appendChild(SCARD);
function buildStat(name){
  var s=STATS[name]||{};
  SCARD.textContent="";
  var h=el("div","sc-h"), sp=sprite(name);
  if(sp){ var box=el("span","sc-sp"); box.appendChild(sp); h.appendChild(box); }
  var t=el("div"); t.appendChild(el("h5",null,name));
  if(s.kind) t.appendChild(el("div","sc-kind", s.kind));
  h.appendChild(t); SCARD.appendChild(h);
  var rows=[];
  if(s.damage)    rows.push(["Damage", s.damage+(s.dtype?"  "+s.dtype:""), true]);
  if(s.defense)   rows.push(["Defense", s.defense, false]);
  if(s.speed)     rows.push(["Speed", s.speed+(s.use?"  ("+s.use+")":""), false]);
  else if(s.use)  rows.push(["Use time", s.use, false]);
  if(s.knockback) rows.push(["Knockback", s.knockback, false]);
  if(s.crit)      rows.push(["Crit", s.crit, false]);
  if(s.mana)      rows.push(["Mana", s.mana, false]);
  if(s.velocity)  rows.push(["Velocity", s.velocity, false]);
  if(rows.length){
    var dl=el("dl","sc-rows");
    rows.forEach(function(r){
      var dd=el("dd",null,String(r[1])); if(r[2]) dd.className="dmg";
      dl.appendChild(el("dt",null,r[0])); dl.appendChild(dd);
    });
    SCARD.appendChild(dl);
  }
  if(s.setbonus) SCARD.appendChild(el("p","sc-bonus","Set bonus: "+s.setbonus));
  if(s.tip)      SCARD.appendChild(el("p","sc-tip", s.tip));
  if(!rows.length && !s.tip && !s.setbonus)
    SCARD.appendChild(el("p","sc-none","No stats published on the source wiki."));
}
function placeStat(x,y){
  var pad=14, w=SCARD.offsetWidth, h=SCARD.offsetHeight;
  var lx=x+pad, ly=y+pad;
  if(lx+w>window.innerWidth-8) lx=Math.max(8, x-w-pad);
  if(ly+h>window.innerHeight-8) ly=Math.max(8, y-h-pad);
  SCARD.style.left=lx+"px"; SCARD.style.top=ly+"px";
}
function hoverTarget(e){
  return e.target.closest && e.target.closest("[data-item]");
}
document.addEventListener("mouseover",function(ev){
  var t=hoverTarget(ev); if(!t) return;
  buildStat(t.dataset.item); placeStat(ev.clientX,ev.clientY);
  SCARD.setAttribute("data-show","1");
});
document.addEventListener("mousemove",function(ev){
  if(SCARD.getAttribute("data-show")!=="1") return;
  var t=hoverTarget(ev);
  if(t) placeStat(ev.clientX,ev.clientY); else SCARD.setAttribute("data-show","0");
});
document.addEventListener("scroll",function(){ SCARD.setAttribute("data-show","0"); }, true);
document.addEventListener("focusin",function(ev){
  var t=hoverTarget(ev); if(!t) return;
  var r=t.getBoundingClientRect();
  buildStat(t.dataset.item); placeStat(r.left, r.bottom-14);
  SCARD.setAttribute("data-show","1");
});
document.addEventListener("focusout",function(){ SCARD.setAttribute("data-show","0"); });

/* ---------- keyboard: left/right walks the run ---------- */
document.addEventListener("keydown",function(e){
  if(e.metaKey||e.ctrlKey||e.altKey) return;
  var tn=(e.target.tagName||"").toLowerCase();
  if(tn==="input"||tn==="textarea"||e.target.isContentEditable) return;
  var i=stageIdx(cur);
  if(e.key==="ArrowRight" && i<STAGES.length-1){ cur=ORDER[i+1]; setHash(); render(); }
  else if(e.key==="ArrowLeft" && i>0){ cur=ORDER[i-1]; setHash(); render(); }
});

window.addEventListener("hashchange",function(){
  var h=(location.hash||"").replace(/^#/,"").split("/");
  var hs=decodeURIComponent(h[0]||""), hc=decodeURIComponent(h[1]||"");
  var ch=false;
  if(VALID[hs] && hs!==cur){ cur=hs; ch=true; }
  if(CLASSES.indexOf(hc)>=0 && hc!==cls){ cls=hc; ch=true; }
  if(ch){ store("lo.stage",cur); store("lo.class",cls); render(); }
});

/* keep the sticky rail clear of the sticky site nav */
function measure(){
  var nb=document.querySelector(".sitenav"), rw=document.querySelector(".railwrap");
  var nh=nb?nb.offsetHeight:42;
  document.documentElement.style.setProperty("--navh", nh+"px");
  document.documentElement.style.setProperty("--railh", (nh+(rw?rw.offsetHeight:0)+14)+"px");
}
window.RUNBAR_EXTRA=function(wrap, st){
  if(!st.started) return;
  var k=(VALID[st.stage] ? st.stage : null); if(!k) return;
  var b=document.createElement("button");
  b.type="button"; b.className="go";
  b.textContent="Go to my checkpoint";
  b.title="Jump to "+STAGES[stageIdx(k)][1]+", the checkpoint your boss checklist is on.";
  b.addEventListener("click",function(){ cur=k; setHash(); render(); scrollTop(); });
  wrap.appendChild(b);
};

window.addEventListener("resize", measure);
measure(); render(); setHash();
keepRailInView();
})();
</script>
"""

out = os.path.join(ROOT, "loadouts.html")
open(out, "w", encoding="utf-8").write(HTML + SC.progress_js("loadouts.html") + JS)
print("wrote loadouts.html %.2f MB | %d gear entries | %d checkpoints | %d classes"
      % (os.path.getsize(out)/1048576, n_items, len(STAGES), len(CLASSES)))
