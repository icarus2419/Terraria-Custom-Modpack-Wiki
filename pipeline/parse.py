import json, os, re, sys
from html.parser import HTMLParser

BASE = os.path.dirname(os.path.abspath(__file__))
ITEM_CLASSES = ("i", "item-link")

def is_item_span(cls):
    if not cls: return False
    parts = cls.split()
    return any(p in ITEM_CLASSES for p in parts)

class CraftsParser(HTMLParser):
    """Parse wiki.gg 'crafts' tables, honouring result-cell rowspan continuation."""
    def __init__(self, host):
        super().__init__(convert_charrefs=True)
        self.host = host
        self.rows = []
        # table gating
        self.in_crafts = 0
        self.table_depth = 0
        # row state
        self.cellkind = None
        self.pending_result = None      # (item, rows_remaining)
        self.row_result = None
        self.row_ings = None
        # cell parse state
        self.stack = []                 # span kinds
        self.cur_item = None
        self.last_item = None
        self.cur_group = None
        self.a_text = None
        self.in_eico = 0
        self.eico_note = None
        self.cur_img = None

    # ---------- helpers ----------
    def absurl(self, src):
        if not src: return None
        if src.startswith("//"): return "https:" + src
        if src.startswith("http"): return src
        return "https://%s%s" % (self.host, src)

    def pageurl(self, href):
        if not href: return None
        if href.startswith("http"): return href
        return "https://%s%s" % (self.host, href)

    def flush_item(self):
        if self.cur_item and self.cur_item.get("name"):
            if self.cur_group is not None:
                self.cur_group.append(self.cur_item)
                self.last_item = self.cur_item
        self.cur_item = None

    # ---------- tags ----------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "")
        if tag == "table":
            self.table_depth += 1
            if "crafts" in cls or self.in_crafts:
                pass
        elif tag == "div" and "crafts" in cls.split():
            self.in_crafts += 1
        elif tag == "tr":
            self.row_result = None
            self.row_ings = None
        elif tag in ("td", "th"):
            k = cls.split()
            if "result" in k: self.cellkind = "result"
            elif "ingredients" in k: self.cellkind = "ingredients"
            else: self.cellkind = None
            if self.cellkind == "result":
                self.row_result = {"span": int(a.get("rowspan", "1") or 1), "items": []}
                self.cur_group = self.row_result["items"]
            elif self.cellkind == "ingredients":
                self.row_ings = []          # list of groups (one per <li>)
                self.cur_group = None
            else:
                self.cur_group = None
        elif tag == "li" and self.cellkind == "ingredients":
            self.flush_item()
            self.last_item = None
            self.cur_group = []
            self.row_ings.append(self.cur_group)
        elif tag == "span":
            if "eico" in cls.split():
                self.in_eico += 1
                self.eico_note = a.get("title") or None
                if self.cur_item is not None and self.eico_note:
                    self.cur_item["note"] = self.eico_note
            elif "am" in cls.split() or "note-text" in cls.split():
                self.stack.append("am")
            elif is_item_span(cls):
                self.flush_item()
                self.cur_item = {"name": None, "img": None, "url": None, "qty": 1}
                self.stack.append("item")
            else:
                self.stack.append("span")
        elif tag == "img":
            if self.cur_item is not None and not self.cur_item["img"] and not self.in_eico:
                self.cur_item["img"] = self.absurl(a.get("src"))
        elif tag == "a":
            if self.in_eico: return
            self.a_text = ""
            self.a_href = a.get("href", "")
            self.a_title = a.get("title", "")

    def handle_endtag(self, tag):
        if tag == "table":
            self.table_depth -= 1
        elif tag == "div":
            if self.in_crafts: self.in_crafts = max(0, self.in_crafts - 1)
        elif tag == "span":
            if self.in_eico:
                self.in_eico -= 1
            elif self.stack:
                self.stack.pop()
        elif tag == "a":
            if self.in_eico: return
            txt = (self.a_text or "").strip()
            # a missing sprite renders as a redlink to File:/Special:Upload whose link text is
            # the filename - that is not the item's name, so let the real name anchor win
            isfile = bool(re.search(r"/wiki/(File|Image|Media):|Special:Upload", self.a_href or "")) \
                     or bool(re.match(r"(File|Image|Media):", self.a_title or "")) \
                     or bool(re.match(r"(File|Image|Media):", txt))
            if txt and not isfile and self.cur_item is not None and not self.cur_item["name"]:
                self.cur_item["name"] = txt
                self.cur_item["url"] = self.pageurl(self.a_href)
            self.a_text = None
        elif tag in ("td", "th"):
            self.flush_item()
            self.cellkind = None
            self.cur_group = None
        elif tag == "tr":
            self.flush_item()
            self.close_row()

    def handle_data(self, d):
        if self.in_eico: return
        if self.a_text is not None:
            self.a_text += d
            return
        s = d.strip()
        if not s: return
        if self.stack and self.stack[-1] == "am":
            m = re.fullmatch(r"\(?\s*([\d,]+)\s*\)?", s)
            tgt = self.cur_item if self.cur_item is not None else self.last_item
            if m and tgt is not None:
                tgt["qty"] = int(m.group(1).replace(",", ""))

    # ---------- rows ----------
    def close_row(self):
        if self.row_ings is None:
            return
        if self.row_result and self.row_result["items"]:
            self.pending_result = [self.row_result["items"][0], self.row_result["span"]]
        if not self.pending_result:
            return
        res, remaining = self.pending_result
        groups = [g for g in self.row_ings if g]
        if groups:
            self.rows.append((res, groups))
        remaining -= 1
        self.pending_result = [res, remaining] if remaining > 0 else None

def parse(name, host):
    d = json.load(open(os.path.join(BASE, "wiki", name + ".json")))
    p = CraftsParser(host)
    p.feed(d["parse"]["text"])
    out = []
    for res, groups in p.rows:
        ings = []
        for g in groups:
            ings.append([{"name": it["name"], "img": it["img"], "url": it["url"],
                          "qty": it.get("qty", 1), "note": it.get("note")} for it in g])
        out.append({"result": res["name"], "result_img": res["img"],
                    "result_url": res["url"], "result_qty": res.get("qty", 1),
                    "result_note": res.get("note"), "ingredients": ings})
    return out

SOURCES = [
    ("vanilla", "terraria.wiki.gg"),
    ("thorium", "thoriummod.wiki.gg"),
    ("fargo",   "fargosmods.wiki.gg"),
    ("spirit",  "spiritmod.wiki.gg"),
    ("fables",  "calamityfables.wiki.gg"),
]

def fmt(r):
    parts = []
    for g in r["ingredients"]:
        alt = " or ".join("%s%s" % (i["name"], " (%d)" % i["qty"] if i["qty"] > 1 else "") for i in g)
        parts.append(alt)
    return "%s = %s" % (r["result"], " + ".join(parts))

if __name__ == "__main__":
    allo = {}
    for name, host in SOURCES:
        rs = parse(name, host)
        allo[name] = rs
        print("%-8s %4d recipes" % (name, len(rs)))
    json.dump(allo, open(os.path.join(BASE, "recipes_raw.json"), "w"), indent=1)
    print()
    for r in allo["vanilla"]:
        if r["result"] in ("Cell Phone", "Avenger Emblem", "Spectre Boots",
                           "The Grand Design", "Lava Waders", "Terraspark Boots",
                           "Cyan Weighted Pressure Plate"):
            print("  ", fmt(r))
