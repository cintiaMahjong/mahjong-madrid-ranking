```python
import streamlit as st
import pandas as pd
import urllib.request
import json
from pathlib import Path


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Liga Mahjong Madrid",
    page_icon="🀄",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ============================================================
# TEMPORADAS
# ============================================================

TEMPORADA_1 = "Oct 2025 - Sept 2026"
TEMPORADA_2 = "Oct 2026 - Sept 2027"


# ============================================================
# CSS - MOBILE FIRST
# ============================================================

st.markdown("""
<style>

/* ============================================================
   FONDO GENERAL
   ============================================================ */

html,
body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: #0b2118 !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stMainBlockContainer"] {
    max-width: 680px !important;
    padding-top: 0.7rem !important;
    padding-left: 0.65rem !important;
    padding-right: 0.65rem !important;
    padding-bottom: 2rem !important;
}


/* ============================================================
   OCULTAR ELEMENTOS STREAMLIT
   ============================================================ */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}


/* ============================================================
   TEXTO GENERAL
   ============================================================ */

body,
p,
label,
span {
    color: #f5e8c5;
}


/* ============================================================
   CABECERA
   ============================================================ */

.cabecera {
    text-align: center;
    margin-bottom: 15px;
}

.titulo {
    color: #f5e8c5 !important;
    font-size: 1.55rem;
    font-weight: 900;
    letter-spacing: 1.4px;
    line-height: 1.1;
    margin-top: 4px;
}

.subtitulo {
    color: #b89445 !important;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 2px;
    margin-top: 5px;
}


/* ============================================================
   SELECTOR MCR / RIICHI
   ============================================================ */

div[data-testid="stHorizontalBlock"]:has(
    button[key="boton_mcr"]
) button,
div[data-testid="stHorizontalBlock"]:has(
    button[key="boton_riichi"]
) button {
    min-height: 54px !important;
    height: 54px !important;
    border-radius: 12px !important;
    font-size: 1rem !important;
    font-weight: 900 !important;
}


/* Botones generales del selector */

button[key="boton_mcr"],
button[key="boton_riichi"] {
    background: #123125 !important;
    border: 2px solid #806a35 !important;
    color: #e6d9ad !important;
    box-shadow: none !important;
}


/* ============================================================
   TABS DE TEMPORADA
   ============================================================ */

[data-baseweb="tab-list"] {
    background: #102a20 !important;
    border-radius: 11px !important;
    padding: 4px !important;
    gap: 4px !important;
    margin-top: 12px !important;
    margin-bottom: 18px !important;
}

button[data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: #9f987e !important;
    font-size: 0.72rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.3px !important;
    padding: 8px 5px !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: #286b49 !important;
    color: #fff1bd !important;
}

button[data-baseweb="tab"] p {
    color: inherit !important;
}

[data-baseweb="tab-highlight"] {
    background: transparent !important;
}


/* ============================================================
   TÍTULO RANKING
   ============================================================ */

.titulo-ranking {
    display: flex;
    align-items: center;
    margin-top: 2px;
    margin-bottom: 10px;
}

.titulo-ranking-texto {
    color: #f5e8c5 !important;
    font-size: 1.08rem;
    font-weight: 900;
    letter-spacing: 1px;
}

.linea-dorada {
    height: 1px;
    background: #806a35;
    flex: 1;
    margin-left: 10px;
}


/* ============================================================
   CABECERA DEL RANKING
   ============================================================ */

.cabecera-ranking {
    display: grid;
    grid-template-columns: 45px 1fr 75px;
    padding: 5px 12px 7px 12px;
    color: #8f8156 !important;
    font-size: 0.62rem;
    font-weight: 800;
    letter-spacing: 1px;
}


/* ============================================================
   BOTONES DE JUGADORES
   ============================================================ */

/*
   Eliminamos completamente el sistema anterior de divs
   superpuestos y margin-top negativos.
*/

div[data-testid="stButton"] {
    margin-bottom: 6px !important;
}

div[data-testid="stButton"] > button {
    background: #143225 !important;
    background-color: #143225 !important;
    border: 1px solid #4f5539 !important;
    border-radius: 12px !important;
    min-height: 68px !important;
    padding: 9px 12px !important;
    box-shadow: none !important;
    transition: none !important;
}

div[data-testid="stButton"] > button:hover {
    background: #19412f !important;
    background-color: #19412f !important;
    border-color: #8f793c !important;
}

div[data-testid="stButton"] > button:focus {
    box-shadow: none !important;
    border-color: #b89445 !important;
}


/* Texto de botones */

div[data-testid="stButton"] > button p {
    color: #f5e8c5 !important;
    font-size: 0.92rem !important;
    font-weight: 8
```
