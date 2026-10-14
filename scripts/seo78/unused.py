# -*- coding: utf-8 -*-
"""Affiche la prochaine ville à traiter, les mots-clés libres, les angles libres et les ordres de blocs déjà pris."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build, kp_data
q = json.load(open(os.path.join(HERE, "queue.json"), encoding="utf-8"))
done = {t["slug"] for t in build.TOWNS}
todo = [t for t in q["towns"] if t["slug"] not in done]
print("RESTANT DANS LA FILE :", len(todo))
print("PROCHAINE VILLE :", json.dumps(todo[0], ensure_ascii=False) if todo else "AUCUNE — file terminée, ne rien créer")
used = {k for t in build.TOWNS for k in t["kw"]}
print("\nMOTS-CLÉS NATIONAUX LIBRES (nom | volume France | concurrence) :")
for l in kp_data.NATIONAL.strip().splitlines():
    if l.split("|")[0] not in used: print("  ", l)
print("\nANGLES LIBRES :")
taken = {t.get("angle") for t in build.TOWNS}
for a in q["angles"]:
    if a not in taken: print("  -", a)
print("\nORDRES DE BLOCS DÉJÀ UTILISÉS (à ne pas répéter) :")
for t in build.TOWNS: print("  ", t["slug"], [b[0] for b in t["blocks"] if b[0] not in ("links",)])
print("\nANNEAU GÉOGRAPHIQUE (maillage) :", " > ".join(build.maillage.RING))
print("VILLES EXISTANTES (slugs pour near=[...]) :", ", ".join(sorted(done)))
