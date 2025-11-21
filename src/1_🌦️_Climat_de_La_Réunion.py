import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import numpy as np
import geojson

from data_layer.bigquery import get_table

st.set_page_config(
    page_title="Climat de La Réunion",
    page_icon="🌧️",
    layout="wide"
)

st.title("🏝️ Le climat à La Réunion")

# Division de la page en deux colonnes
col1, col2 = st.columns([1, 2]) # 1/3 pour la carte, 2/3 pour les graphiques

COULEURS_ZONES = {
    'AV_H': '#009E73', 
    'SV_H': '#0072B2',
    'AV_C': '#D55E00',
    'SV_C': '#F0E442'
}
# Conversion approximative des noms de couleurs CSS en RGB :
COLOR_MAP_EXPRESSION = """
    properties.Zone === 'AV_H' ? [0, 158, 115, 150] :
    properties.Zone === 'SV_H' ? [0, 114, 178, 150] :
    properties.Zone === 'AV_C' ? [213, 94, 0, 150] :
    [240, 228, 66, 150]
"""


# ----------------------------------------------------
# A. PREMIÈRE COLONNE : CARTE DE LA RÉUNION (pydeck)
# ----------------------------------------------------

with col1:
    st.subheader("Carte des micro-climats")
    st.markdown(":orange-badge[Côte sous le vent (SV_C)] :red-badge[Côte au vent (AV_C)]")
    st.markdown(":blue-badge[Hauts sous le vent (SV_H)] :green-badge[Hauts au vent (AV_H)]")

    # Coordonnées centrales de La Réunion, approximativement
    LATITUDE = -21.1076
    LONGITUDE = 55.5361

    # Configuration de la vue de la carte
    view_state = pdk.ViewState(
        latitude=LATITUDE,
        longitude=LONGITUDE,
        zoom=8.8,
        pitch=0 # angle de vue
    )

    # Couche GeoJSON pour afficher les polygones
    filepath = '/home/chloe_radice/code/chloe-radice/projet-cc/src/zones_climatiques.geojson'
    with open(filepath, 'r') as file:
        geojson_data = geojson.load(file)

    geojson_layer = pdk.Layer(
        'GeoJsonLayer',
        geojson_data,
        opacity=0.4,
        stroked=True,
        filled=True,
        extruded=False,
        # Utilisation de la NOUVELLE expression de mapping de couleur
        #get_fill_color= COLOR_MAP_EXPRESSION,
        get_fill_color= [0, 128, 128, 60],
        get_line_color=[0, 128, 128, 200],
        line_width_min_pixels=1,
        pickable=True,
        auto_highlight=True
    )
    
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=view_state,
        layers=[geojson_layer],
    # NOUVEL AJOUT : Configuration du tooltip
        # L'objet {Zone} fait référence à la propriété "Zone" du GeoJSON feature
        tooltip={
            "html": "<b>Micro-climat :</b> {Zone}",
            "style": {
                "backgroundColor": "white",
                "color": "steelblue"
            }
        }
    ))

# ----------------------------------------------------
# B. DEUXIÈME COLONNE : GRAPHIQUES DE SÉRIES TEMPORELLES
# ----------------------------------------------------
df_data = get_table(tab_name = 'cc-reunion.data_meteofrance.histo_simu_geo')
#df_data = df_data[df_data.year <= 2025]
df_data = df_data.sort_values(by='year', ascending=True)

with col2:
    st.subheader("Variations annuelles de 1953 à nos jours et projections")
    
    # --- 1. GRAPHIQUE DES TEMPÉRATURES MOYENNES (TMM) ---
    
    fig_tmm = px.line(
        df_data,
        x='year',
        y='TMM',
        color='Z_GEO',
        title="Température Moyenne Annuelle (TMM) par micro-climat",
        labels={'TMM': 'TMM (°C)', 'year': 'Année','Z_GEO' : 'micro-climat'},
        color_discrete_map=COULEURS_ZONES,
        template='plotly_white'
    )
    fig_tmm.update_layout(height=300)
    st.plotly_chart(fig_tmm, use_container_width=True)

    # --- 2. GRAPHIQUE DES PRÉCIPITATIONS ANNUELLES ---
    
    fig_precip = px.line(
        df_data,
        x='year',
        y='RRMX',
        color='Z_GEO',
        title = "Hauteur moyenne de Précipitations Annuelle (RRM) par micro-climat",
        labels={'RRMX': 'RRM (mm)', 'year': 'Année','Z_GEO' : 'micro-climat'},
        color_discrete_map=COULEURS_ZONES,
        template='plotly_white'
    )
    fig_precip.update_layout(height=300)
    st.plotly_chart(fig_precip, use_container_width=True)
