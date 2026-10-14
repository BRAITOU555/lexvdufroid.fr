# -*- coding: utf-8 -*-
"""Fichier de mots-clés (national, 78, par ville). Usage : python3 -I scripts/seo78/keywords.py [sortie.csv]"""
import sys, os, csv, json, re, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build, kp_data, gen2
q = json.load(open(os.path.join(HERE, "queue.json"), encoding="utf-8"))
def slug(n):
    n = n.replace("’", "'").lower(); n = unicodedata.normalize("NFD", n); n = "".join(c for c in n if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", n).strip("-")
GOOGLE = {k: (v, c) for k, v, c, *_ in kp_data.ALL}
NOGOOGLE = "pas de donnée Google (moins de 10 / mois)"
pages = {(t["town"], t["type"]): t for t in build.TOWNS}
used = {}
for t in build.TOWNS:
    for k in t["kw"]: used[k] = gen2.fname(t)
names = {x["slug"]: x["name"] for x in q["towns"]}; names.update({t["town"]: t["name"] for t in build.TOWNS})
towns = list(q["priority_existing"]) + [x["slug"] for x in q["towns"]]
SERV = {
 "depannage": ["depannage climatisation", "depannage clim", "reparation climatisation", "reparation climatiseur"],
 "entretien": ["entretien climatisation", "entretien clim", "nettoyage climatisation", "contrat entretien climatisation"],
 "urgence": ["urgence climatisation", "depannage climatisation urgence", "climatisation en panne urgence"],
 "installation": ["climatisation", "installation climatisation", "pose climatisation", "devis climatisation", "installateur climatisation"],
}
def target(tw, ty, kw):
    t = pages.get((tw, ty))
    if kw in used: return used[kw], "page en ligne"
    if t: return gen2.fname(t), "page en ligne"
    return f"{ty}-climatisation-{tw}.html", "page à créer"
def row(kw, scope, ville, service, page, etat):
    v, c = GOOGLE.get(kw, (NOGOOGLE, "—"))
    if v == "—": v = NOGOOGLE
    return [kw, v, c, scope, ville, service, "zones/" + page if page else "", etat]
out = [["mot clé", "recherches mensuelles (France, fourchette Google)", "concurrence", "portée", "ville", "service", "page cible", "état de la page"]]
# 1) national (relevé Google)
for kw, (v, c) in sorted(GOOGLE.items(), key=lambda x: x[0]):
    if not any(kw.endswith(" " + n.lower().replace("-", " ")) for n in names.values()) and "78" not in kw.split() and "yvelines" not in kw:
        out.append([kw, v, c, "national", "", "", ("zones/" + used[kw]) if kw in used else "page départementale / réserve", "page en ligne" if kw in used else "réserve"])
# 2) département
for kw in ["climatisation 78", "climatisation yvelines", "depannage climatisation 78", "depannage climatisation yvelines", "installation climatisation 78", "installation climatisation yvelines",
           "installateur climatisation 78", "entretien climatisation 78", "entretien climatisation yvelines", "urgence climatisation 78", "urgence climatisation yvelines"]:
    out.append(row(kw, "département 78", "Yvelines", "", "climatisation-yvelines-78.html", "page en ligne"))
# 3) par ville × service
for tw in towns:
    nm = slug(names.get(tw, tw)).replace("-", " ")
    for ty, pres in SERV.items():
        for pre in pres:
            kw = f"{pre} {nm}".strip()
            pg, etat = target(tw, ty, kw)
            out.append(row(kw, "ville", names.get(tw, tw), ty, pg, etat))
dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "mots-cles-78.csv")
with open(dest, "w", newline="", encoding="utf-8-sig") as f:
    csv.writer(f, delimiter=";").writerows(out)
print(len(out) - 1, "lignes ->", dest)
