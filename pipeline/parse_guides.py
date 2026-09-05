"""Parse each wiki's 'Class setups' guide into (stage, class, category, items).

Three shapes in play:
  vanilla  - div.infocard.guide-class-setups, hgroup carries stage AND class
  thorium  - div.infocard, hgroup carries class only; stage is the section heading
  spirit   - same as thorium
  stars    - wikitables with a Class column; stage is the section heading
"""
import json, os, re, sys
from html.parser import HTMLParser
BASE = os.path.dirname(os.path.abspath(__file__))

CLASSES = ["Melee","Ranged","Magic","Summoner","Summon","Bard","Healer","Thrower","Rogue",
           "Throwing","Mixed","All Classes","Any Class","Radiant","Symphonic"]
def norm_class(s):
    s = re.sub(r"\s+", " ", (s or "")).strip()
    low = s.lower()
    if low.startswith("summon"): return "Summoner"
    if low.startswith("throw"):  return "Thrower"
    if low in ("radiant",):      return "Healer"
    if low in ("symphonic",):    return "Bard"
    for c in CLASSES:
        if low == c.lower(): return c
    return s

class GuideParser(HTMLParser):
    """Depth-tracked: nested divs must not close an outer hgroup/title/box."""
    def __init__(self, host, stage_from_heading):
        super().__init__(convert_charrefs=True)
        self.host = host
        self.stage_from_heading = stage_from_heading
        self.cards = []
        self.heading = None
        self.in_head = 0; self.head_txt = ""
        self.depth = 0                  # absolute div depth
        self.card = None; self.card_d = None
        self.hg_d = None; self.hg_parts = []; self.hg_cur = ""; self.hg_main = None
        self.main_d = None
        self.title_d = None; self.title_txt = ""
        self.boxes = []                 # stack of (depth, title)
        self.in_sup = 0
        self.a = None; self.a_txt = ""; self.img = None

    def abs_(self, s):
        if not s: return None
        if s.startswith("//"): return "https:" + s
        if s.startswith("http"): return s
        return "https://%s%s" % (self.host, s)

    def cur_box(self):
        """Outermost named box is the category; innermost is the qualifier."""
        named = [t for _, t in self.boxes if t]
        if not named: return None, None
        return named[0], (named[-1] if len(named) > 1 else None)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs); cls = a.get("class", "") or ""; k = cls.split()
        if tag in ("h2", "h3"):
            self.in_head = 1; self.head_txt = ""; return
        if tag == "div":
            self.depth += 1
            if "infocard" in k and self.card is None:
                self.card = {"stage": None, "cls": None, "boxes": []}
                self.card_d = self.depth
                self.hg_d = self.title_d = self.main_d = None
                self.hg_parts = []; self.hg_cur = ""; self.hg_main = None; self.boxes = []
                return
            if self.card is None: return
            if "hgroup" in k and self.hg_d is None:
                self.hg_d = self.depth; self.hg_parts = []; self.hg_cur = ""
            elif self.hg_d is not None and "main" in k and self.main_d is None:
                self.main_d = self.depth
                if self.hg_cur.strip(): self.hg_parts.append(self.hg_cur.strip()); self.hg_cur = ""
            elif "title" in k and self.title_d is None:
                self.title_d = self.depth; self.title_txt = ""
            elif "box" in k:
                self.boxes.append([self.depth, None])
            return
        if self.card is None: return
        if tag == "sup": self.in_sup += 1
        elif tag == "img":
            if not self.in_sup and not self.img: self.img = self.abs_(a.get("src"))
        elif tag == "a":
            self.a = a.get("href", ""); self.a_txt = ""

    def handle_endtag(self, tag):
        if tag in ("h2", "h3") and self.in_head:
            self.in_head = 0
            t = re.sub(r"\[\s*edit\s*\]", "", self.head_txt).strip()
            if t: self.heading = t
            return
        if self.card is None:
            if tag == "div": self.depth = max(0, self.depth - 1)
            return
        if tag == "sup": self.in_sup = max(0, self.in_sup - 1); return
        if tag == "a":
            txt = re.sub(r"\s+", " ", (self.a_txt or "")).strip()
            bad = (not txt or self.in_sup or self.title_d is not None or self.hg_d is not None
                   or re.match(r"(File|Image|Media):", txt) or "action=edit" in (self.a or "")
                   or re.fullmatch(r"\[[^\]]{0,4}\]", txt)
                   or "#cite" in (self.a or "") or "cite_note" in (self.a or ""))
            if not bad:
                cat, qual = self.cur_box()
                if cat:
                    box = None
                    for b in self.card["boxes"]:
                        if b["title"] == cat: box = b; break
                    if box is None:
                        box = {"title": cat, "items": []}; self.card["boxes"].append(box)
                    if not any(x["name"] == txt for x in box["items"]):
                        box["items"].append({"name": txt, "img": self.img,
                                             "url": self.abs_(self.a), "note": qual})
            self.a = None; self.a_txt = ""
            if txt and not bad: self.img = None      # consumed; otherwise keep for the name anchor
            return
        if tag == "div":
            d = self.depth
            if self.main_d == d:
                self.main_d = None
                if self.hg_cur.strip():
                    self.hg_main = self.hg_cur.strip(); self.hg_parts.append(self.hg_main)
                self.hg_cur = ""
            elif self.hg_d == d:
                if self.hg_cur.strip(): self.hg_parts.append(self.hg_cur.strip())
                self.hg_cur = ""; self.hg_d = None
                parts = [p for p in self.hg_parts if p]
                self.card["cls"] = norm_class(self.hg_main or (parts[-1] if parts else None))
                others = [p for p in parts if p != (self.hg_main or "")]
                self.card["stage"] = (others[0] if (others and not self.stage_from_heading)
                                      else self.heading)
            elif self.title_d == d:
                self.title_d = None
                t = re.sub(r"\s+", " ", self.title_txt).strip()
                if self.boxes and t: self.boxes[-1][1] = t
            while self.boxes and self.boxes[-1][0] >= d: self.boxes.pop()
            if self.card_d == d:
                if any(b["items"] for b in self.card["boxes"]):
                    if not self.card.get("stage"): self.card["stage"] = self.heading
                    self.cards.append(self.card)
                self.card = None; self.card_d = None; self.boxes = []
            self.depth = max(0, self.depth - 1)

    def handle_data(self, d):
        if self.in_head: self.head_txt += d; return
        if self.card is None: return
        # a box title or class name may itself be a link ("Armor" links to the armor
        # progression guide) - the label wins over the anchor in those positions
        if self.title_d is not None: self.title_txt += d
        elif self.hg_d is not None: self.hg_cur += d
        elif self.a is not None: self.a_txt += d


