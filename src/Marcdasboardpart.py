import streamlit as st
from google.cloud import bigquery
import pandas as pd

# Titre de l'app
# st.title("Climat de La Réunion")

# Initialiser le client BigQuery
client = bigquery.Client()

# Sélecteurs Streamlit
# annee = st.selectbox("Choisir une année", [1952, 1953, 1954])  # ou générer dynamiquement
# region = st.selectbox("Choisir une région climatique", ["BSh", "Aw", "Am", "Af", "Cwa", "Cfa", "Cwb", "Cfb"])

# Requête SQL
query = f"""
SELECT
  --T.ANNEE,
  SUM(T.NBJGELEE) AS SUM_NB_GELEES
FROM
  `cc-reunion.data_meteofrance.stg_mens_temperatures` AS T
"""

# Exécuter la requête et récupérer le dataframe
df = client.query(query).to_dataframe()

# Afficher le dataframe
st.dataframe(df)

# Exemple de graphique
# st.line_chart(df[['nb_stations', 'autre_colonne']])
