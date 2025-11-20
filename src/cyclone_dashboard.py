import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.oauth2 import service_account
import os
from streamlit_option_menu import option_menu




# Configuration de la page
st.set_page_config(
    page_title="Projet CC",
    page_icon="🌀",
    layout="wide"
)

# Titre principal
st.title("Overview ")
st.markdown("### Détection et analyse des événements cycloniques basés sur les précipitations extrêmes")

# Initialiser la connexion BigQuery avec SQLAlchemy
@st.cache_resource
def get_engine():
    # Chemin vers le fichier de credentials
    credentials_path = os.path.join(os.path.dirname(__file__), '..', 'secrets', 'cc-reunion-4e33fbae13a2.json')
    
    # Créer l'URL de connexion SQLAlchemy pour BigQuery
    project_id = 'cc-reunion'
    connection_string = f'bigquery://{project_id}'
    
    # Créer l'engine avec les credentials
    engine = create_engine(
    "bigquery://cc-reunion",
    credentials_path="/home/marc0/code/Jassat/projet-cc/secrets/cc-reunion-4e33fbae13a2.json"
)
    return engine

engine = get_engine()

# Requête SQL pour la détection des cyclones
query = """
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
"""

# Exécuter la requête et récupérer les données
@st.cache_data
def load_data():
    with st.spinner('Chargement des données...'):
        df = pd.read_sql(query, engine)
    return df

df_full = load_data()

# Filtres interactifs
st.sidebar.header("🎛️ Filtres")

# Filtre par plage d'années
annees_disponibles = sorted(df_full['annee'].unique())
annee_min, annee_max = st.sidebar.slider(
    "Période d'analyse",
    min_value=int(min(annees_disponibles)),
    max_value=int(max(annees_disponibles)),
    value=(int(min(annees_disponibles)), int(max(annees_disponibles)))
)

# Filtre par mois
mois_labels = {
    1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril', 5: 'Mai', 6: 'Juin',
    7: 'Juillet', 8: 'Août', 9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
}
# dropdown multiselect avec checkbox pour le choix des mois
mois_selectionnes = st.sidebar.multiselect(
    "Choix du mois", list(mois_labels.values()),
    #options=list(mois_labels.keys()),
    #value=list(mois_labels.keys()),
    #format_func=lambda x: mois_labels[x],
)

# Filtre par intensité (nombre de jours >100mm)
min_jours = st.sidebar.number_input(
    "Nombre minimum de jours >100mm",
    min_value=1.0,
    max_value=float(df_full['Nb_Jours_Sup_100mm'].max()),
    value=1.0,
    step=0.5
)

# Appliquer les filtres
df = df_full[
    (df_full['annee'] >= annee_min) & 
    (df_full['annee'] <= annee_max) &
    (df_full['mois'].isin(mois_selectionnes)) &
    (df_full['Nb_Jours_Sup_100mm'] >= min_jours)
].copy()

# Afficher quelques statistiques clés
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total d'événements détectés", len(df))

with col2:
    st.metric("Année la plus touchée", df.groupby('annee').size().idxmax() if len(df) > 0 else "N/A")

with col3:
    max_pluie = df['Cumul_Mensuel_Pluie_Total'].max() if len(df) > 0 else 0
    st.metric("Cumul mensuel max (mm)", f"{max_pluie:.1f}")

with col4:
    max_jours = df['Nb_Jours_Sup_100mm'].max() if len(df) > 0 else 0
    st.metric("Max jours >100mm/mois", f"{max_jours:.1f}")

st.markdown("---")

# Section 1: Tableau des données
st.subheader("📊 Événements cycloniques détectés (jours avec >100mm de pluie)")
st.dataframe(
    df.style.format({
        'Cumul_Mensuel_Pluie_Total': '{:.2f}',
        'Cumul_MAxi_par_mois': '{:.2f}',
        'Nb_Jours_Sup_100mm': '{:.2f}'
    }),
    use_container_width=True
)

# Section 2: Graphiques
st.markdown("---")
st.subheader("📈 Visualisations")

# Graphique 1: Évolution temporelle des événements cycloniques
fig1 = px.scatter(
    df,
    x='date_key',
    y='Nb_Jours_Sup_100mm',
    size='Cumul_Mensuel_Pluie_Total',
    color='Cumul_MAxi_par_mois',
    hover_data=['annee', 'mois', 'Cumul_Mensuel_Pluie_Total', 'Cumul_MAxi_par_mois'],
    title="Évolution des événements cycloniques dans le temps",
    labels={
        'date_key': 'Date',
        'Nb_Jours_Sup_100mm': 'Nombre de jours avec >100mm',
        'Cumul_Mensuel_Pluie_Total': 'Cumul mensuel (mm)',
        'Cumul_MAxi_par_mois': 'Précipitation max 24h (mm)'
    },
    color_continuous_scale='Blues'
)
fig1.update_layout(height=500)
st.plotly_chart(fig1, use_container_width=True)

# Graphique 2: Distribution par année
st.subheader("Distribution annuelle des événements")
events_per_year = df.groupby('annee').size().reset_index(name='nombre_evenements')
fig2 = px.bar(
    events_per_year,
    x='annee',
    y='nombre_evenements',
    title="Nombre d'événements cycloniques par année",
    labels={
        'annee': 'Année',
        'nombre_evenements': "Nombre d'événements"
    },
    color='nombre_evenements',
    color_continuous_scale='Reds'
)
fig2.update_layout(height=400)
st.plotly_chart(fig2, use_container_width=True)

# Graphique 3: Distribution par mois
st.subheader("Saisonnalité des cyclones")
events_per_month = df.groupby('mois').size().reset_index(name='nombre_evenements')
mois_labels = {1: 'Jan', 2: 'Fév', 3: 'Mar', 4: 'Avr', 5: 'Mai', 6: 'Jun',
               7: 'Jul', 8: 'Aoû', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Déc'}
events_per_month['mois_label'] = events_per_month['mois'].map(mois_labels)

fig3 = px.bar(
    events_per_month,
    x='mois_label',
    y='nombre_evenements',
    title="Distribution mensuelle des événements cycloniques",
    labels={
        'mois_label': 'Mois',
        'nombre_evenements': "Nombre d'événements"
    },
    color='nombre_evenements',
    color_continuous_scale='Teal'
)
fig3.update_layout(height=400)
st.plotly_chart(fig3, use_container_width=True)

# Section 4: Événements les plus intenses
st.markdown("---")
st.subheader("🌊 Top 10 des événements les plus intenses")
top_events = df.nlargest(10, 'Cumul_Mensuel_Pluie_Total')[
    ['annee', 'mois', 'Cumul_Mensuel_Pluie_Total', 'Cumul_MAxi_par_mois', 'Nb_Jours_Sup_100mm']
]
st.dataframe(
    top_events.style.format({
        'Cumul_Mensuel_Pluie_Total': '{:.2f}',
        'Cumul_MAxi_par_mois': '{:.2f}',
        'Nb_Jours_Sup_100mm': '{:.2f}'
    }),
    use_container_width=True
)

# Footer
st.markdown("---")
st.markdown("*Données: Météo France - Critère de détection: Mois avec plus de 1 jour de précipitations >100mm*")
