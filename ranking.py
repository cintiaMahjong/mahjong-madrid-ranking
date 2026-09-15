```python
import streamlit as st
import pandas as pd
import urllib.request
import json
from pathlib import Path


# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="Liga Mahjong Madrid",
    page_icon="🀄",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# =========================================================
# TEMPORADAS
# =========================================================

TEMPORADA_1 = "Oct 2025 - Sept 2026"
TEMPORADA_2 = "Oct 2026 - Sept 2027"


# =========================================================
# ESTILO
# =========================================================

st.markdown(
    """
    <style>

    /* Fondo general */
    .stApp {
        background-color: #0b2118;
    }

    [data-testid="stHeader"] {
        background-color: transparent;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 680px;
        padding-left: 12px;
        padding-right: 12px;
        padding-top: 10px;
    }

    /* Ocultar menú y footer */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    /* Texto general */
    p, label, span {
        color: #f5e8c5;
    }

    /* Título */
    .titulo {
        text-align: center;
        color: #f5e8c5;
        font-size: 25px;
        font-weight: 900;
        letter-spacing: 1.5px;
        margin-top: 5px;
    }

    .subtitulo {
        text-align: center;
        color: #b89445;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 18px;
    }

    /* Botones MCR / RIICHI */
    button {
        border-radius: 10px !important;
    }

    /* Botones principales */
    div[data-testid="stButton"] button {
        background-color: #143225 !important;
        color: #f5e8c5 !important;
        border: 1px solid #806a35 !important;
        font-weight: 800 !important;
    }

    div[data-testid="stButton"] button:hover {
        border-color: #d1ae52 !important;
        color: #fff0bd !important;
    }

    /* Título ranking */
    .ranking-titulo {
        color: #f5e8c5;
        font-size: 19px;
        font-weight: 900;
        margin-top: 12px;
        margin-bottom: 8px;
    }

    /* Cabecera ranking */
    .ranking-cabecera {
        color: #8f815
```
