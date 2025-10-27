import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Tavola Periodica Interattiva", layout="wide")
st.title("🧪 Tavola Periodica Interattiva – Periodic Quiz")

# Carica dati
data = pd.read_csv("data/elementi.csv")

# Mappa per categorie colori
category_colors = {
    "Metallo alcalino": "#FFD6A5",
    "Metallo alcalino-terroso": "#FDFFB6",
    "Metallo di transizione": "#9BF6FF",
    "Semimetallo": "#CAFFBF",
    "Non metallo": "#90E0EF",
    "Gas nobile": "#FFB3C6",
    "Alogeno": "#FFC6FF",
    "Lanthanide": "#D0F4DE",
    "Actinide": "#FFEE93"
}

# Variabile di sessione
if "quiz_mode" not in st.session_state:
    st.session_state.quiz_mode = False
if "score" not in st.session_state:
    st.session_state.score = 0
if "asked" not in st.session_state:
    st.session_state.asked = []

# Pulsante per iniziare quiz
if st.button("Inizia Quiz"):
    st.session_state.quiz_mode = True
    st.session_state.score = 0
    st.session_state.asked = []

# Funzione per ottenere domanda casuale
def get_question():
    remaining = data[~data['NumeroAtomico'].isin(st.session_state.asked)]
    if len(remaining) == 0:
        return None
    row = remaining.sample(1).iloc[0]
    st.session_state.asked.append(row["NumeroAtomico"])
    return row

# Modalità Quiz
question = None
if st.session_state.quiz_mode:
    question = get_question()
    if question is not None:
        st.subheader(f"Dov'è l'elemento: {question['Nome']}?")

# Funzione per creare tavola
def draw_table():
    # 7 periodi, 18 gruppi
    table_html = "<table style='border-collapse: collapse;'>"
    for period in range(1, 8):
        table_html += "<tr>"
        for group in range(1, 19):
            # Cerca elemento con questo periodo e gruppo
            elem = data[(data["Periodo"]==period) & (data["Gruppo"]==group)]
            if len(elem) > 0:
                elem = elem.iloc[0]
                color = category_colors.get(elem["Categoria"], "#FFFFFF")
                display_text = f"{elem['NumeroAtomico']}<br>{elem['Simbolo']}"
                # Se in modalità quiz, mostra solo numero atomico
                if st.session_state.quiz_mode:
                    display_text = f"{elem['NumeroAtomico']}"
                table_html += f"<td style='border:1px solid #555; width:50px; height:50px; text-align:center; vertical-align:middle; background-color:{color}; cursor:pointer;' onclick='window.location.reload()'>{display_text}</td>"
            else:
                table_html += "<td style='width:50px; height:50px;'></td>"
        table_html += "</tr>"
    table_html += "</table>"
    st.markdown(table_html, unsafe_allow_html=True)
  
# I hate myself Im so alone i just wanna a best friend or better a Bro


draw_table()

if st.session_state.quiz_mode and question is None:
    st.success(f"Quiz terminato! Punteggio: {st.session_state.score}/{len(st.session_state.asked)}")
