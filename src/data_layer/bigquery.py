import streamlit as st
from google.cloud import bigquery
import json

# Crée et met en cache le client BigQuery à partir du secret
@st.cache_resource
def get_bq_client():
    try:
        service_account_info = json.loads(st.secrets["bigquery"]["service_account_json"])
        client = bigquery.Client.from_service_account_info(service_account_info)
        return client
    except KeyError:
        raise KeyError("Missing 'bigquery.service_account_json' in Streamlit secrets. Please configure secrets.toml")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in service_account_json secret: {e}")


# Requête SQL (utilise le client mis en cache)
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
def get_table_histo_simu():
    return run_query(f"""
                     SELECT *
                     FROM `cc-reunion.data_meteofrance.histo_simu_ann`
    """)

def get_table(tab_name):
    return run_query(f"""
                     SELECT *
                     FROM `{tab_name}`
    """)

def get_full_table_for_cyclone():
    return run_query("SELECT * FROM `cc-reunion.data_meteofrance.histo_simu_geo`")

def get_table_pluie_extreme():
    return run_query("""
        WITH CTE AS (
            SELECT 
                NBJFXI3S16X,
                RRMX,
                year,
                CASE
                    WHEN NBJFXI3S16X > 32.7 THEN 'Cyclone'
                    WHEN NBJFXI3S16X > 28.5 THEN 'Tempête Violente'
                    WHEN NBJFXI3S16X > 24.5 THEN 'Tempête'
                    ELSE 'Normal'
                END AS Statut_Alerte_Vent, 
                CASE
                    WHEN RRMX > 5000 THEN 'Année très pluvieuse' 
                    WHEN RRMX > 3000 THEN 'Année Normale'
                    WHEN RRMX > 1000 THEN 'Année Sèche'
                    ELSE 'Normal'
                END AS Forte_pluviometrie
            FROM 
                `cc-reunion.data_meteofrance.histo_simu_geo` AS t1
        )

        SELECT
            Statut_Alerte_Vent,
            Forte_pluviometrie,
            CTE.year,
            CTE.RRMX,
            CTE.NBJFXI3S16X,
            CASE 
                WHEN CTE.NBJFXI3S16X > 32.7 AND CTE.RRMX > 5000 THEN 'Episode Cyclonique Majeur'
                ELSE 'Normal'
            END AS Statut_Cyclone_Majeur,

        FROM CTE 
    """)

    #histo_ann
# CREATE OR REPLACE TABLE `data_meteofrance.histo_simu_geo` AS (
#   SELECT
#     NUM_POSTE,
#     Z_GEO,
#     s_australe,
#     saisons,
#     EXTRACT(YEAR FROM AAAAMM) AS year,
#     AVG(TM) AS TMM,
#     AVG(TN) AS TNM,
#     AVG(TX) AS TXM,
#     SUM(NBJTXS32) AS TXS32,
#     SUM(NBJTNS25) AS TNS25,
#     SUM(RR) AS RRM,
#     SUM(NBJRR100) AS RRS100
#   FROM `cc-reunion.data_meteofrance.histo_simu_geo `
#   GROUP BY 1,2,3,4,5
# )


def get_detection_precip_superieure100mm():
    return run_query("""
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
        GROUP BY 
            ANNEE, 
            MOIS, 
            AAAAMM

        ORDER BY 
            AAAAMM ASC
        )

        SELECT *
        FROM CTE
        WHERE Nb_Jours_Sup_100mm > 1
    """)

