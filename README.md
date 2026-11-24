# Projet Python pour la Data Science

*Auteurs : Lucien Faivre, Jean-Sébastien Dosso, Yoan Laborde-Mouret (2026)*

## Sujet : L'utilisation de la zone 14 par Auckland FC lors de la saison 2024-2025 de l'A-League

Auckland FC participe pour la première fois au championnat australien d'A-League lors de la saison 2024-2025 et termine à la première place de la saison régulière. Ce projet s'intéresse à son animation offensive, en particulier dans la zone 14, située dans l'axe du terrain devant la surface de réparation adverse.

Nous étudions d'abord le profil d'Auckland FC à l'échelle du championnat, notamment ses passes et ses courses sans ballon. Nous analysons ensuite les actions réalisées dans la zone 14 au cours de quatre rencontres, avant de comparer plus précisément Auckland FC à Western United lors du match du 3 mai 2025, remporté 4-2 par Western United.

**Problématique :** Comment Auckland FC utilise-t-il la zone 14 dans son jeu offensif, et quelles différences observe-t-on avec Western United lors de leur confrontation ?

L'étude mobilise des statistiques descriptives, des tableaux comparatifs et des cartes de terrain réalisées avec Python. Les résultats et leurs interprétations sont réunis dans le notebook de synthèse.

## Données

Nous exploitons les données ouvertes de [SkillCorner](https://github.com/SkillCorner/opendata), de deux types :

- des statistiques saisonnières sur les passes, les courses sans ballon et les performances physiques des joueurs de l'A-League 2024-2025 ;
- des données d'événements dynamiques et des informations sur le terrain pour quatre matchs d'Auckland FC.

Les rencontres étudiées sont :

- Auckland FC – Newcastle United Jets, 2-0 (30 novembre 2024) ;
- Auckland FC – Wellington Phoenix, 2-1 (7 décembre 2024) ;
- Western United – Auckland FC, 4-2 (3 mai 2025) ;
- Melbourne Victory – Auckland FC, 0-1 (17 mai 2025).

Les fichiers des matchs, aux formats Parquet et JSON, sont accessibles depuis le stockage S3 d'Onyxia. Les données sont traitées avec `pandas`, tandis que les graphiques sont réalisés avec `matplotlib`.


## Reproduction du projet

**Installation.** Cloner le dépôt et l'ouvrir dans un environnement Python, notamment sur Onyxia. Vérifier la disponibilité des bibliothèques nécessaires :

```bash
pip install pandas matplotlib s3fs pyarrow
```

**Lancement.** Ouvrir les notebooks du dossier `Notebooks/` et exécuter les cellules dans l'ordre. Ils utilisent les fonctions du dossier `src/` et chargent certaines données depuis le stockage distant d'Onyxia. La connexion aux données et le chargement des fonctions avant exécution des commandes des notebooks sont donc nécessaires pour refaire les calculs.

**Restitution.** Ouvrir `synthèse.ipynb`, qui constitue le rapport analytique principal du projet : il présente les figures sélectionnées, les comparaisons et les interprétations. 

## Structure du repo

- Dossier `Notebooks/` : dossier qui contient les différents notebooks permettant de visualiser les différents résultats et contenant les explications de code,
- Dossier `src/` : dossier qui contient les scripts python des fonctions réutilisées dans les notebooks,
- Dossier `images/` : dossier qui contient les figures et tableaux utilisés pour la présentation des résultats,
- Fichier `synthèse.ipynb` : Notebook qui contient le rapport principal du projet avec l'analyse des différentes sorties.




## Compléments : classement final et comparaison avec les autres équipes

Deux compléments sont présentés dans la section 8 de la synthèse :

- le classement final de la saison régulière, récupéré sur [Wikipédia](https://en.wikipedia.org/wiki/2024%E2%80%9325_A-League_Men) par *scraping* et relié au style de jeu des équipes (section 8 du notebook `01_exploration_donnees`) ; une copie du tableau (`data/classement_wikipedia_2024_25.csv`) est utilisée si la page est inaccessible ;
- la comparaison d'Auckland FC avec les autres équipes sur les vingt matchs de l'open data SkillCorner (notebook `05_comparaison_ligue`), lus directement sur le dépôt GitHub de SkillCorner.

Les fonctions correspondantes sont dans `src/donnees.py` et `src/fonctions_comparaison.py`. Ces compléments utilisent en plus `requests` et `lxml` ; toutes les bibliothèques du projet sont listées dans `requirements.txt` :

```bash
pip install -r requirements.txt
```
