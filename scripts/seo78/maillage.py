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

def apply(TOWNS):
    idx = {s:i for i,s in enumerate(RING)}
    N = len(RING)
    for k, t in enumerate(TOWNS):
        s = t["slug"]
        if s == "yvelines-78":
            others = [x for x in TOWNS if x["slug"] != s]
            hubl = []
        else:
            me = idx[s]
            others = sorted([x for x in TOWNS if x["slug"] not in (s, "yvelines-78")],
                            key=lambda x: min((idx[x["slug"]]-me) % N, (me-idx[x["slug"]]) % N))
            hubl = [("climatisation-yvelines-78.html", "Climatisation dans les Yvelines (78) : installation, dépannage, entretien")]
        items = hubl + [(gen2.fname(x), ANCH[x["slug"]]) for x in others] if s != "yvelines-78" else []
        blocks = list(t["blocks"])
        pos = len(blocks) - 1  # avant "zone"
        add = []
        if items:
            add.append(("links", "Autour de chez vous", "Les autres villes des Yvelines où nous intervenons",
                        "Chaque page décrit un besoin précis. Si vous êtes à la limite de deux communes, lisez aussi celle d’à côté.", items))
        a1 = ART[(k) % 5]; a2 = ART[(k+2) % 5]
        sv = SERV[:]
        add.append(("links", "Nos services", "Aller plus loin sur la climatisation",
                    "Les pages du site qui complètent celle-ci : services, guides pratiques et devis.", sv + [a1, a2]))
        t["blocks"] = blocks[:pos] + add + blocks[pos:]
