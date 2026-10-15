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
TYPE_OF = {"poissy": "depannage", "les-mureaux": "depannage", "conflans-sainte-honorine": "entretien", "la-celle-saint-cloud": "entretien", "yvelines-78": "hub"}
for t in TOWNS:
    t.setdefault("town", t["slug"])
    t.setdefault("type", TYPE_OF.get(t["slug"], "installation"))
    if t["slug"] == "yvelines-78": t["file"] = "climatisation-yvelines-78.html"
BY = {t["slug"]: t for t in TOWNS}
assert len(BY) == len(TOWNS), "slug en double"

gen2.PAGEFILES = {gen2.fname(t) for t in TOWNS}
gen2.RENAMED = {f"installation-climatisation-{t['town']}.html": gen2.fname(t) for t in TOWNS if t["type"] in ("depannage", "entretien")}

# --- page départementale : liens vers chaque ville
hub = BY["yvelines-78"]
_order = ["installation", "depannage", "entretien", "urgence"]
town_links = [(gen2.fname(t), maillage.anchor_of(t)) for t in sorted((x for x in TOWNS if x["slug"] != "yvelines-78"), key=lambda x: (maillage.RING.index(x["town"]), _order.index(x["type"])))]
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
    return n.endswith(base) and n.split(" ")[0] in ("climatisation", "installation", "depannage", "entretien", "devis", "pose", "nettoyage", "reparation", "urgence")
errs = []
for t in TOWNS:
    for k in t["kw"]:
        if not norm_kw_ok(t, k): errs.append((t["slug"], "mot-clé hors relevé", k))
    for h, _ in t["near"]:
        if h.startswith("../"): continue
        h = gen2.resolve(h)
        if h not in {gen2.fname(x) for x in TOWNS} and not os.path.exists(os.path.join(gen2.REPO, "zones", h)):
            errs.append((t["slug"], "lien cassé", h))
if errs:
    for x in errs: print("ERREUR", x)
    sys.exit(1)

def publish():
    R = gen2.REPO
    # pages représentant chaque ville (liens de pied de page, zones.html)
    order = ["installation", "depannage", "entretien", "urgence"]
    rep = {}
    for t in sorted((x for x in TOWNS if x["slug"] != "yvelines-78"), key=lambda x: order.index(x["type"])):
        rep.setdefault(t["town"], t)
    reps = [rep[s_] for s_ in maillage.RING if s_ in rep]

    # fichiers périmés (page renommée ou supprimée)
    sm_path = os.path.join(R, "sitemap.xml")
    sm = open(sm_path, encoding="utf-8").read()
    for f in glob.glob(os.path.join(R, "zones", "*.html")):
        b = os.path.basename(f)
        if re.match(r"^(installation|depannage|entretien|urgence)-climatisation-", b) and "paris" not in b and b not in gen2.PAGEFILES:
            os.remove(f); print("supprimé (renommé)", b)
            sm = re.sub(r"[ \t]*<url><loc>https://lexvdufroid\.fr/zones/" + re.escape(b) + r"</loc>.*?</url>\n", "", sm)

    gen2.write_all(TOWNS)

    today = datetime.date.today().isoformat()
    add = ""
    for t in TOWNS:
        loc = f"https://lexvdufroid.fr/zones/{gen2.fname(t)}"
        if loc not in sm:
            add += f'  <url><loc>{loc}</loc><lastmod>{t.get("date", today)}</lastmod></url>\n'
    if add: sm = sm.replace("</urlset>", add + "</urlset>", 1)
    open(sm_path, "w", encoding="utf-8").write(sm)

    zp = os.path.join(R, "zones.html")
    z = open(zp, encoding="utf-8").read()
    items = ",\n".join(f'                  <a href="zones/{gen2.fname(t)}">{t["name"]}</a>' for t in reps) + "."
    z2 = re.sub(r'(<p class="zones-inline-links">\s*Pages locales :\s*\n)(\s*<a href="zones/(?:installation|depannage|entretien|urgence)-climatisation-versailles\.html">.*?)(\n\s*</p>)',
                lambda m: m.group(1) + items + m.group(3), z, count=1, flags=re.S)
    if z2 != z: open(zp, "w", encoding="utf-8").write(z2)

    # Pied de page sobre : un seul lien vers le hub Yvelines (les villes restent listées dans zones.html et le hub)
    towns = [("climatisation-yvelines-78.html", "Toutes nos zones d’intervention dans les Yvelines (78)")]
    n = 0
    for f in glob.glob(R + "/*.html") + glob.glob(R + "/articles/*.html") + glob.glob(R + "/zones/*.html"):
        t_ = open(f, encoding="utf-8").read()
        if 'class="footer-yvelines"' not in t_: continue
        rel = os.path.relpath(f, R)
        pre = "" if rel.startswith("zones/") else ("../zones/" if rel.startswith("articles/") else "zones/")
        lis = "".join(f'<a href="{pre}{h}">{l}</a>' for h, l in towns)
        t2 = re.sub(r'(<nav class="footer-yvelines"[^>]*><h3>[^<]*</h3><p>).*?(</p></nav>)', lambda m: m.group(1) + lis + m.group(2), t_, flags=re.S)
        if t2 != t_: open(f, "w", encoding="utf-8").write(t2); n += 1
    print("pieds de page mis à jour :", n)

if __name__ == "__main__":
    publish()
