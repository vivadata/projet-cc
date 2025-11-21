import streamlit as st

from data_layer.bigquery import get_data, get_todo1

st.set_page_config(
    page_title="Climat de La Réunion",
    page_icon="🌧️",
    layout="wide"
)
st.header("Températures annuelles")


df2 = get_data()

st.line_chart(df2, x="ANNEE", y="moy_nuits_ge_20")