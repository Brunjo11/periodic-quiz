# app.py
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Tavola Periodica Interattiva", layout="wide")
st.title("🧪 Tavola Periodica Interattiva – Periodic Quiz")

DATA_PATH = "data/elementi.csv"

# ---------- fallback: crea un CSV minimale se manca ----------
if not os.path.exists(DATA_PATH):
    os.makedirs("data", exist_ok=True)
    sample = """NumeroAtomico,Simbolo,Nome,Periodo,Gruppo,Categoria,Colore
1,H,Idrogeno,1,1,Non metallo,#2E86AB
2,He,Elio,1,18,Gas nobile,#7F7FD5
3,Li,Litio,2,1,Metallo alcalino,#6A994E
4,Be,Berio,2,2,Metallo alcalino-terroso,#B08EA2
5,B,Boro,2,13,Semimetallo,#8D6B4F
6,C,Carbonio,2,14,Non metallo,#3B3B98
7,N,Azoto,2,15,Non metallo,#2B3A67
8,O,Ossigeno,2,16,Non metallo,#2E8B57
9,F,Fluoro,2,17,Alogeno,#6C5B7B
10,Ne,Neon,2,18,Gas nobile,#4E4E50
"""
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        f.write(sample)

# ---------- carica dati ----------
try:
    data = pd.read_csv(DATA_PATH, dtype={"NumeroAtomico": int})
except Exception as e:
    st.error(f"Errore caricamento {DATA_PATH}: {e}")
    st.stop()

# Normalizza nomi colonne
cols_map = {c.lower(): c for c in data.columns}
def col(name):
    name = name.lower()
    return cols_map.get(name, name)

# Assicuriamoci di avere le colonne richieste
required = ["NumeroAtomico", "Simbolo", "Nome", "Periodo", "Gruppo", "Categoria", "Colore"]
for r in required:
    if r not in data.columns:
        st.error(f"Il file {DATA_PATH} deve contenere la colonna `{r}`.")
        st.stop()

# Palette colori
category_colors = {
    "Metallo alcalino": "#5b8c5a",
    "Metallo alcalino-terroso": "#7f6a55",
    "Metallo di transizione": "#4a6fa5",
    "Semimetallo": "#7a6f64",
    "Non metallo": "#3d6b6d",
    "Gas nobile": "#6b5b95",
    "Alogeno": "#6b4757",
    "Lanthanide": "#5f7f6e",
    "Actinide": "#6b6b4f"
}
def get_color(row):
    cat = str(row["Categoria"])
    if cat in category_colors:
        return category_colors[cat]
    if pd.notna(row.get("Colore")) and str(row["Colore"]).strip() != "":
        return row["Colore"]
    return "#2f2f2f"

# ---------- session state ----------
if "quiz_mode" not in st.session_state:
    st.session_state.quiz_mode = False
if "score" not in st.session_state:
    st.session_state.score = 0.0
if "asked" not in st.session_state:
    st.session_state.asked = []
if "question" not in st.session_state:
    st.session_state.question = None
if "round" not in st.session_state:
    st.session_state.round = 0
if "last_feedback" not in st.session_state:
    st.session_state.last_feedback = None

# ---------- UI: controllo quiz ----------
col1, col2 = st.columns([1, 4])
with col1:
    if st.button("Inizia Quiz"):
        st.session_state.quiz_mode = True
        st.session_state.score = 0.0
        st.session_state.asked = []
        st.session_state.round = 0
        st.session_state.last_feedback = None
        st.session_state.question = None
with col2:
    st.write("")  # spazio

# Bottone per resettare tutto
if st.button("Reset"):
    st.session_state.quiz_mode = False
    st.session_state.score = 0.0
    st.session_state.asked = []
    st.session_state.question = None
    st.session_state.round = 0
    st.session_state.last_feedback = None

st.markdown("---")

# ---------- funzione per scegliere domanda ----------
def pick_question():
    remaining = data[~data["NumeroAtomico"].isin(st.session_state.asked)]
    if remaining.empty or st.session_state.round >= 10:
        return None
    row = remaining.sample(1).iloc[0]
    return row

if st.session_state.quiz_mode and (st.session_state.question is None):
    st.session_state.question = pick_question()
    if st.session_state.question is None:
        st.session_state.quiz_mode = False

# ---------- funzione per valutare la risposta ----------
def check_answer(selected_num):
    qrow = st.session_state.question
    target = int(qrow["NumeroAtomico"])
    sel_row = data[data["NumeroAtomico"] == selected_num].iloc[0]

    if selected_num == target:
        st.session_state.score += 1.0
        st.session_state.last_feedback = ("correct", f"Giusto! Hai cliccato {selected_num} ({sel_row['Simbolo']}). +1 punto.")
    else:
        same_period = int(sel_row["Periodo"]) == int(qrow["Periodo"])
        same_cat = str(sel_row["Categoria"]).strip().lower() == str(qrow["Categoria"]).strip().lower()
        if same_period or same_cat:
            st.session_state.score += 0.5
            reason = "periodo" if same_period else "categoria"
            st.session_state.last_feedback = ("partial", f"Quasi! Hai scelto {selected_num} ({sel_row['Simbolo']}) — stesso {reason}. +0.5 punti.")
        else:
            st.session_state.last_feedback = ("wrong", f"Sbagliato. Hai scelto {selected_num} ({sel_row['Simbolo']}). +0 punti.")

    st.session_state.asked.append(int(qrow["NumeroAtomico"]))
    st.session_state.round += 1
    st.session_state.question = pick_question() if st.session_state.round < 10 else None

