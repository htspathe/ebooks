# ebooks — KDP Production Studio

Dépôt central pour produire, vérifier et publier des livres Amazon KDP.

## Première collection
- `books/halloween-2026/` : *Cute Halloween Coloring Book*, 40 illustrations prévues, format 8.5 × 11 pouces, noir et blanc, sans fond perdu.
- Actuellement, le projet reste **NON PUBLIABLE** tant que les 40 illustrations, la résolution et la revue éditoriale ne sont pas validées.

## Workflow
1. Ajouter les illustrations individuelles dans `books/halloween-2026/assets/originals/page_XX.png`.
2. Mettre à jour `manifest.csv` et `book.json`.
3. Installer `pip install -r requirements.txt`.
4. Lancer `python tools/kdp_check.py books/halloween-2026 --out reports/halloween-quality.json`.
5. Préparer un brouillon : `python tools/build_interior.py books/halloween-2026 --draft`.
6. Corriger les erreurs, faire une revue humaine des légendes, du comptage et des visuels, puis générer l'intérieur définitif et vérifier dans KDP Print Previewer.

Les scripts et le registre de production seront ajoutés progressivement. Aucun agent ne publie sur Amazon automatiquement.
