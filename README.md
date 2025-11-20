# Projet-CC : Analyse du climat à La Réunion

Ce dépôt contient le code, les transformations et la documentation nécessaires pour analyser les données climatiques de La Réunion, depuis l’ingestion des données brutes jusqu’à la création d’un dashboard interactif avec Streamlit.

Le projet repose sur BigQuery et dbt pour assurer un pipeline analytique propre, testé (en cours 👀) et maintenable.

## Objectifs du projet

Explorer les données climatiques officielles de La Réunion.

Nettoyer et valider les données via dbt.

Produire des tables analytiques prêtes à être visualisées.

Alimenter un tableau de bord Streamlit permettant d’explorer :

- les températures,
- les précipitations,
- la fréquence des événements extrêmes,
- les tendances historiques (par région climatique, etc.).

## Architecture du projet
project-root/
├── data/                     # Données brutes générées (à conserver ?)
├── dbt/
│   ├── models/
│   │   ├── staging/          # Nettoyage, typage, qualité minimale
│   │   ├── intermediate/     # Jointures, enrichissements, transformations
│   │   └── marts/            # Tables finales utilisées par Streamlit
│   ├── tests/                # Tests de qualité dbt (unique, not null, etc.)
│   └── macros/               # Macros dbt personnalisées
├── dashboard/                # Documentation liée au dashboard Streamlit
└── README.md

## Dépendances principales

Google BigQuery

dbt Core + adaptateur BigQuery

Looker Studio (pour la data viz)

Python 3.11+ (optionnel selon ton code local)

## Installation & Setup
1. Cloner le projet
git clone git@github.com:<ORG>/<REPO>.git
cd <REPO>

2. Installer dbt BigQuery
pip install dbt-bigquery

3. Configurer les credentials GCP

Place ton fichier service_account.json et configure l’authentification :

export GOOGLE_APPLICATION_CREDENTIALS="path/to/service_account.json"

4. Tester la connexion
dbt debug

## Pipeline de données
● Préparation BigQuery

Conversion de dates (AAAAMM → DATE)

Filtrage des enregistrements non validés

Exclusion des périodes trop anciennes ou incomplètes

Jointure avec les métadonnées des stations

● Modèles dbt

staging :
normalisation des colonnes, types, validation qualité

intermediate :
agrégation, enrichissements, calcul d'indicateurs

marts :
tables prêtes à être consommées par Looker Studio

## Dashboard

Un dashboard Looker Studio est disponible ici : (lien)

Il permet notamment :
- 

## Tests dbt

## Auteur·ices

Olive KAYITESI
Nicolas MERINIAN
Chloé RADICE
Marc RENAUDIE
Said Abbas SAID ABDALLAH