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



# --- Requête SQL ---
# La requête SQL reste inchangée, elle récupère toutes les données annuelles agrégées par zone.
def get_annuelles_par_zone():
    return ("""
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