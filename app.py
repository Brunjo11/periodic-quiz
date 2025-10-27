# app.py
import streamlit as st
import pandas as pd
import random
import os

st.set_page_config(page_title="Tavola Periodica Interattiva", layout="wide")
st.title("🧪 Tavola Periodica Interattiva – Periodic Quiz")

DATA_PATH = "data/elementi.csv"

# ---------- fallback: crea un CSV minimale se manca (per test veloce) ----------
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

# Normalizza nomi colonne (in caso di differenze)
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

# ---------- palette colori (toni scuri, sobri) ----------
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
# fallback: se categoria non presente usa colore dalla colonna Colore del CSV, oppure grigio scuro
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

# ---------- gestione click tramite query param 'sel' ----------
params = st.experimental_get_query_params()
selected = None
if "sel" in params:
    try:
        selected = int(params["sel"][0])
    except:
        selected = None

# ---------- se utente ha selezionato una casella durante il quiz ----------
if st.session_state.quiz_mode and selected is not None and st.session_state.question is not None:
    target = int(st.session_state.question["NumeroAtomico"])
    st.session_state.round += 1
    # trova riga dell'elemento selezionato
    sel_row = data[data["NumeroAtomico"] == selected]
    if not sel_row.empty:
        sel_row = sel_row.iloc[0]
        # controllo esatto
        if selected == target:
            st.session_state.score += 1.0
            st.session_state.last_feedback = ("correct", f"Giusto! Hai cliccato {selected} ({sel_row['Simbolo']}). +1 punto.")
        else:
            # controllo parziale: stesso periodo o stessa categoria
            qrow = st.session_state.question
            same_period = int(sel_row["Periodo"]) == int(qrow["Periodo"])
            same_cat = str(sel_row["Categoria"]).strip().lower() == str(qrow["Categoria"]).strip().lower()
            if same_period or same_cat:
                st.session_state.score += 0.5
                reason = "periodo" if same_period else "categoria"
                st.session_state.last_feedback = ("partial", f"Quasi! Hai scelto {selected} ({sel_row['Simbolo']}) — stesso {reason}. +0.5 punti.")
            else:
                st.session_state.last_feedback = ("wrong", f"Sbagliato. Hai scelto {selected} ({sel_row['Simbolo']}). +0 punti.")
    else:
        st.session_state.last_feedback = ("wrong", f"Casella vuota o non valida ({selected}). +0 punti.")

    # marcare domanda come fatta
    st.session_state.asked.append(int(st.session_state.question["NumeroAtomico"]))
    # scegli nuova domanda (se round < 10)
    if st.session_state.round < 10:
        st.session_state.question = pick_question()
    else:
        st.session_state.question = None
    # dopo aver gestito la selezione, puliamo il parametro URL per evitare doppie selezioni
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    
    # I hate myself Im so alone i wanna only a best friend or better a Bro😊😁
    
    
    
    
    
    
    
    
    
    
    
    st.experimental_set_query_params()  # svuota i parametri

# ---------- mostra punteggio e feedback ----------
score_col1, score_col2 = st.columns([2, 8])
with score_col1:
    st.metric("Punteggio", f"{st.session_state.score}/{10}")
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

# ---------- generazione HTML della tabella (7 periodi x 18 gruppi) ----------
# costruiamo una matrice 7x18
periods = list(range(1, 8))
groups = list(range(1, 19))

# Prepariamo un dizionario di lookup per velocità: key = (period, group) -> row
lookup = {}
for _, r in data.iterrows():
    try:
        p = int(r["Periodo"])
    except:
        continue
    try:
        g = int(r["Gruppo"])
    except:
        # se non c'è gruppo numerico lo ignoriamo nella griglia principale
        continue
    lookup[(p, g)] = r

# Stile CSS: caselle staccate, bordi sottili, font, dimensione
css = """
<style>
.table-wrap { margin-left:30px; }
.periodic-table { border-collapse: separate; border-spacing: 8px; } /* spacing between cells */
.element-box {
  width: 64px;
  height: 64px;
  display:flex;
  flex-direction:column;
  justify-content:center;
  align-items:center;
  border-radius:6px;
  color: #fff;
  font-family: 'Segoe UI', Roboto, Arial, sans-serif;
  box-shadow: 0 1px 0 rgba(0,0,0,0.35) inset;
  border: 1px solid rgba(0,0,0,0.4);
}
.element-atom { font-size:14px; opacity:0.95; }
.element-symbol { font-weight:700; font-size:18px; }
.empty-cell { width:64px; height:64px; background:transparent; }
.legend { margin-left: 30px; margin-top: 16px; }
</style>
"""

