import streamlit as st
import plotly.express as px
import pandas as pd
from data_layer.bigquery import get_nb_moy_nuits_sup_20deg_par_zone_par_annee

st.set_page_config(
    page_title="Évolution des nuits ≥ 20°C par zone géographique",
    page_icon="",
    layout="wide"
)

st.title("Évolution des nuits ≥ 20°C par zone géographique")


# ------------------------------
# 2. Plotly : line chart multi-zones
# ------------------------------
df = get_nb_moy_nuits_sup_20deg_par_zone_par_annee()
# Data before 1983 is incomplete
df = df[df["ANNEE"] >= 1983]


# st.write("### Aperçu des données")
# st.dataframe(df)
fig = px.line(
    df,
    x="ANNEE",
    y="moy_nuits_ge_20",
    color="zone_geographique",
    markers=True,
    title="Moyenne du nombre de nuits ≥ 20°C par zone géographique",
)

fig.update_layout(
    xaxis_title="Année",
    yaxis_title="Nuits ≥ 20°C (moyenne par station)",
    legend_title="Zone géographique",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)




# ------------------------------
# 3. Scatter plot avec trendline
# ------------------------------
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.title("Nuits ≥ 20°C — Évolution par zone géographique")

# df contient : ANNEE, zone_geographique, moy_nuits_ge_20, (nb_stations)

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







# --- Définition des groupes ---
groupes = {
    "Zones côtières (AV_C + SSV_C)": ["AV_C", "SSV_C"],
    "Zones montagneuses (AV_H + SSV_H)": ["AV_H", "SSV_H"]
}

# Filtre à partir de 1983
# df = df[df["ANNEE"] >= 1983]


def calcule_augmentation(df, zones):
    """Calcule l'augmentation des nuits chaudes depuis 1983
       pour un groupe de zones donné.
    """
    df_group = df[df["zone_geographique"].isin(zones)]

    # moyenne par année pour ce groupe
    df_annuel = (
        df_group.groupby("ANNEE", as_index=False)["moy_nuits_ge_20"]
        .mean()
        .sort_values("ANNEE")
    )

    annee_depart = df_annuel["ANNEE"].min()
    annee_fin = df_annuel["ANNEE"].max()

    val_depart = df_annuel.loc[df_annuel["ANNEE"] == annee_depart, "moy_nuits_ge_20"].values[0]
    val_fin    = df_annuel.loc[df_annuel["ANNEE"] == annee_fin,    "moy_nuits_ge_20"].values[0]

    augmentation = val_fin - val_depart

    return augmentation, val_depart, val_fin, annee_depart, annee_fin


# --- Affichage des 2 cards côte à côte ---
col1, col2 = st.columns(2)
cotes_aug, cotes_value_start, cotes_value_end, cotes_annee_start, cotes_annee_end = calcule_augmentation(df, groupes["Zones côtières (AV_C + SSV_C)"])

with col1:
    # aug, start, end, a0, a1 = calcule_augmentation(df, groupes["Zones côtières (AV_C + SSV_C)"])
    st.metric(
        label=f"Nuits ≥ 20°C — Zones côtières",
        # value=f"{cotes_aug:.1f} nuits/an",
        value="",
        delta=f"{cotes_value_end:.1f} en {cotes_annee_end} vs {cotes_value_start:.1f} en {cotes_annee_start}"
    )

with col2:
    aug, start, end, a0, a1 = calcule_augmentation(df, groupes["Zones montagneuses (AV_H + SSV_H)"])
    st.metric(
        label=f"Augmentation nuits ≥ 20°C — Zones montagneuses",
        # value=f"{aug:.1f} nuits/an",
        value="",
        delta=f"{end:.1f} en {a1} vs {start:.1f} en {a0}"
    )


import streamlit as st

# Exemple de valeurs calculées avant
augmentation = 20.4   # pente ou différence selon ton choix
annee_depart = 1983
annee_fin = 2025


# --- Card custom ---
st.markdown(
    """
    <style>
        .card {
            background-color: #f8f9fa;
            padding: 1.2rem 1.5rem;
            border-radius: 12px;
            border: 1px solid #ddd;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .card-title {
            font-size: 1.1rem;
            color: #555;
            margin-bottom: 0.3rem;
        }
        .card-value {
            font-size: 1.8rem;
            font-weight: 700;
            margin: 0.4rem 0;
        }
        .card-subtitle {
            font-size: 0.9rem;
            color: #777;
        }
    </style>
    <div class="card">
        <div class="card-title">
            <b>Nuits ≥ 20°C — Zones côtières</b>
        </div>

        <div class="card-value">
            {augmentation:+.1f} nuits/an
        </div>

        <div class="card-subtitle">
            évolution annuelle moyenne depuis {annee_depart}
        </div>
    </div>
    """.format(
        augmentation=augmentation,
        annee_depart=annee_depart
    ),
    unsafe_allow_html=True
)


