# Fichier : Simulation_temperature_extreme_2100_Reunion.py

# Importations nécessaires
from google.cloud import bigquery
import streamlit as st 
import pandas as pd
import altair as alt

## Configuration de la page Streamlit
st.set_page_config(
    page_title="Simulation Température extrême à La Réunion en 2100",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ Simulation des Jours de Forte Chaleur à La Réunion en 2100 (Projection 2100)")

# --- Initialisation du client BigQuery ---
client = bigquery.Client() # 🚨 CORRECTION : Initialisation du client

# --- Requête SQL (Version Statique 2100) ---
# La requête a été simplifiée et corrigée pour ne calculer que la projection en 2100.
query = """
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
"""

# --- Fonction de chargement des données (avec cache) ---
@st.cache_data
def load_data():
    # Exécute la requête SQL et retourne le DataFrame
    df = client.query(query).to_dataframe()
    return df

try:
    # 1. Chargement des données
    data_proj = load_data()
    
    # 2. Barre latérale et Filtres Interactifs
    # --------------------------------------------------------------------------
    st.sidebar.header("Filtres Scénario 📈")
    
    # Sélecteur de Scénario (RCP 4.5 vs RCP 8.5)
    scenarios_uniques = sorted(data_proj['Scenario'].unique().tolist())
    scenario_selectionne = st.sidebar.selectbox(
        "Choisissez un Scénario de Réchauffement :", 
        scenarios_uniques
    )
    
    # Filtrage du DataFrame par Scénario
    df_filtre = data_proj[data_proj['Scenario'] == scenario_selectionne]

    
    # --- Indicateurs de Performance (KPI) ---
    st.subheader(f"Projection d'Augmentation des Jours Chauds ({scenario_selectionne})")
    col1, col2 = st.columns(2)

    # 1. Zone la plus touchée (Delta Max)
    max_delta = df_filtre['delta_projection_2100'].max()
    zone_max = df_filtre[df_filtre['delta_projection_2100'] == max_delta]['Z_CLIM'].iloc[0]
    
    col1.metric(
        "Augmentation Maximale Projetée (2100)", 
        f"+{max_delta:.1f} jours/an",
        f"Zone : {zone_max}"
    )
    
    # 2. Moyenne de l'augmentation sur l'île (Delta Moyen)
    delta_moyen_ile = df_filtre['delta_projection_2100'].mean()
    col2.metric(
        "Augmentation Moyenne sur La Réunion",
        f"+{delta_moyen_ile:.1f} jours/an"
    )

    # --- Visualisation 1 : Cartographie du Changement (Carte Choroplèthe) ---
    st.subheader(f"Carte du Changement Projeté (Delta Tmax > 32°C) - Scénario {scenario_selectionne}")
    
    # Altair ne fait pas de choroplèthes directement, mais peut afficher des points colorés.
    # Pour simuler la cartographie du changement par zone, nous utilisons la couleur sur le delta.
    
    # Utilisation des coordonnées moyennes de la zone (calculées dans la requête SQL)
    chart_map = alt.Chart(df_filtre).mark_circle().encode(
        latitude='latitude_centre:Q',
        longitude='longitude_centre:Q',
        size=alt.Size('delta_projection_2100:Q', title="Augmentation Jours Chauds (Delta)"),
        color=alt.Color('delta_projection_2100:Q', title="Delta Jours Chauds (2100)", scale=alt.Scale(range='heatmap')),
        tooltip=['Z_CLIM', 'baseline_jours_chauds_zone:Q', 'delta_projection_2100:Q', 'jours_chauds_projete_2100:Q']
    ).properties(
        title="Impact du Changement Climatique sur les Jours Chauds (Horizon 2100)"
    ).interactive()

    st.altair_chart(chart_map, use_container_width=True)
    
    # --- Visualisation 2 : Comparaison de la Projection (Baseline vs. Futur) ---
    st.subheader(f"Comparaison Baseline (1991-2020) vs. Projection 2100 - Scénario {scenario_selectionne}")
    
    # On reformate le DataFrame pour Altair
    df_long = df_filtre.melt(
        id_vars=['Z_CLIM', 'Scenario'],
        value_vars=['baseline_jours_chauds_zone', 'jours_chauds_projete_2100'],
        var_name='Type_Valeur',
        value_name='Jours_Chauds'
    )
    
    chart_bar_comparison = alt.Chart(df_long).mark_bar().encode(
        x=alt.X('Jours_Chauds:Q', title='Jours > 32°C Moyens/an'),
        y=alt.Y('Z_CLIM:N', title='Zone Climatique', sort='-x'),
        color=alt.Color('Type_Valeur:N', title='Période', scale=alt.Scale(domain=['baseline_jours_chauds_zone', 'jours_chauds_projete_2100'], range=['#93B5C9', '#E63946'])),
        column=alt.Column('Type_Valeur:N', header=alt.Header(titleOrient="bottom", labelOrient="bottom")),
        tooltip=['Z_CLIM', 'Type_Valeur', alt.Tooltip('Jours_Chauds:Q', format='.1f')]
    ).properties(
        title="Augmentation des Jours Chauds par Zone"
    ).interactive()

    st.altair_chart(chart_bar_comparison, use_container_width=False)
    
    # 4. Affichage du DataFrame
    st.subheader(f"Aperçu des Données (Projection 2100)")
    st.dataframe(df_filtre.head(10))


except Exception as e:
    st.error(f"Une erreur s'est produite lors de l'exécution : {e}")
    st.warning("Vérifiez la connexion à BigQuery, les identifiants et le nom des colonnes (ex: `latitude`, `longitude` dans `T_ST`).")