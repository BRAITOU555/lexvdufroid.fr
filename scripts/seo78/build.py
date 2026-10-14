# -*- coding: utf-8 -*-
"""Génère toutes les pages Yvelines (78) + maillage, sitemap, zones.html, pieds de page.
Usage : python3 -I scripts/seo78/build.py      (depuis la racine du dépôt)
Les pages vivent dans scripts/seo78/pages/*.py (une liste de dicts par fichier)."""
import sys, os, re, glob, importlib.util, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen2, maillage, patch
from kp_data import KNOWN

def load_pages():
    out = []
    for f in sorted(glob.glob(os.path.join(HERE, "pages", "*.py")), key=lambda p: (len(os.path.basename(p)), p)):
        spec = importlib.util.spec_from_file_location(os.path.basename(f)[:-3], f)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        for k, v in vars(m).items():
            if k.isupper() and isinstance(v, list) and v and isinstance(v[0], dict) and "slug" in v[0]:
                out += v
    return out

TOWNS = load_pages()
BY = {t["slug"]: t for t in TOWNS}
assert len(BY) == len(TOWNS), "slug en double"

# --- page départementale : liens vers chaque ville
hub = BY["yvelines-78"]
town_links = [(gen2.fname(t), "Climatisation " + t["name"]) for t in TOWNS if t["slug"] != "yvelines-78"]
hub["blocks"].insert(1, ("links", "Pages locales", "Une page par ville", "Chaque page parle de sa commune et de ses habitudes de pose.", town_links))

# --- un mot clé = une seule page
KW = {
 "poissy": ["climatisation poissy", "dépannage climatisation", "reparation climatisation", "réparation climatiseur"],
 "les-mureaux": ["climatisation les mureaux", "réparation climatiseur mural", "réparation air climatisé mural", "réparation air climatisé"],
 "velizy-villacoublay": ["entreprise de climatisation", "entreprise climatisation", "installateur de climatisation", "air climatisé central", "climatiseur central"],
 "elancourt": ["climatisation elancourt", "prix d une clim pour 100m2", "prix clim réversible pour 100m2", "pompe a chaleur gainable", "cout installation climatisation"],
 "le-vesinet": ["climatisation le vesinet", "devis climatisation maison", "mise en service climatisation", "pose de climatisation"],
 "sartrouville": ["installation climatisation sartrouville", "installer une climatisation", "installer climatisation maison", "pompe de relevage clim", "installation clim"],
 "rambouillet": ["climatisation rambouillet", "clim reversible chauffage", "climatiseur reversible", "climatisation réversible", "clim reversible"],
 "marly-le-roi": ["clim reversible air air", "installer clim reversible", "installation clim reversible", "pompe à chaleur clim réversible prix"],
 "maisons-laffitte": ["climatisation maisons laffitte", "climatiseur monobloc réversible", "clim monobloc reversible", "clim reversible mobile", "climatiseur appartement"],
}
for slug, kws in KW.items():
    if slug in BY: BY[slug]["kw"] = kws

ORDER = {
 "poissy": ["text", "photo", "list", "editorial"],
 "plaisir": ["editorial", "photo", "text", "list"],
 "guyancourt": ["photo", "list", "text", "editorial"],
 "velizy-villacoublay": ["list", "photo", "text", "editorial"],
 "chatou": ["photo", "editorial", "text", "list"],
 "elancourt": ["editorial", "list", "price", "photo"],
}
for slug, kinds in ORDER.items():
    if slug not in BY: continue
    t = BY[slug]
    body = {b[0]: b for b in t["blocks"] if b[0] not in ("faq", "zone", "links")}
    tail = [b for b in t["blocks"] if b[0] in ("faq", "zone")]
    if set(body) == set(kinds):
        t["blocks"] = [body[k] for k in kinds] + tail

