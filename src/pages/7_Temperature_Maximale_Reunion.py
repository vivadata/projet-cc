# Fichier : Température_Maximale_Réunion.py

# Importations nécessaires
from google.cloud import bigquery
import streamlit as st
import pandas as pd
import altair as alt

## Configuration de la page Streamlit
st.set_page_config(
    page_title="Température extrême à La Réunion",
    page_icon="☀️",
    layout="wide"
)

st.title("☀️ Analyse des Jours de Forte Chaleur à La Réunion")

# --- Initialisation du client BigQuery ---
client = bigquery.Client()

# --- Requête SQL ---
# La requête SQL reste inchangée, elle récupère toutes les données annuelles agrégées par zone.
query = """
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
"""

# --- Fonction de chargement des données (avec cache) ---
@st.cache_data
def load_data():
    df = client.query(query).to_dataframe()
    # Conversion de l'année en datetime pour la série temporelle
    df['ANNEE_DATE'] = pd.to_datetime(df['ANNEE'], format='%Y')
    # Conversion de l'année en numérique/int pour le curseur
    df['ANNEE'] = pd.to_numeric(df['ANNEE'])
    return df

try:
    # 1. Chargement des données
    data_temp = load_data()
    
    # 2. Préparation du DataFrame pour l'interface
    min_annee = int(data_temp['ANNEE'].min())
    max_annee = int(data_temp['ANNEE'].max())

    # 3. Barre latérale et Filtres Interactifs
    # --------------------------------------------------------------------------
    st.sidebar.header("Filtres d'Analyse")
    
    # --- NOUVEAU CURSEUR D'ANNÉE ---
    annee_selectionnee = st.sidebar.slider(
        "Sélectionnez une Année d'Analyse :", 
        min_value=min_annee, 
        max_value=max_annee, 
        value=max_annee, # Année par défaut : la plus récente
        step=1
    )
    
    # Sélecteur de zone climatique
    zones_uniques = ['Toutes les zones'] + sorted(data_temp['Z_CLIM'].unique().tolist())
    zone_selectionnee = st.sidebar.selectbox(
        "Sélectionnez une Zone Climatique :", 
        zones_uniques
    )
    
    # 4. Filtrage des DataFrames
    # --------------------------------------------------------------------------
    
    # DataFrame pour la Série Temporelle (filtré uniquement par Z_CLIM)
    if zone_selectionnee != 'Toutes les zones':
        df_serie_temporelle = data_temp[data_temp['Z_CLIM'] == zone_selectionnee]
    else:
        df_serie_temporelle = data_temp.copy()
        
    # DataFrame pour les KPI et l'Analyse Annuelle (filtré par Z_CLIM et ANNEE)
    df_annee_filtree = df_serie_temporelle[df_serie_temporelle['ANNEE'] == annee_selectionnee]

    # --- Indicateurs de Performance (KPI) ---
    st.subheader(f"Indicateurs Clés pour l'Année {annee_selectionnee} 🌡️")
    col1, col2, col3 = st.columns(3)

    # 1. Moyenne pour l'Année et la Zone sélectionnée
    if not df_annee_filtree.empty:
        jours_annee = df_annee_filtree['moyenne_jours_chauds_zone'].mean()
        
        # Calcul de la variation par rapport à la moyenne de la zone sur toute la période
        moyenne_historique_zone = df_serie_temporelle['moyenne_jours_chauds_zone'].mean()
        delta_annee = jours_annee - moyenne_historique_zone
        
        col1.metric(
            f"Moyenne Jours Chauds en {annee_selectionnee} (Zone Filtrée)",
            f"{jours_annee:.1f} jours/an",
            delta=f"{delta_annee:.1f} par rapport à la moyenne historique"
        )
    else:
        col1.info("Aucune donnée disponible pour cette sélection.")


    # 2. Moyenne globale de l'année sélectionnée (toutes zones confondues)
    moyenne_globale_annee = data_temp[data_temp['ANNEE'] == annee_selectionnee]['moyenne_jours_chauds_zone'].mean()
    col2.metric(
        f"Moyenne Année {annee_selectionnee} (Global)", 
        f"{moyenne_globale_annee:.1f} jours/an",
        delta_color="off"
    )
    
    # --- Visualisation Principale : Série Temporelle ---
    st.subheader("Série Temporelle : Évolution des Jours de Forte Chaleur (1950-2024)")
    
    # Création du graphique en lignes
    chart_line = alt.Chart(df_serie_temporelle).mark_line().encode(
        # Utilisation de :T pour Temporel
        x=alt.X('ANNEE_DATE:T', title='Année'),
        y=alt.Y('moyenne_jours_chauds_zone:Q', title='Moyenne Jours > 32°C'),
        color='Z_CLIM:N', 
        tooltip=[
            alt.Tooltip('ANNEE_DATE:T', title='Année', format='%Y'), 
            'Z_CLIM', 
            alt.Tooltip('moyenne_jours_chauds_zone:Q', format='.1f', title='Jours Chauds')
        ]
    ).properties(
        title=f'Tendance des Jours de Chaleur Extrême pour {zone_selectionnee}'
    ).interactive()

    st.altair_chart(chart_line, use_container_width=True)
    
    # --- Visualisation Secondaire : Comparaison des Zones (Barres) ---
    st.subheader("Comparaison : Jours Chauds Moyens par Zone (Toute la Période)")
    
    # Calcul de la moyenne sur toute la période pour chaque zone
    df_comparaison = data_temp.groupby('Z_CLIM')['moyenne_jours_chauds_zone'].mean().reset_index()
    df_comparaison.columns = ['Z_CLIM', 'T_moyenne_periode']

    chart_bar = alt.Chart(df_comparaison).mark_bar().encode(
        x=alt.X('T_moyenne_periode:Q', title='Moyenne Jours > 32°C (Période Totale)'),
        y=alt.Y('Z_CLIM:N', sort='-x', title='Zone Climatique'),
        color=alt.Color('Z_CLIM:N', legend=None),
        tooltip=['Z_CLIM', alt.Tooltip('T_moyenne_periode:Q', format='.1f', title='Moyenne Jours Chauds')]
    ).properties(
        title='Zones les plus exposées à la chaleur extrême (Moyenne 1950-2024)'
    ).interactive()

    st.altair_chart(chart_bar, use_container_width=True)

    # 4. Affichage du DataFrame
    st.subheader(f"Aperçu des Données Filtrées (Année {annee_selectionnee})")
    st.dataframe(df_annee_filtree)


except Exception as e:
    st.error(f"Une erreur s'est produite : {e}")
    st.warning("Vérifiez la connexion à BigQuery (credentials) et la structure des colonnes dans la requête SQL.")