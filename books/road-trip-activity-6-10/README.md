# BOOK_001 — Road Trip Activity Book for Kids

Premier livre pilote de la KDP Factory de Production OS.

- **Audience :** enfants de 6 à 10 ans
- **Langue :** anglais (prévue)
- **Marché :** Amazon.com (à confirmer)
- **Format :** broché, 8.5 × 11 pouces, intérieur noir et blanc
- **Longueur :** exactement 80 pages, pages de début incluses
- **Statut :** plan enregistré ; 48 activités programmatiques (pages 15–54 et 73–80) générées en SVG avec corrigés et contrôles algorithmiques. Leur revue visuelle reste à faire. Les illustrations de coloriage et les paires « cherche les différences » ne sont pas encore intégrées ; le PDF final de 80 pages n'est pas assemblé.

## Fichiers de référence

- `BOOK_SPEC.md` — spécifications et règles non négociables.
- `PAGE_PLAN.md` — répartition et contenu prévu des pages 1 à 80.
- `PAGE_MANIFEST.csv` — registre structuré des 80 pages et contrôles associés.
- `KDP_PROGRESS_STATE.json` — état lisible par les agents et l'orchestrateur.
- `QA_CHECKLIST.md` — critères de validation des activités et du paquet KDP.

## Règle de pagination

PAGE_PLAN.md et PAGE_MANIFEST.csv définissent ensemble la pagination officielle du pilote. Toute modification doit mettre à jour les deux fichiers et KDP_PROGRESS_STATE.json. Le total doit rester à 80 pages.

## Workflow cible

1. Recherche de marché et bibliothèque de références.
2. Bible éditoriale et validation humaine du concept.
3. Génération des puzzles et corrigés par code.
4. Production des illustrations originales.
5. Assemblage de l'intérieur et de la couverture.
6. Contrôles automatisés, inspection visuelle et correction.
7. Préparation d'un dossier KDP ; soumission manuelle uniquement.

## Production programmatique

Le moteur et ses 48 pages SVG générées se trouvent dans `production/programmatic_activities/`. Les corrigés et le rapport de validation sont dans `generated_activities/answer_keys/` et `generated_activities/VALIDATION_REPORT.json`. Le statut reste `GENERATED_NEEDS_VISUAL_REVIEW` jusqu'à inspection humaine de toutes les pages.
