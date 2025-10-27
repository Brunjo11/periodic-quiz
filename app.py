import streamlit as st
import pandas as pd

# Carica i dati
data = pd.read_csv("data/elementi.csv")

st.set_page_config(page_title="Tavola Periodica Interattiva", layout="wide")

st.title("🧪 Tavola Periodica Interattiva – Periodic Quiz")

# Mostra i dati per test
st.dataframe(data)

st.write("Prossimo passo: visualizzare la tavola tipo Zanichelli con i colori corretti.")
