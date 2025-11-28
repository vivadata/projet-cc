import streamlit as st
import plotly.express as px
import geojson
from pathlib import Path
from config.constants import get_coordonnees_reunion, get_couleurs_zones
from data_layer.bigquery import get_table
import folium
from streamlit_folium import st_folium


st.set_page_config(
    page_title="Climat de La Réunion",
    page_icon="🌧️",
    layout="wide"
)

st.title("🏝️ Le climat à La Réunion")


# ----------------------------------------------------
# CONFIGURATION DE LA CARTE
# ----------------------------------------------------

# Fonction de style pour les zones climatiques
def style_function(feature):
    zone = feature['properties'].get('Zone')
    couleurs = get_couleurs_zones()
    return {
        "fillColor": couleurs.get(zone, "#808080"),
        "color": couleurs.get(zone, "#000000"),
        "weight": 2,
        "fillOpacity": 0.4,
    }

# Fonction de surlignage au survol
def highlight_function(feature):
    return {
        "weight": 4,
        "color": "yellow",
        "fillOpacity": 0.7,
    }


# __file__ = chemin du fichier Python courant
BASE_DIR = Path(__file__).resolve().parent
filepath = BASE_DIR / "zones_climatiques.geojson"

with open(filepath, 'r', encoding='utf-8') as file:
    geojson_data = geojson.load(file)

# Division de la page en deux colonnes
col1, col2 = st.columns([1, 2]) # 1/3 pour la carte, 2/3 pour les graphiques

# ----------------------------------------------------
# A. PREMIÈRE COLONNE : CARTE DE LA RÉUNION AVEC LES MICRO-CLIMATS
# ----------------------------------------------------

with col1:
    st.subheader("Carte des micro-climats")
    st.markdown(":orange-badge[Côte sous le vent (SV_C)] :red-badge[Côte au vent (AV_C)]")
    st.markdown(":blue-badge[Hauts sous le vent (SV_H)] :green-badge[Hauts au vent (AV_H)]")

    # Création de la carte Folium centrée sur La Réunion
    m = folium.Map(location=get_coordonnees_reunion(), zoom_start=9)

    # Ajout du GeoJSON
    folium.GeoJson(
        geojson_data,
        name="Zones climatiques",
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=["Zone"],
            aliases=["Micro-climat:"]
        )
    ).add_to(m)

    # Affichage de la carte dans Streamlit
    # `use_container_width=True`` est essentiel pour que la carte puisse s'afficher correctement
    # en s'adaptant à la largeur de la colonne
    st_folium(m, use_container_width=True, height=400)



# ----------------------------------------------------
# B. DEUXIÈME COLONNE : GRAPHIQUES DE SÉRIES TEMPORELLES
# ----------------------------------------------------
df_data = get_table(tab_name = 'cc-reunion.data_meteofrance.histo_simu_geo')
df_data = df_data[df_data.year <= 2025]
df_data = df_data.sort_values(by='year', ascending=True)

with col2:
    st.subheader("Variations annuelles de 1953 à nos jours")
    height = 400
    
    # --- 1. GRAPHIQUE DES TEMPÉRATURES MOYENNES (TMM) ---
    
    fig_tmm = px.line(
        df_data,
        x='year',
        y='TMM',
        color='Z_GEO',
        title="Température Moyenne Annuelle (TMM) par micro-climat",
        labels={'TMM': 'TMM (°C)', 'year': 'Année','Z_GEO' : 'micro-climat'},
        color_discrete_map=get_couleurs_zones(),
        template='plotly_white'
    )
    fig_tmm.update_layout(height=height)
    st.plotly_chart(fig_tmm, use_container_width=True)

    # --- 2. GRAPHIQUE DES PRÉCIPITATIONS ANNUELLES ---
    
    fig_precip = px.line(
        df_data,
        x='year',
        y='RRMX',
        color='Z_GEO',
        title = "Hauteur moyenne de Précipitations Annuelle (RRM) par micro-climat",
        labels={'RRMX': 'RRM (mm)', 'year': 'Année','Z_GEO' : 'micro-climat'},
        color_discrete_map=get_couleurs_zones(),
        template='plotly_white'
    )
    fig_precip.update_layout(height=height)
    st.plotly_chart(fig_precip, use_container_width=True)
