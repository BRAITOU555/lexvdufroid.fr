# -*- coding: utf-8 -*-
"""Contrôles qualité. Usage : python3 -I scripts/seo78/check.py   (code retour 1 si échec)"""
import sys, os, re, html, json, glob, itertools, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build, gen2
R = gen2.REPO
MAX_SIM = 0.06
BANNED = ["il est important de noter", "n’hésitez pas", "n'hésitez pas", "dans le monde d", "incontournable", "véritable", "plongez", "découvrez", "en conclusion", "ainsi,", "fort de", "sur mesure", "clé en main", "à la pointe"]
def norm(s):
    s = s.replace("²", "2").replace("’", "'")
    s = unicodedata.normalize("NFD", s.lower()); s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"(\d) m ?2", r"\1m2", s)
fails = []
W = {}
for t in build.TOWNS:
    f = os.path.join(R, "zones", gen2.fname(t)); s = open(f, encoding="utf-8").read()
    main = re.sub(r"<script.*?</script>", "", re.search(r"<main.*?</main>", s, re.S).group(0), flags=re.S)
    main_nolinks = re.sub(r'<section class="local-soft-panel local-text-panel">(?:(?!</section>).)*?<ul class="local-text-list"><li><a.*?</section>', "", main, flags=re.S)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", main))
    W[t["slug"]] = re.findall(r"\w+", html.unescape(re.sub(r"<[^>]+>", " ", main_nolinks)).lower())
    n = " " + norm(txt + " " + t["title"] + " " + t["meta"]) + " "
    for k in t["kw"]:
        if " " + norm(k).strip() + " " not in n: fails.append((t["slug"], "mot-clé absent du texte", k))
    if re.search(r"\d\s?€|€|euros?\b", s): fails.append((t["slug"], "prix / euros dans la page", ""))
    for b in BANNED:
        if b in txt.lower(): fails.append((t["slug"], "formule IA", b))
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try: json.loads(blk)
        except Exception as e: fails.append((t["slug"], "JSON-LD invalide", str(e)))
    for h in re.findall(r'(?:href|src)="([^"#?]+)"', s):
        if h.startswith(("http", "mailto", "tel", "/", "data:")): continue
        if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(f), h))): fails.append((t["slug"], "lien/image cassé", h))
    if not re.search(r'<h1[^>]*>', s) or len(t["title"]) > 95: fails.append((t["slug"], "titre trop long (>95) ou H1 absent", str(len(t["title"]))))
G = {k: {tuple(w[i:i+4]) for i in range(len(w) - 3)} for k, w in W.items()}
# Les formules communes à beaucoup de pages (téléphone, « devis clair avant travaux »…) sont du gabarit de site,
# pas du contenu : on les écarte avant de mesurer la ressemblance entre deux pages.
_df = {}
for _g in G.values():
    for _x in _g: _df[_x] = _df.get(_x, 0) + 1
G = {k: {x for x in g if _df[x] < 8} for k, g in G.items()}
worst = (0, "", "")
for a, b in itertools.combinations(G, 2):
    j = len(G[a] & G[b]) / max(1, len(G[a] | G[b]))
    if j > worst[0]: worst = (j, a, b)
    if j > MAX_SIM: fails.append((a + " / " + b, "similarité trop forte", f"{j:.1%}"))
used = [k for t in build.TOWNS for k in t["kw"]]
for k in {k for k in used if used.count(k) > 1}: fails.append(("mots-clés", "mot-clé utilisé sur deux pages", k))
import xml.etree.ElementTree as ET
ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
urls = {x.text for x in ET.parse(os.path.join(R, "sitemap.xml")).getroot().findall(".//s:loc", ns)}
for t in build.TOWNS:
    if "https://lexvdufroid.fr/zones/" + gen2.fname(t) not in urls: fails.append((t["slug"], "absent du sitemap", ""))
print(f"{len(build.TOWNS)} pages, similarité max {worst[0]:.1%} ({worst[1]} / {worst[2]})")
for x in fails: print("ÉCHEC", x)
sys.exit(1 if fails else 0)
