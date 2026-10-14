# -*- coding: utf-8 -*-
import gen2
RING = ["mantes-la-jolie","limay","les-mureaux","poissy","conflans-sainte-honorine","maisons-laffitte","sartrouville","houilles","montesson","chatou","le-vesinet","saint-germain-en-laye","marly-le-roi","la-celle-saint-cloud","le-chesnay-rocquencourt","versailles","viroflay","velizy-villacoublay","guyancourt","montigny-le-bretonneux","elancourt","trappes","plaisir","rambouillet"]
ANCH = {
 "versailles":"Installation climatisation Versailles : appartement ancien et maison",
 "saint-germain-en-laye":"Climatisation Saint-Germain-en-Laye : clim réversible, tarif et pose",
 "poissy":"Climatisation Poissy : dépannage et réparation climatiseur",
 "mantes-la-jolie":"Climatisation Mantes-la-Jolie : devis pose climatisation",
 "rambouillet":"Climatisation Rambouillet : climatiseur réversible pour chauffer",
 "le-chesnay-rocquencourt":"Climatisation Le Chesnay : climatiseur mural avec installation",
 "sartrouville":"Installation climatisation Sartrouville : installer une climatisation en maison",
 "conflans-sainte-honorine":"Climatisation Conflans-Sainte-Honorine : entretien et nettoyage",
 "velizy-villacoublay":"Entreprise de climatisation Vélizy-Villacoublay : bureaux et locaux pro",
 "montigny-le-bretonneux":"Installation et dépannage climatisation Montigny-le-Bretonneux",
 "maisons-laffitte":"Climatisation Maisons-Laffitte : climatiseur monobloc réversible",
 "le-vesinet":"Climatisation Le Vésinet : devis maison et mise en service",
 "houilles":"Climatisation Houilles : pose de clim réversible",
 "les-mureaux":"Climatisation Les Mureaux : réparation de climatiseur mural",
 "plaisir":"Climatisation Plaisir : installateur Daikin",
 "chatou":"Climatisation Chatou : clim réversible Mitsubishi",
 "marly-le-roi":"Clim réversible air-air Marly-le-Roi : maison sur coteau",
 "guyancourt":"Climatisation Guyancourt : clim prête à poser ou installateur",
 "elancourt":"Climatisation Élancourt : clim pour une maison de 100 m²",

 "trappes":"Climatisation Trappes : clim sans évacuation et appartement",
 "la-celle-saint-cloud":"Nettoyage climatisation La Celle-Saint-Cloud : maison et entretien",
 "viroflay":"Poseur de climatisation Viroflay : installation climatisation",
 "montesson":"Climatisation Montesson : thermopompe murale et devis clim réversible",
 "limay":"Climatiseur réversible Limay : bruit, voisinage et prix",
}
SERV = [("../depannage.html","Dépannage climatisation en Île-de-France"),
        ("../climatisation.html","Installation de climatisation : split, gainable, monobloc"),
        ("../entretien.html","Entretien de climatisation et de clim réversible"),
        ("../contact.html","Demander un devis climatisation gratuit"),
        ("../zones.html","Toutes nos zones d’intervention")]
ART = [("../articles/choisir-puissance-climatisation.html","Quelle puissance de climatisation choisir ?"),
       ("../articles/fuite-eau-climatisation.html","Fuite d’eau d’un climatiseur : causes et solutions"),
       ("../articles/climatisation-ne-refroidit-plus.html","Ma climatisation ne refroidit plus : que faire ?"),
       ("../articles/entretien-climatisation-obligatoire.html","L’entretien de la climatisation est-il obligatoire ?"),
       ("../articles/climatisation-appartement-paris.html","Climatisation en appartement : règles et solutions")]
try:
    import maillage_extra
    for _slug, _after, _anchor in maillage_extra.EXTRA:
        if _slug not in RING:
            RING.insert(RING.index(_after) + 1, _slug)
        ANCH[_slug] = _anchor
except ImportError:
    pass

TYPES = ["installation", "depannage", "entretien", "urgence"]
TYPE_LABEL = {"installation": "Installation", "depannage": "Dépannage", "entretien": "Entretien", "urgence": "Urgence"}

def anchor_of(t):
    return t.get("anchor") or ANCH[t["slug"]]

def apply(TOWNS):
    N = len(RING)
    idx = {s: i for i, s in enumerate(RING)}
    dist = lambda a, b: min((idx[a] - idx[b]) % N, (idx[b] - idx[a]) % N)
    pages = [t for t in TOWNS if t["slug"] != "yvelines-78"]
    for k, t in enumerate(TOWNS):
        if t["slug"] == "yvelines-78":
            add = [("links", "Nos services", "Aller plus loin sur la climatisation",
                    "Les pages du site qui complètent celle-ci : services, guides pratiques et devis.", SERV + [ART[0], ART[2]])]
            blocks = list(t["blocks"]); pos = len(blocks) - 1
            t["blocks"] = blocks[:pos] + add + blocks[pos:]
            continue
        town, typ = t["town"], t["type"]
        add = []
        # 1) les autres services dans la même ville
        sib = sorted([x for x in pages if x["town"] == town and x is not t], key=lambda x: TYPES.index(x["type"]))
        items = [(gen2.fname(x), anchor_of(x)) for x in sib] + [("climatisation-yvelines-78.html", "Climatisation dans les Yvelines (78) : installation, dépannage, entretien, urgence")]
        add.append(("links", "Dans votre ville", f"Les autres services à {t['name']}",
                    "Un besoin différent, une page différente : dépannage, entretien, installation ou urgence.", items))
        # 2) même service dans les villes voisines
        same = sorted([x for x in pages if x["type"] == typ and x["town"] != town], key=lambda x: (dist(town, x["town"]), x["town"]))[:9]
        if same:
            add.append(("links", "Autour de chez vous", f"{TYPE_LABEL[typ]} de climatisation dans les villes voisines",
                        "Si vous êtes à la limite de deux communes, lisez aussi la page d’à côté.", [(gen2.fname(x), anchor_of(x)) for x in same]))
        # 3) un autre service dans les 3 villes les plus proches
        near_towns = []
        for x in sorted(pages, key=lambda x: (dist(town, x["town"]), x["town"])):
            if x["town"] != town and x["town"] not in near_towns: near_towns.append(x["town"])
            if len(near_towns) == 3: break
        cross = []
        for nt in near_towns:
            c = [x for x in pages if x["town"] == nt and x["type"] != typ]
            if c: cross.append(c[k % len(c)])
        if cross:
            add.append(("links", "À côté", "D’autres besoins dans les communes voisines", "Chaque ville a ses pages.", [(gen2.fname(x), anchor_of(x)) for x in cross]))
        # 4) services et guides
        add.append(("links", "Nos services", "Aller plus loin sur la climatisation",
                    "Les pages du site qui complètent celle-ci : services, guides pratiques et devis.", SERV[:] + [ART[k % 5], ART[(k + 2) % 5]]))
        blocks = list(t["blocks"]); pos = len(blocks) - 1
        t["blocks"] = blocks[:pos] + add + blocks[pos:]
