# Projet-CC : Analyse du climat à La Réunion

**Défi Changement Climatique**  
Analyse des données météorologiques françaises en open data, avec un focus sur l’Île de La Réunion.

Ce projet s’inscrit dans le cadre du défi national [data.gouv.fr - Changement Climatique](https://defis.data.gouv.fr/defis/changement-climatique), organisé par l’association Latitudes.

Ce dépôt contient le code, les transformations et la documentation nécessaires pour analyser les données climatiques de La Réunion, depuis l’ingestion des données brutes jusqu’à la production d’un dashboard interactif avec Looker Studio.

Le projet repose sur **BigQuery** et **dbt** pour assurer un pipeline analytique structuré, testé et maintenable.

(lien dans la section *Dashboard*)

---

## Objectifs

- Explorer les données climatiques officielles de La Réunion.
- Nettoyer et valider les données via dbt (données Météo-France).
- Produire des tables analytiques prêtes à la visualisation.
- Réaliser des analyses exploratoires (SQL / Python) :
  - Températures et précipitations
  - Fréquence des événements extrêmes
  - Tendances historiques par région climatique, etc.
- Alimenter un tableau de bord interactif avec Looker Studio.

---

## Architecture du projet
```
project-root/
├── data/ # Données brutes (à conserver ?)
├── dbt/
│ ├── models/
│ │ ├── staging/ # Nettoyage, typage, contrôle qualité minimal
│ │ ├── intermediate/ # Jointures, enrichissements, transformations
│ │ └── marts/ # Tables finales pour la dataviz
│ ├── tests/ # Tests dbt (unique, not null, etc.)
│ └── macros/ # Macros dbt personnalisées
├── dashboard/ # Documentation du dashboard Looker Studio
└── README.md
```

---

## Technologies utilisées

- **BigQuery** : exploration SQL et agrégations  
- **dbt** : modélisation, documentation, tests qualité  
- **Python** : analyses ponctuelles avec Numpy, Pandas, Altair, Plotly  
- **Streamlit** : visualisation et dashboard  
- **Git** : gestion de version  
- **Open data Météo-France** : données climatiques  

---

## Dépendances principales

- Google BigQuery  
- dbt Core + adaptateur BigQuery  
- Streamlit (dashboard)  
- Python 3.11+ (optionnel selon le code local)

---

## Installation & Setup

1. **Cloner le projet**
```bash
git clone git@github.com:<ORG>/<REPO>.git
cd <REPO>
```

2. **Installer dbt BigQuery**
```bash
pip install dbt-bigquery
```

3. **Configurer les credentials GCP**
Place ton fichier service_account.json et configure l’authentification :
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service_account.json"
```

4. **Tester la connexion**
```bash
dbt debug
```

## Pipeline de données

### Préparation BigQuery :

- Conversion des dates (AAAAMM → DATE)
- Filtrage des enregistrements non validés
- Exclusion des périodes trop anciennes ou incomplètes
- Jointure avec les métadonnées des stations

### Modèles dbt :

- staging : normalisation des colonnes, typage, validation qualité
- intermediate : agrégation, enrichissements, calcul d’indicateurs
- marts : tables prêtes à la consommation par l’outil de dataviz (Looker Studio)

## Dashboard

Le dashboard Streamlit permet d’explorer :
- Températures (Jour / Nuit)
- Précipitations
- Événements extrêmes
- Prévisions futures

Lien vers le dashboard : https://projet-cc.streamlit.app/

## Tests dbt

Des tests de qualité sont définis dans dbt/tests pour valider les données et assurer la fiabilité des tables analytiques.

# Auteur·ices

Olive KAYITESI – [GitHub](https://github.com/kayitesiolive23-tech)

Nicolas MERINIAN – [GitHub](https://github.com/nicolasmerinian)

Chloé RADICE – [GitHub](https://github.com/chloe-radice)

Marc RENAUDIE – [GitHub](https://github.com/Jassat)

Said Abbas SAID ABDALLAH – [GitHub](https://github.com/ssaidabdallah142-hub)
