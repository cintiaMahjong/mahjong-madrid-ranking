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
# CSS
# ============================================================

st.markdown("""
<style>

/* ============================================================
   FONDO
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
   OCULTAR ELEMENTOS
   ============================================================ */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}


/* ============================================================
   TEXTO
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
    margin-bottom: 16px;
}

.titulo {
    color: #f5e8c5 !important;
    font-size: 1.5rem;
    font-weight: 900;
    letter-spacing: 1.4px;
    line-height: 1.1;
    margin-top: 5px;
}

.subtitulo {
    color: #b89445 !important;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 2px;
    margin-top: 5px;
}


/* ============================================================
   MCR / RIICHI
   ============================================================ */

button[key="boton_mcr"],
button[key="boton_riichi"] {
    min-height: 54px !important;
    height: 54px !important;

    background: #123125 !important;
    background-color: #123125 !important;

    border: 2px solid #806a35 !important;
    border-radius: 12px !important;

    color: #e6d9ad !important;

    font-size: 1rem !important;
    font-weight: 900 !important;

    box-shadow: none !important;
}

button[key="boton_mcr"] p,
button[key="boton_riichi"] p {
    color: #e6d9ad !important;
}


/* ============================================================
   PESTAÑAS
   ============
```
