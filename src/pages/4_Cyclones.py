import streamlit as st
import plotly.express as px
import pandas as pd
from config.constants import data_sinistres_cyclone, get_mois_labels
import re
from data_layer.bigquery import get_detection_precip_superieure100mm


# Exécuter la requête et récupérer le dataframe
df_pie_chart = get_detection_precip_superieure100mm()


# Configuration de la page
st.set_page_config(
    page_title="Projet CC",
    page_icon="🌀",
    layout="wide"
)

# Titre principal
st.title("Précipitations")
st.markdown("### Détection et analyse des événements cycloniques basés sur les précipitations extrêmes")


# Filtres interactifs
# st.sidebar.header("🎛️ Filtres")

# Filtre par plage d'années
# annees_disponibles = sorted(df_pie_chart_full['annee'].unique())
# annee_min, annee_max = st.sidebar.slider(
#     "Période d'analyse",
#     min_value=int(min(annees_disponibles)),
#     max_value=int(max(annees_disponibles)),
#     value=(int(min(annees_disponibles)), int(max(annees_disponibles)))
# )

# Filtre par mois


# dropdown multiselect avec checkbox pour le choix des mois
# mois_selectionnes = st.sidebar.multiselect(
#     "Choix du mois",
#     list(get_mois_labels().values()),
#     default=list(get_mois_labels().values()) # sélectionner de tous les mois par défaut
# )

# Filtre par intensité (nombre de jours >100mm)
# min_jours = st.sidebar.number_input(
#     "Nombre minimum de jours >100mm",
#     min_value=1.0,
#     max_value=float(df_pie_chart_full['Nb_Jours_Sup_100mm'].max()),
#     value=1.0,
#     step=0.5
# )

# Appliquer les filtres
# df_pie_chart = df_pie_chart_full[
#     (df_pie_chart_full['annee'] >= annee_min) & 
#     (df_pie_chart_full['annee'] <= annee_max) &
#     (df_pie_chart_full['mois'].isin(mois_selectionnes)) &
#     (df_pie_chart_full['Nb_Jours_Sup_100mm'] >= min_jours)
# ].copy()

# Afficher quelques statistiques clés
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total d'événements détectés", len(df_pie_chart))

with col2:
    st.metric("Année la plus touchée", df_pie_chart.groupby('annee').size().idxmax() if len(df_pie_chart) > 0 else "N/A")

with col3:
    max_pluie = df_pie_chart['Cumul_Mensuel_Pluie_Total'].max() if len(df_pie_chart) > 0 else 0
    st.metric("Cumul mensuel max (mm)", f"{max_pluie:.1f}")

with col4:
    max_jours = df_pie_chart['Nb_Jours_Sup_100mm'].max() if len(df_pie_chart) > 0 else 0
    st.metric("Max jours >100mm/mois", f"{max_jours:.1f}")

st.markdown("---")

