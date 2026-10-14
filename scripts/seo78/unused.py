# -*- coding: utf-8 -*-
"""Affiche la prochaine page à créer (ville + type), les mots-clés libres, les angles libres, les ordres de blocs pris."""
import sys, os, json, re, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build, kp_data, gen2
q = json.load(open(os.path.join(HERE, "queue.json"), encoding="utf-8"))
def slug(n):
    n = n.replace("’", "'").lower(); n = unicodedata.normalize("NFD", n); n = "".join(c for c in n if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", n).strip("-")
have = {(t["town"], t["type"]) for t in build.TOWNS}
towns = list(q["priority_existing"]) + [x["slug"] for x in q["towns"]]
names = {x["slug"]: x["name"] for x in q["towns"]}
names.update({t["town"]: t["name"] for t in build.TOWNS})
jobs = [(tw, ty) for tw in towns for ty in q["types"] if (tw, ty) not in have]
print("PAGES RESTANTES :", len(jobs))
if not jobs:
    print("PROCHAINE PAGE : AUCUNE — file terminée, ne rien créer"); sys.exit(0)
tw, ty = jobs[0]
ex = next((t for t in build.TOWNS if t["town"] == tw), None)
print("PROCHAINE PAGE :", json.dumps({"town": tw, "name": names.get(tw, tw), "type": ty,
      "slug_page": f"{ty}-{tw}", "fichier": f"zones/{ty}-climatisation-{tw}.html",
      "cp_connu": ex["cp"] if ex else None, "communes_voisines_connues": ex["areas"] if ex else None}, ensure_ascii=False))
print("  -> villes déjà couvertes qui sont voisines (pour near=[...]) : voir l'anneau ci-dessous ; la ville est-elle dans l'anneau ?", tw in build.maillage.RING)
used = {k for t in build.TOWNS for k in t["kw"]}
print(f"\nMOTS-CLÉS NATIONAUX LIBRES POUR LE TYPE « {ty} » (mot clé exact à reprendre mot pour mot) :")
for k in q["kw_by_type"][ty]:
    if k not in used:
        row = next((l for l in kp_data.NATIONAL.splitlines() if l.startswith(k + "|")), "")
        print("  ", row or k)
print("  + mots-clés locaux à utiliser (non relevés par Google mais ce que les gens tapent) :")
nm = slug(names.get(tw, tw)).replace("-", " ")
for pre in {"depannage": ["depannage climatisation", "depannage clim", "reparation climatisation"], "entretien": ["entretien climatisation", "entretien clim", "nettoyage climatisation"],
            "urgence": ["urgence climatisation", "depannage climatisation urgence"], "installation": ["installation climatisation", "pose climatisation", "devis climatisation"]}[ty]:
    print("   ", f"{pre} {nm}")
taken = {t.get("angle") for t in build.TOWNS}
print(f"\nANGLES LIBRES POUR « {ty} » (recopier l'un d'eux EXACTEMENT dans le champ angle) :")
for a in q["angles_by_type"][ty]:
    if a not in taken: print("  -", a)
print("\nORDRES DE BLOCS DÉJÀ UTILISÉS (ne pas répéter ; 4 à 6 blocs avant faq/zone) :")
for t in build.TOWNS: print("  ", t["slug"], [b[0] for b in t["blocks"] if b[0] != "links"])
print("\nANNEAU (maillage) :", " > ".join(build.maillage.RING))
print("PAGES EXISTANTES (slug → type) :", ", ".join(f'{t["slug"]}:{t["type"]}' for t in build.TOWNS))
