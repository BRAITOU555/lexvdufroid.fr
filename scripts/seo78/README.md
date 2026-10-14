# Création automatique de pages « climatisation Yvelines (78) »

Chaque passage crée **UNE** nouvelle page de ville, rédigée à la main (pas de gabarit à trous), la contrôle, puis pousse sur `main`.
Le site se met en ligne tout seul quand `main` est poussé. Ne rien faire d'autre (ni zip, ni AMP).

## Procédure (dans l'ordre)
1. `git pull origin main`, puis `python3 -I scripts/seo78/unused.py` : donne la ville suivante, les mots-clés libres, les angles libres, les ordres de blocs déjà utilisés et les pages existantes. Si « AUCUNE », s'arrêter sans rien créer.
2. Lire UN exemple complet pour le format : `scripts/seo78/pages/p5.py` (page Limay ou Montesson) et `scripts/seo78/gen2.py` (fonction `block`) pour les types de blocs : `text`, `list`, `photo`, `price`, `editorial`, `faq`, `zone`.
3. Vérifier les faits locaux de la ville avec WebSearch (code postal, communes voisines, quartiers, gare). Ce qu'on ne peut pas vérifier : rester général, ne rien inventer.
4. Créer `scripts/seo78/pages/pNN_<slug>.py` (NN = numéro suivant, 2 chiffres) contenant une liste en MAJUSCULES, ex. `PAGES_SLUG = [dict(...)]`, avec **tous** les champs : `slug, name, cp, crumb, title, meta, h1, eyebrow, lead, points, hero, hero_alt, caption, intro, blocks, faq, areas, kw, near, next_h2, next_p, foot, service_type, angle, date` (`date` = date du jour AAAA-MM-JJ, `angle` = texte EXACT d'un angle libre de `queue.json`).
5. Ajouter la ville au maillage : dans `scripts/seo78/maillage_extra.py`, ajouter à `EXTRA` un tuple `("slug", "slug_de_la_ville_voisine_dans_l_anneau", "Texte du lien : sujet de la page")`.
6. `python3 -I scripts/seo78/build.py` puis `python3 -I scripts/seo78/check.py`. Si ÉCHEC : corriger la page (jamais les contrôles) et recommencer. Ne pas pousser tant que `check.py` n'est pas vert.
7. `git add -A`, commit « Yvelines : page <ville> » avec les lignes d'attribution demandées, `git pull --rebase origin main`, `git push origin HEAD:main`.

## Règles de contenu (non négociables)
- **Aucun prix, aucun montant, aucun « € » / « euros »**. On peut écrire « prix », « tarif », « devis » comme mots, jamais un chiffre.
- **Mots-clés** : `kw` = `climatisation <ville>` (volume Keyword Planner 0–10 pour les petites villes) + 2 à 4 mots-clés nationaux libres affichés par `unused.py`. Un mot-clé = une seule page. Chaque mot-clé doit apparaître mot pour mot dans le texte (titre, H1, H2, paragraphes, questions de FAQ, jamais plus de 2 fois chacun). Ne pas bourrer.
- **Ton** : phrases courtes, concrètes, comme un technicien qui parle à un voisin. Interdit : « il est important de noter », « n'hésitez pas », « découvrez », « véritable », « incontournable », « clé en main », « sur mesure », listes de bénéfices génériques, titres creux.
- **Unicité** : angle différent de toutes les pages existantes, ordre et nombre de blocs différents des autres pages (voir `unused.py`), une photo `hero` qui existe dans `images/` (fichiers `.png`, le site sert les `.webp`), 5 à 7 questions de FAQ propres à la ville et à l'angle. Similarité max autorisée : 8 % (mesurée par `check.py`).
- **Géographie** : uniquement des communes réellement des Yvelines (78) ; pas d'Hauts-de-Seine ni de Val-d'Oise.
- Pas de promesse inventée (agréments, certifications, délais garantis, avis clients).
- Ne jamais modifier les pages existantes à la main : tout passe par `scripts/seo78/`.

## Limites
Si WebSearch ne répond pas, créer la page avec des faits généraux. Si un push échoue (conflit), `git pull --rebase` puis repousser une seule fois ; sinon s'arrêter et le dire.