# ---------- stars: table shape ----------
class StarsParser(HTMLParser):
    def __init__(self, host):
        super().__init__(convert_charrefs=True)
        self.host = host; self.rows = []
        self.heading = None; self.in_head = 0; self.head_txt = ""
        self.headers = []; self.in_table = 0; self.in_th = 0; self.th_txt = ""
        self.in_td = 0; self.col = -1; self.cells = None; self.td_txt = ""
        self.a = None; self.a_txt = ""; self.img = None; self.in_sup = 0

    def abs_(self, s):
        if not s: return None
        if s.startswith("//"): return "https:" + s
        if s.startswith("http"): return s
        return "https://%s%s" % (self.host, s)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs); cls = a.get("class","") or ""
        if tag in ("h2","h3"): self.in_head = 1; self.head_txt = ""; return
        if tag == "table": self.in_table += 1; self.headers = []; return
        if not self.in_table: return
        if tag == "tr": self.cells = []; self.col = -1
        elif tag == "th": self.in_th = 1; self.th_txt = ""
        elif tag == "td":
            self.in_td = 1; self.col += 1; self.td_txt = ""
            if self.cells is not None: self.cells.append({"text":"", "items":[]})
        elif tag == "img":
            if self.in_td and not self.in_sup and not self.img: self.img = self.abs_(a.get("src"))
        elif tag == "a":
            self.a = a.get("href",""); self.a_txt = ""

    def handle_endtag(self, tag):
        if tag in ("h2","h3") and self.in_head:
            self.in_head = 0
            t = re.sub(r"\[\s*edit\s*\]","",self.head_txt).strip()
            if t: self.heading = t
            return
        if not self.in_table: return
        if tag == "th" and self.in_th:
            self.in_th = 0; self.headers.append(re.sub(r"\s+"," ",self.th_txt).strip())
        elif tag == "a" and self.in_td:
            txt = re.sub(r"\s+"," ",(self.a_txt or "")).strip()
            if txt and not self.in_sup and "action=edit" not in (self.a or "") \
               and not re.match(r"(File|Image):", txt) \
               and not re.fullmatch(r"\[[^\]]{0,4}\]", txt) \
               and "#cite" not in (self.a or "") and self.cells:
                self.cells[self.col]["items"].append(
                    {"name": txt, "img": self.img, "url": self.abs_(self.a)})
                self.img = None
            self.a = None; self.a_txt = ""
        elif tag == "td" and self.in_td:
            self.in_td = 0
            if self.cells: self.cells[self.col]["text"] = re.sub(r"\s+"," ",self.td_txt).strip()
        elif tag == "tr":
            if self.cells and len(self.cells) >= 2:
                self.rows.append({"stage": self.heading, "headers": list(self.headers),
                                  "cells": self.cells})
            self.cells = None
        elif tag == "table":
            self.in_table = max(0, self.in_table - 1)

    def handle_data(self, d):
        if self.in_head: self.head_txt += d; return
        if self.in_th: self.th_txt += d
        elif self.a is not None: self.a_txt += d
        elif self.in_td: self.td_txt += d