html = css + "<div class='table-wrap'><table class='periodic-table'>"

for p in periods:
    html += "<tr>"
    for g in groups:
        cell = lookup.get((p, g))
        if cell is None:
            # casella vuota
            html += "<td><div class='empty-cell'></div></td>"
        else:
            color = get_color(cell)
            num = int(cell["NumeroAtomico"])
            sym = str(cell["Simbolo"])
            # se in quiz_mode mostriamo solo numero atomico grande; altrimenti numero+simb
            if st.session_state.quiz_mode:
                display = f"<div class='element-box' style='background:{color};'><div class='element-atom'>{num}</div></div>"
            else:
                display = (f"<div class='element-box' style='background:{color};'>"
                           f"<div class='element-atom'>{num}</div>"
                           f"<div class='element-symbol'>{sym}</div>"
                           f"</div>")
            # rendiamo la casella cliccabile: impostiamo parametro sel con il numero atomico
            html += f"<td><a href='?sel={num}' style='text-decoration:none'>{display}</a></td>"
    html += "</tr>"
html += "</table></div>"

# ---------- aggiunta lanthanidi/actinidi (se presenti) ----------
lan = data[data["Categoria"].str.contains("Lanthanide", case=False, na=False)].sort_values("NumeroAtomico")
ac = data[data["Categoria"].str.contains("Actinide", case=False, na=False)].sort_values("NumeroAtomico")
if not lan.empty or not ac.empty:
    html += "<div class='table-wrap'><table class='periodic-table'><tr>"
    # label per la riga principale che mostra 'Lanthanidi' e 'Attinidi'
    html += "<td colspan='18' style='height:8px'></td></tr><tr>"
    html += "<td colspan='2'></td><td colspan='16' style='padding-top:8px; text-align:left; color:#ddd; font-weight:600;'>Serie: Lanthanidi</td></tr><tr>"
    # lanthanidi (mostriamo fino a 15 elementi in fila)
    if not lan.empty:
        for _, r in lan.iterrows():
            color = get_color(r)
            num = int(r["NumeroAtomico"])
            sym = r["Simbolo"]
            if st.session_state.quiz_mode:
                display = f"<div class='element-box' style='background:{color};'><div class='element-atom'>{num}</div></div>"
            else:
                display = (f"<div class='element-box' style='background:{color};'>"
                           f"<div class='element-atom'>{num}</div>"
                           f"<div class='element-symbol'>{sym}</div>"
                           f"</div>")
            html += f"<td><a href='?sel={num}' style='text-decoration:none'>{display}</a></td>"
    html += "</tr>"
    # actinidi
    if not ac.empty:
        html += "<tr><td colspan='2'></td><td colspan='16' style='padding-top:12px; text-align:left; color:#ddd; font-weight:600;'>Serie: Actinidi</td></tr><tr>"
        for _, r in ac.iterrows():
            color = get_color(r)
            num = int(r["NumeroAtomico"])
            sym = r["Simbolo"]
            if st.session_state.quiz_mode:
                display = f"<div class='element-box' style='background:{color};'><div class='element-atom'>{num}</div></div>"
            else:
                display = (f"<div class='element-box' style='background:{color};'>"
                           f"<div class='element-atom'>{num}</div>"
                           f"<div class='element-symbol'>{sym}</div>"
                           f"</div>")
            html += f"<td><a href='?sel={num}' style='text-decoration:none'>{display}</a></td>"
    html += "</tr></table></div>"

# ---------- render HTML ----------
st.markdown(html, unsafe_allow_html=True)

# ---------- se quiz terminato, mostra risultato finale ----------
if st.session_state.round >= 10 and st.session_state.quiz_mode:
    st.session_state.quiz_mode = False
    st.success(f"Quiz completato! Punteggio finale: {st.session_state.score}/10")
    st.write("Puoi premere 'Inizia Quiz' per rifare una sessione.")

# ---------- per debugging: mostra domanda corrente ----------
if st.session_state.quiz_mode and st.session_state.question is not None:
    q = st.session_state.question
    st.subheader(f"Dov'è l'elemento: {q['Nome']}? (numero {int(q['NumeroAtomico'])})")
else:
    st.write("")
