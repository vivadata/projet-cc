import streamlit as st

from data_layer.bigquery import get_todo1

st.set_page_config(
    page_title="Climat de La Réunion",
    page_icon="🌧️",
    layout="wide"
)
st.header("Températures annuelles")

df = get_todo1()

st.dataframe(df)