SRC = [("vanilla","terraria.wiki.gg",False),
       ("thorium","thoriummod.wiki.gg",True),
       ("spirit","spiritmod.wiki.gg",True)]

def parse_all():
    out = {}
    for mod, host, from_head in SRC:
        h = json.load(open(os.path.join(BASE,"guides",mod+".json")))["parse"]["text"]
        p = GuideParser(host, from_head); p.feed(h)
        out[mod] = p.cards
    h = json.load(open(os.path.join(BASE,"guides","stars.json")))["parse"]["text"]
    sp = StarsParser("starsabovemod.wiki.gg"); sp.feed(h)
    cards = []
    for r in sp.rows:
        cl = norm_class(r["cells"][0]["text"])
        if not cl or cl.lower() in ("class",): continue
        boxes = []
        for i, c in enumerate(r["cells"][1:], start=1):
            title = r["headers"][i] if i < len(r["headers"]) else "Gear"
            if c["items"]: boxes.append({"title": title, "items": c["items"]})
        if boxes: cards.append({"stage": r["stage"], "cls": cl, "boxes": boxes})
    out["stars"] = cards
    return out

if __name__ == "__main__":
    allc = parse_all()
    for mod, cards in allc.items():
        stages, classes = [], []
        for c in cards:
            if c["stage"] and c["stage"] not in stages: stages.append(c["stage"])
            if c["cls"] and c["cls"] not in classes: classes.append(c["cls"])
        items = sum(len(b["items"]) for c in cards for b in c["boxes"])
        cats = {}
        for c in cards:
            for b in c["boxes"]: cats[b["title"]] = cats.get(b["title"],0)+1
        print("%-8s cards=%-4d items=%-5d" % (mod, len(cards), items))
        print("     classes:", classes)
        print("     stages :", stages[:12])
        print("     boxes  :", sorted(cats, key=lambda x:-cats[x])[:10])
    json.dump(allc, open(os.path.join(BASE,"guides_parsed.json"),"w"))