for slug, h in {"montigny-le-bretonneux": "Autour de Saint-Quentin-en-Yvelines", "houilles": "Les communes de la boucle",
                "guyancourt": "Les villes à côté", "elancourt": "Pour comparer avec les villes voisines"}.items():
    if slug in BY: BY[slug]["next_h2"] = h

patch.apply(BY)
maillage.apply(TOWNS)

# --- contrôles de base
def norm_kw_ok(t, k):
    if k in KNOWN: return True
    n = k.lower().replace("-", " ")
    base = t["name"].lower().replace("-", " ").replace("’", " ").replace("'", " ")
    base = re.sub(r"[éèê]", "e", re.sub(r"[ô]", "o", base))
    return n.endswith(base) and n.split(" ")[0] in ("climatisation", "installation", "depannage", "entretien", "devis", "pose", "nettoyage")
errs = []
for t in TOWNS:
    for k in t["kw"]:
        if not norm_kw_ok(t, k): errs.append((t["slug"], "mot-clé hors relevé", k))
    for h, _ in t["near"]:
        if h.startswith("../"): continue
        if h not in {gen2.fname(x) for x in TOWNS} and not os.path.exists(os.path.join(gen2.REPO, "zones", h)):
            errs.append((t["slug"], "lien cassé", h))
if errs:
    for x in errs: print("ERREUR", x)
    sys.exit(1)

def publish():
    # --- écriture des pages
    gen2.write_all(TOWNS)

    # --- sitemap
    R = gen2.REPO
    sm = open(os.path.join(R, "sitemap.xml"), encoding="utf-8").read()
    today = datetime.date.today().isoformat()
    add = ""
    for t in TOWNS:
        loc = f"https://lexvdufroid.fr/zones/{gen2.fname(t)}"
        if loc not in sm:
            add += f'  <url><loc>{loc}</loc><lastmod>{t.get("date", today)}</lastmod></url>\n'
    if add:
        sm = sm.replace("</urlset>", add + "</urlset>", 1)
        open(os.path.join(R, "sitemap.xml"), "w", encoding="utf-8").write(sm)

    # --- zones.html : liste des villes du 78
    zp = os.path.join(R, "zones.html")
    z = open(zp, encoding="utf-8").read()
    items = ",\n".join(f'                  <a href="zones/{gen2.fname(t)}">{t["name"]}</a>' for t in TOWNS if t["slug"] != "yvelines-78") + "."
    z2 = re.sub(r'(<p class="zones-inline-links">\s*Pages locales :\s*\n)(\s*<a href="zones/installation-climatisation-versailles\.html">.*?)(\n\s*</p>)',
                lambda m: m.group(1) + items + m.group(3), z, count=1, flags=re.S)
    if z2 != z: open(zp, "w", encoding="utf-8").write(z2)

    # --- pieds de page "Yvelines" sur tout le site
    towns = [("climatisation-yvelines-78.html", "Climatisation Yvelines (78)")] + \
            [(gen2.fname(t), maillage.ANCH[t["slug"]].split(" : ")[0]) for t in sorted((x for x in TOWNS if x["slug"] != "yvelines-78"), key=lambda x: maillage.RING.index(x["slug"]))]
    n = 0
    for f in glob.glob(R + "/*.html") + glob.glob(R + "/articles/*.html") + glob.glob(R + "/zones/*.html"):
        t = open(f, encoding="utf-8").read()
        if 'class="footer-yvelines"' not in t: continue
        rel = os.path.relpath(f, R)
        pre = "" if rel.startswith("zones/") else ("../zones/" if rel.startswith("articles/") else "zones/")
        lis = "".join(f'<a href="{pre}{h}">{l}</a>' for h, l in towns)
        t2 = re.sub(r'(<nav class="footer-yvelines"[^>]*><h3>[^<]*</h3><p>).*?(</p></nav>)', lambda m: m.group(1) + lis + m.group(2), t, flags=re.S)
        if t2 != t: open(f, "w", encoding="utf-8").write(t2); n += 1
    print("pieds de page mis à jour :", n)


if __name__ == "__main__":
    publish()