# Section 1: Tableau des données
st.subheader("📊 Événements cycloniques détectés (jours avec >100mm de pluie)")
st.dataframe(
    df_pie_chart.style.format({
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
    df_pie_chart,
    x='date_key',
    y='Nb_Jours_Sup_100mm',
    size='Cumul_Mensuel_Pluie_Total',
    color='Cumul_MAxi_par_mois',
    hover_data=['annee', 'mois', 'Cumul_Mensuel_Pluie_Total', 'Cumul_MAxi_par_mois'],
    title="Nombre de jours avec cumul de précipitation >100mm  par mois",
    subtitle="Bulle = Intensité mensuelle des précipitations",
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
events_per_year = df_pie_chart.groupby('annee').size().reset_index(name='nombre_evenements')
fig2 = px.bar(
    events_per_year,
    x='annee',
    y='nombre_evenements',
    title="Nombre de jour réunissant des conditions cycloniques par année",
    labels={
        'annee': 'Année',
        'nombre_evenements': "Nombre d'événements"
    },
    color='nombre_evenements',
    color_continuous_scale='Reds'
)
fig2.update_layout(height=400)
st.plotly_chart(fig2, use_container_width=True)


# Section 4: Événements les plus intenses
st.markdown("---")
st.subheader("🌊 Top 10 des événements les plus intenses")
top_events = df_pie_chart.nlargest(10, 'Cumul_Mensuel_Pluie_Total')[
    ['annee', 'mois', 'Cumul_Mensuel_Pluie_Total', 'Cumul_MAxi_par_mois', 'Nb_Jours_Sup_100mm']
]
st.dataframe(
    top_events.style.format({
        'Cumul_Mensuel_Pluie_Total': '{:.2f}',
        'Cumul_MAxi_par_mois': '{:.2f}',
        'Nb_Jours_Sup_100mm': '{:.2f}'
    }),
    use_container_width=True,
    column_config= {
        'annee' : 'Année',
        'mois' : 'Mois',
        'Cumul_Mensuel_Pluie_Total' : 'Cumul Mensuel de pluie',
        'Cumul_MAxi_par_mois' : 'Cumul Maxi par jour',
        'Nb_Jours_Sup_100mm' : 'Nombre de jour > 100mm',
    },
)

# Footer
st.markdown("---")
st.markdown("*Données: Météo France - Critère de détection: Mois avec plus de 1 jour de précipitations >100mm*")

# # --------------------------
# # Figure scater pour voir les données : Cyclones et pluies extrêmes
# # --------------------------

# # 1. Récupération des données
# df_pie_chart_pluie_extreme = get_table_pluie_extreme()

# # 2. Convertir AAAAMM en format Date/Année pour un axe X correct
# df_pie_chart_pluie_extreme['year'] = pd.to_datetime(df_pie_chart_pluie_extreme['year'], format='%Y')

# # 3. Définition de la carte de couleurs
# # Les couleurs doivent correspondre aux valeurs définies dans la clause CASE WHEN
# color_map = {
#     'Normal': 'blue', 
#     'Tempête': 'yellow',
#     'Tempête Violente': 'orange',
#     'Cyclone': 'red'
# }

# # 4. Création du graphique
# df_pie_chart_pluie_extreme_long = pd.melt(df_pie_chart_pluie_extreme, 
#                                 id_vars=['year', 'Statut_Cyclone_Majeur', 'Statut_Alerte_Vent', 'Forte_pluviometrie'], 
#                                 value_vars=['NBJFXI3S16X', 'RRMX'],
#                                 var_name='Métrique', 
#                                 value_name='Valeur')

# fig = px.scatter(
#     df_pie_chart_pluie_extreme_long,
#     x='year',
#     y='Valeur',
#     color='Statut_Alerte_Vent',  # La couleur est déterminée par le statut d'alerte en fonction de la vitesse du vent
#     symbol='Métrique',      # Utilise un symbole différent pour distinguer FXIAB et RR
#     color_discrete_map=color_map,
#     title='Événements de Pluviométrie (RRMX) et Vent (NBJFXI3S16X) avec Seuils d\'Alerte',
#     labels={
#         'year': 'Date (Année)', 
#         'Valeur': 'Mesure (NBJFXI3S16X / RRMX)', 
#         'Statut_Alerte': 'Niveau d\'Alerte'
#     }
# )

# # Améliorations de lisibilité (optionnel)
# fig.update_traces(marker=dict(size=8, opacity=0.8))
# fig.update_layout(xaxis_title="Date", yaxis_title="Valeur de la Métrique")

# st.plotly_chart(fig)



# --------------------------
# Création de 3 pie charts pour la répartition des cyclones selon les périodes
# 1 - 1952-1995
# 2 - 1996-2025
# 3 - 2026-2100 (hypothétique)
# --------------------------

def creer_pie_chart_periode(df_pie_chart, annee_debut, annee_fin, titre):
    """
    Filtre le DataFrame, compte les statuts d'alerte et crée le graphique.
    """
    
    # 1. Filtrage du DataFrame pour la période demandée
    # On filtre les valeurs 'Normal' car le graphique ne doit montrer que les événements extrêmes
    df_pie_chart_filtre = df_pie_chart[
        (df_pie_chart['AAAAMM_int'] >= annee_debut * 100) & 
        (df_pie_chart['AAAAMM_int'] <= annee_fin * 12) & 
        (df_pie_chart['Statut_Alerte'] != 'Normal')
    ].copy()
    
    # 2. Agrégation : Compter le nombre d'occurrences pour chaque Statut_Alerte
    df_pie_chart_compte = df_pie_chart_filtre['Statut_Alerte'].value_counts().reset_index()
    df_pie_chart_compte.columns = ['Statut_Alerte', 'Nombre_Evenements']

    # 3. Définition des couleurs pour la cohérence
    color_map = {
        'Tempête': 'yellow',
        'Tempête Violente': 'orange',
        'Cyclone': 'red'
    }

    # 4. Création du Pie Chart
    fig_pie = px.pie(
        df_pie_chart_compte,
        values='Nombre_Evenements',
        names='Statut_Alerte',
        title=f'Répartition des événements extrêmes : {titre}',
        color='Statut_Alerte',
        color_discrete_map=color_map
    )
    
    # Rendre l'anneau pour une meilleure lisibilité (Donut Chart)
    fig_pie.update_traces(textposition='inside', textinfo='percent+label', hole=.4)
    
    st.plotly_chart(fig_pie)

# --------------------------
# Exécution pour les périodes 1 et 2
# --------------------------
# TODO
# 1 - Répartition entre 1952 et 1995
# fig_pie_1 = creer_pie_chart_periode(df_pie_chart, 1952, 1995, 'Période 1952 - 1995')
# st.plotly_chart(fig_pie_1)

# # 2 - Répartition entre 1996 et 2025
# fig_pie_2 = creer_pie_chart_periode(df_pie_chart, 1996, 2025, 'Période 1996 - 2025')
# st.plotly_chart(fig_pie_2)


# --------------------------
# Exécution pour la période 3 (Hypothétique/Projection)
# --------------------------

# 3 - Répartition entre 2026 et 2100
# IMPORTANT : Mise à jour des données pour prendre en compte la simulation/projection
# fig3 = px.pie(
#     df_pie_chart,
#     values='Nombre_Evenements',
#     names='Statut_Alerte',
#     title='Répartition des événements extrêmes : Période de Projection (2026 - 2100) - SIMULÉ',
#     color='Statut_Alerte',
#     color_discrete_map={
#         'Tempête': 'yellow',
#         'Tempête Violente': 'orange',
#         'Cyclone': 'red'
#     }
# )
# fig3.update_traces(textposition='inside', textinfo='percent+label', hole=.4)
# fig3.show()

# --------------------------
# Création d'un tableau pour le top 5 des évènement les plus couteux 
# --------------------------


def get_top_5_degats_cyclone():


    df = pd.DataFrame(data_sinistres_cyclone)

    # 1. Normalisation et extraction du coût principal en M€ (Millions d'euros)
    def extract_cost(cost_str):
        # Utilise une regex pour trouver le premier nombre suivi de 'M€'
        match = re.search(r'([\d,\.>~]+)\s*M€', cost_str)
        if match:
            # Nettoie la chaîne pour garder uniquement le nombre (retire les > et ~)
            value = match.group(1).replace('>', '').replace('~', '').replace(',', '.')
            return float(value)
        return 0.0 # Retourne 0.0 si le coût n'est pas trouvé ou non-M€

    df['Cout_M_Euros'] = df['Coût estimé'].apply(extract_cost)

    # 2. Tri par le coût le plus élevé
    df_sorted = df.sort_values(by='Cout_M_Euros', ascending=False)

    # 3. Sélection du Top 5 et des colonnes finales
    df_top5 = df_sorted.head(5)
    
    # Création de la colonne finale du coût formaté (en conservant les détails de l'estimation)
    df_top5['Coût'] = df_top5['Coût estimé']

    # Sélection des colonnes demandées
    result_table = df_top5[['Date', 'Évènement', 'Coût']]
    
    # Renommer les colonnes pour la présentation
    result_table = result_table.rename(columns={'Évènement': 'Événement'})

    return result_table

# Appel de la fonction pour obtenir le tableau final
df_final = get_top_5_degats_cyclone()
print(df_final) # Décommentez pour vérifier le résultat dans un environnement standard
