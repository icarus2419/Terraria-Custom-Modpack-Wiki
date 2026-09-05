import json, os, sys, time, urllib.parse, urllib.request

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wiki")
os.makedirs(OUT, exist_ok=True)

def jina(url, tries=3):
    enc = urllib.parse.quote(url, safe='')
    for i in range(tries):
        try:
            req = urllib.request.Request("https://r.jina.ai/" + enc,
                headers={"x-return-format": "text", "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            sys.stderr.write("retry %d %s: %s\n" % (i, url, e))
            time.sleep(4)
    return None

def parse_page(host, page):
    url = ("https://%s/api.php?action=parse&page=%s&prop=text&formatversion=2&format=json"
           % (host, urllib.parse.quote(page, safe='')))
    return jina(url)

if __name__ == "__main__":
    host, page, name = sys.argv[1], sys.argv[2], sys.argv[3]
    txt = parse_page(host, page)
    path = os.path.join(OUT, name + ".json")
    if txt is None:
        print("FAIL", name); sys.exit(1)
    open(path, "w").write(txt)
    try:
        d = json.loads(txt)
        if "error" in d:
            print("ERROR", name, d["error"].get("code"), d["error"].get("info")[:120])
        else:
            html = d["parse"]["text"]
            print("OK", name, "html_bytes=%d" % len(html), "| tables=%d" % html.count("<table"))
    except Exception as e:
        print("BADJSON", name, str(e)[:100], txt[:200])