# ---------- CSS caselle ----------
css = """
<style>
.table-wrap { margin-left:30px; }
.element-box {
  width: 64px; height: 64px; display:flex; flex-direction:column; justify-content:center; align-items:center;
  border-radius:6px; color: #fff; font-family: 'Segoe UI', Roboto, Arial, sans-serif;
  box-shadow: 0 1px 0 rgba(0,0,0,0.35) inset; border: 1px solid rgba(0,0,0,0.4); margin:2px;
}
.element-atom { font-size:14px; opacity:0.95; }
.element-symbol { font-weight:700; font-size:18px; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ---------- generazione tabella principale con bottoni ----------
periods = list(range(1, 8))
groups = list(range(1, 19))

lookup = {}
for _, r in data.iterrows():
    try:
        p = int(r["Periodo"])
        g = int(r["Gruppo"])
        lookup[(p, g)] = r
    except:
        continue

for p in periods:
    cols = st.columns(18)
    for i, g in enumerate(groups):
        cell = lookup.get((p, g))
        if cell is None:
            cols[i].write("")
        else:
            color = get_color(cell)
            num = int(cell["NumeroAtomico"])
            sym = str(cell["Simbolo"])
            if st.session_state.quiz_mode:
                if cols[i].button(f"{num}", key=f"btn_{num}"):
                    check_answer(num)
                cols[i].markdown(f"<div class='element-box' style='background:{color};'><div class='element-atom'>{num}</div></div>", unsafe_allow_html=True)
            else:
                display = f"<div class='element-box' style='background:{color};'><div class='element-atom'>{num}</div><div class='element-symbol'>{sym}</div></div>"
                cols[i].markdown(display, unsafe_allow_html=True)

# ---------- lanthanidi / attinidi ----------
lan = data[data["Categoria"].str.contains("Lanthanide", case=False, na=False)].sort_values("NumeroAtomico")
ac = data[data["Categoria"].str.contains("Actinide", case=False, na=False)].sort_values("NumeroAtomico")

if not lan.empty or not ac.empty:
    st.write("---")
    if not lan.empty:
        st.write("Serie: Lanthanidi")
        lan_cols = st.columns(len(lan))
        for i, (_, r) in enumerate(lan.iterrows()):
            color = get_color(r)
            num = int(r["NumeroAtomico"])
            sym = r["Simbolo"]
            if st.session_state.quiz_mode:
                if lan_cols[i].button(f"{num}", key=f"lan_{num}"):
                    check_answer(num)
                lan_cols[i].markdown(f"<div class='element-box' style='background:{color};'><div class='element-atom'>{num}</div></div>", unsafe_allow_html=True)
            else:
                lan_cols[i].markdown(f"<div class='element-box' style='background:{color};'><div class='element-atom'>{num}</div><div class='element-symbol'>{sym}</div></div>", unsafe_allow_html=True)

    if not ac.empty:
        st.write("Serie: Attinidi")
        ac_cols = st.columns(len(ac))
        for i, (_, r) in enumerate(ac.iterrows()):
            color = get_color(r)
            num = int(r["NumeroAtomico"])
            sym = r["Simbolo"]
            if st.session_state.quiz_mode:
                if ac_cols[i].button(f"{num}", key=f"ac_{num}"):
                    check_answer(num)
                ac_cols[i].markdown(f"<div class='element-box' style='background:{color};'><div class='element-atom'>{num}</div></div>", unsafe_allow_html=True)
            else:
                ac_cols[i].markdown(f"<div class='element-box' style='background:{color};'><div class='element-atom'>{num}</div><div class='element-symbol'>{sym}</div></div>", unsafe_allow_html=True)

# ---------- mostra punteggio e feedback ----------
score_col1, score_col2 = st.columns([2, 8])
with score_col1:
    st.metric("Punteggio", f"{st.session_state.score}/10")
    st.write(f"Domande fatte: {st.session_state.round}/10")
with score_col2:
    if st.session_state.last_feedback:
        typ, msg = st.session_state.last_feedback
        if typ == "correct":
            st.success(msg)
        elif typ == "partial":
            st.warning(msg)
        else:
            st.error(msg)

st.markdown("### Istruzioni")
st.write("• Usa 'Inizia Quiz' per avviare. • Clicca sulla casella corrispondente all'elemento richiesto. • Ogni sessione ha 10 domande. • 1 punto esatto, 0.5 se stesso periodo o categoria, 0 altrimenti.")

st.markdown("---")

# ---------- quiz terminato ----------
if st.session_state.round >= 10 and st.session_state.quiz_mode:
    st.session_state.quiz_mode = False
    st.success(f"Quiz completato! Punteggio finale: {st.session_state.score}/10")
    st.write("Puoi premere 'Inizia Quiz' per rifare una sessione.")

# ---------- mostra domanda corrente ----------
if st.session_state.quiz_mode and st.session_state.question is not None:
    q = st.session_state.question
    st.subheader(f"Dov'è l'elemento: {q['Nome']}? (numero {int(q['NumeroAtomico'])})")
else:
    st.write("")
