import streamlit as st
from google.cloud import bigquery

# Initialiser le client BigQuery

@st.cache_resource
def get_bq_client():
    return bigquery.Client()

# Requête SQL
@st.cache_data
def run_query(sql: str):
    client = get_bq_client()
    return client.query(sql).to_dataframe()
    
# Exemple de fonction qui fait un truc
def get_todo1():
    return run_query(f"""
        WITH CTE AS (
        SELECT 
            ANNEE AS annee,
            MOIS AS mois,
            -- On garde AAAAMM pour le tri ou l'affichage chronologique
            AAAAMM AS date_key, 

            -- Somme des précipitations pour la période donnée
            AVG(RR) AS Cumul_Mensuel_Pluie_Total,

            --  'NBRR', c'est le nombre de jours de pluie

            -- RRAB précipitation maximale tombée en 24 heures au cours du mois (Average)
            AVG(RRAB) AS Cumul_MAxi_par_mois,

            -- Nombre de jours > 100mm
            AVG(NBJRR100) AS Nb_Jours_Sup_100mm

        FROM `cc-reunion.data_meteofrance.stg_mensq_pluviometrie`
        -- Indispensable pour fusionner les données de toutes les stations par mois
        GROUP BY 
            ANNEE, 
            MOIS, 
            AAAAMM

        -- Tri par ordre chronologique (ce qui réglera aussi ton problème de tri dans le graph)
        ORDER BY 
            AAAAMM ASC
        )

        SELECT *
        FROM CTE
        WHERE Nb_Jours_Sup_100mm > 1
    """)

def get_data():
    return run_query("""
                     SELECT ANNEE, moy_nuits_ge_20 
                     FROM `cc-reunion.data_meteofrance.int_mensq_temperatures_sup_20deg`
                     ORDER BY ANNEE ASC
    """)

def get_nb_moy_nuits_sup_20deg():
    return run_query("""
                     SELECT ANNEE, AVG(moy_nuits_ge_20) as nb_moy_nuits_sup_20deg
                     FROM `cc-reunion.data_meteofrance.int_mensq_temperatures_sup_20deg`
                     GROUP BY ANNEE
                     ORDER BY ANNEE ASC
    """)

def get_nb_moy_nuits_sup_20deg_par_zone_par_annee():
    return run_query("""
        WITH nuit_par_station AS (
        SELECT
            t.NUM_POSTE,
            sz.Z_GEO,
            t.ANNEE,
            SUM(t.NBJTNS20) AS nuits_ge_20_par_station
        FROM `cc-reunion.data_meteofrance.stg_mensq_temperatures` t
        JOIN `cc-reunion.MENS_meteofrance.stations_zones` sz
            ON t.NUM_POSTE = sz.NUM_POSTE
        GROUP BY t.NUM_POSTE, sz.Z_GEO, t.ANNEE
        ),

        par_zone AS (
        SELECT
            ANNEE,
            Z_GEO,
            COUNT(*) AS nb_stations,
            AVG(nuits_ge_20_par_station) AS moy_nuits_ge_20
        FROM nuit_par_station
        GROUP BY ANNEE, Z_GEO
        )

        SELECT
            ANNEE,
            Z_GEO AS zone_geographique,
            moy_nuits_ge_20,
            nb_stations
        FROM par_zone
        ORDER BY zone_geographique, ANNEE
    """)