# --- Requête SQL ---
# La requête SQL reste inchangée, elle récupère toutes les données annuelles agrégées par zone.
def get_annuelles_par_zone():
    return run_query("""
        WITH CTE AS (
        SELECT
            t1.ANNEE,
            t2.Z_CLIM,
            t2.Z_GEO,
            AVG(t1.total_jours_sup_32c_annuel) AS moyenne_jours_chauds_zone,
            COUNT(DISTINCT t1.NUM_POSTE) AS nombre_stations_incluses
        FROM 
            `cc-reunion.MENS_meteofrance.Table_NBJTXS32_ANNEE` AS t1
        INNER JOIN
            `cc-reunion.MENS_meteofrance.stations` AS t2
            ON t1.NUM_POSTE = t2.NUM_POSTE
        GROUP BY 
            t1.ANNEE,
            t2.Z_CLIM,
            t2.Z_GEO
        )
        SELECT
            ANNEE,
            Z_CLIM,
            Z_GEO,
            moyenne_jours_chauds_zone,
            nombre_stations_incluses
        FROM CTE
        ORDER BY 
            ANNEE,
            Z_CLIM;
        """)


# --- Requête SQL (Version Statique 2100) ---
# La requête a été simplifiée et corrigée pour ne calculer que la projection en 2100.
def get_projection_2100():
    return run_query("""
        WITH T_OBS_REF AS (
            -- 1. CALCUL DE LA BASELINE OBSERVÉE PAR STATION (Moyenne 1991-2020)
            SELECT
                t1.NUM_POSTE,
                t2.Z_CLIM,
                t2.Z_GEO,
                AVG(t1.total_jours_sup_32c_annuel) AS baseline_jours_chauds_ref
            FROM
                `cc-reunion.MENS_meteofrance.Table_NBJTXS32_ANNEE` AS t1
            INNER JOIN
                `cc-reunion.MENS_meteofrance.stations` AS t2 
                ON t1.NUM_POSTE = t2.NUM_POSTE
            WHERE
                t1.ANNEE BETWEEN '1991' AND '2020' 
            GROUP BY
                t1.NUM_POSTE, t2.Z_CLIM, t2.Z_GEO
        ),

        T_PROJ_AGR AS (
            -- 2. CALCUL DU DELTA MOYEN PAR ZONE UNIQUEMENT POUR L'ANNÉE 2100
            SELECT
                t2.Scenario, 
                t2.Z_GEO, 
                AVG(t2.NBJTXS32) AS delta_jours_chauds_moyen_2100
            FROM
                `cc-reunion.MENS_meteofrance.Table_sim_2100` AS t2 
            WHERE
                EXTRACT(YEAR FROM t2.date_2100) = 2100 
            GROUP BY 
                t2.Scenario, t2.Z_GEO
        )

        -- 3. JOINTURE FINALE ET CALCUL DE LA PROJECTION STATIQUE (HORIZON 2100)
        SELECT
            2100 AS ANNEE_HORIZON, 
            T_PROJ.Scenario,
            T_ST.Z_CLIM,
            T_PROJ.Z_GEO,
            
            -- Calcul du centroïde de la zone
            AVG(T_ST.LAT) AS latitude_centre,
            AVG(T_ST.LON) AS longitude_centre,
            
            -- Projection = Baseline Moyenne de Zone + Delta 2100
            AVG(T_OBS_REF.baseline_jours_chauds_ref) AS baseline_jours_chauds_zone,
            AVG(T_OBS_REF.baseline_jours_chauds_ref) + T_PROJ.delta_jours_chauds_moyen_2100 AS jours_chauds_projete_2100,
            T_PROJ.delta_jours_chauds_moyen_2100 AS delta_projection_2100 
            
        FROM
            T_PROJ_AGR AS T_PROJ
        INNER JOIN
            `cc-reunion.MENS_meteofrance.stations` AS T_ST 
            ON T_PROJ.Z_GEO = T_ST.Z_GEO
        INNER JOIN
            T_OBS_REF 
            ON T_ST.NUM_POSTE = T_OBS_REF.NUM_POSTE
            
        GROUP BY
            T_PROJ.Scenario,
            T_ST.Z_CLIM,
            T_PROJ.Z_GEO,
            T_PROJ.delta_jours_chauds_moyen_2100
        ORDER BY
            T_ST.Z_CLIM, T_PROJ.Scenario;
        """)