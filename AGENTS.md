# Agents — ebooks KDP

## Règle fondamentale
Ne jamais qualifier un livre de « prêt à publier » si des contrôles techniques ou éditoriaux sont ouverts. Ne jamais approuver une page au nom de l'humain.

## Agent 1 — Catalog Manager
Met à jour le manifest CSV, vérifie la présence et l'indexation des 40 pages et classe les illustrations sources sous `books/<slug>/assets/originals/page_XX.png`.

## Agent 2 — Image QA
Exécute `python tools/kdp_check.py books/halloween-2026`, examine dimensions pixels / ppp, blancs / aplats noirs et images très similaires. Les alertes de ressemblance restent à interpréter.

## Agent 3 — Editorial QA
Vérifie chaque instruction en anglais, le nombre réel d'objets, la variété des scènes, la lisibilité des caractères et l'adaptation pour les enfants 4–8 ans. Consigne l'approbation dans le manifeste après revue réelle.

## Agent 4 — Print Preflight
Contrôle 8.5×11 pouces, position du texte, fond perdu, marges, versos blancs, pages dans l'ordre, PDF final et gabarit de couverture KDP.

## Agent 5 — Publishing Reviewer
N'autorise le passage en revue KDP que si tous les contrôles sont validés. La déclaration des contenus générés par IA, la revue des droits et la prévisualisation KDP restent obligatoires.

Les scripts n'envoient pas de fichiers sur Amazon et ne peuvent pas se substituer à la validation KDP.
