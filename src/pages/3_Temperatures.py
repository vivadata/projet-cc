import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from data_layer.bigquery import get_nb_moy_nuits_sup_20deg_par_zone_par_annee


st.set_page_config(
    page_title="Évolution des nuits ≥ 20°C par zone géographique",
    page_icon="",
    layout="wide"
)




# ------------------------------
# 1. Plotly : line chart multi-zones
# ------------------------------
# df : ANNEE, zone_geographique, moy_nuits_ge_20, (nb_stations)
df = get_nb_moy_nuits_sup_20deg_par_zone_par_annee()
# Data before 1983 is incomplete
df = df[df["ANNEE"] >= 1983]



# ------------------------------
# 3. Scatter plot avec trendline
# ------------------------------
st.title("Nuits ≥ 20°C — Évolution par zone géographique")

# Définition des groupes
groupes = {
    "Zones chaudes (AV_C + SSV_C)": ["AV_C", "SSV_C"],
    "Zones hautes (AV_H + SSV_H)": ["AV_H", "SSV_H"]
}

# Fonction utilitaire pour calculer une tendance avec numpy
def calcule_tendance(df, group_label):
    df_group = df[df["zone_geographique"].isin(groupes[group_label])]
    
    df_tendance = (
        df_group.groupby("ANNEE", as_index=False)["moy_nuits_ge_20"]
        .mean()
        .sort_values("ANNEE")
    )
    
    x = df_tendance["ANNEE"].values
    y = df_tendance["moy_nuits_ge_20"].values
    
    if len(x) > 1:
        coef = np.polyfit(x, y, 1)
        trend = np.poly1d(coef)
        df_tendance["trend"] = trend(x)
        return df_tendance
    else:
        return None

# Prépare les deux tendances
tendance_chaude = calcule_tendance(df, "Zones chaudes (AV_C + SSV_C)")
tendance_haute = calcule_tendance(df, "Zones hautes (AV_H + SSV_H)")

# Construction du graphique
fig = go.Figure()

# 1) Courbes par zone
for zone in df["zone_geographique"].unique():
    df_zone = df[df["zone_geographique"] == zone].sort_values("ANNEE")
    
    fig.add_trace(go.Scatter(
        x=df_zone["ANNEE"],
        y=df_zone["moy_nuits_ge_20"],
        mode="lines+markers",
        name=f"{zone}",
        opacity=0.7
    ))

# 2) Courbe de tendance zones chaudes
if tendance_chaude is not None:
    fig.add_trace(go.Scatter(
        x=tendance_chaude["ANNEE"],
        y=tendance_chaude["trend"],
        mode="lines",
        name="Tendance zones chaudes",
        line=dict(width=4, dash="dash")
    ))

# 3) Courbe de tendance zones hautes
if tendance_haute is not None:
    fig.add_trace(go.Scatter(
        x=tendance_haute["ANNEE"],
        y=tendance_haute["trend"],
        mode="lines",
        name="Tendance zones hautes",
        line=dict(width=4, dash="dot")
    ))

fig.update_layout(
    title="Moyenne des nuits ≥ 20°C par zone géographique",
    xaxis_title="Année",
    yaxis_title="Nuits ≥ 20°C (moyenne)",
    legend_title="Zones",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)






# ------------------------------
# 2. Ecarts à la moyenne par groupe de zones
# ------------------------------
# --- Définition des groupes ---
groupes = {
    "Zones côtières (AV_C + SSV_C)": ["AV_C", "SSV_C"],
    "Zones montagneuses (AV_H + SSV_H)": ["AV_H", "SSV_H"]
}

df["groupe"] = df["zone_geographique"].apply(
    lambda z: "Zones côtières" if z in ["AV_C", "SSV_C"] else "Zones montagneuses"
)

df_plot = df.copy()
df_plot["moy_groupe"] = df_plot.groupby("groupe")["moy_nuits_ge_20"].transform("mean")
df_plot["ecart_moy"] = df_plot["moy_nuits_ge_20"] - df_plot["moy_groupe"]
df_plot["couleur"] = df_plot["ecart_moy"].apply(lambda x: "red" if x > 0 else "blue")







# Création de la colonne couleur pour le graphique
df_plot["couleur"] = df_plot["ecart_moy"].apply(lambda x: "Chaud" if x > 0 else "Froid")

# Définir explicitement les couleurs via color_discrete_map
color_map = {"Chaud": "red", "Froid": "blue"}

fig = px.bar(
    df_plot,
    x="ANNEE",
    y="ecart_moy",
    color="couleur",      # maintenant contient "Chaud"/"Froid"
    facet_col="groupe",
    color_discrete_map=color_map,
    labels={"ecart_moy": "Écart à la moyenne", "ANNEE": "Année"},
    title="Écarts du nombre moyen de nuits ≥20°C par groupe"
)

fig.add_hline(y=0, line_dash="dash", line_color="black")
st.plotly_chart(fig, use_container_width=True)
