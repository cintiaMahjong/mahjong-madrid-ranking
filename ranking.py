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
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# ESTILOS
# =========================================================

st.markdown("""
<style>

    /* =====================================================
       FONDO GENERAL
       ===================================================== */

    .stApp {
        background: #0d241b !important;
    }

    .main {
        background: #0d241b !important;
    }

    [data-testid="stAppViewContainer"] {
        background: #0d241b !important;
    }

    [data-testid="stHeader"] {
        background: #0d241b !important;
    }

    [data-testid="stToolbar"] {
        background: transparent !important;
    }


    /* =====================================================
       TEXTO GENERAL
       ===================================================== */

    html, body, [class*="css"] {
        font-family: Arial, Helvetica, sans-serif;
    }

    p, label, span, div {
        color: #f5e8c5;
    }


    /* =====================================================
       TÍTULO
       ===================================================== */

    .titulo-principal {
        text-align: center;
        color: #f5e8c5 !important;
        font-size: 2.8rem;
        font-weight: 900;
        letter-spacing: 3px;
        margin-top: 5px;
        margin-bottom: 0;
    }

    .subtitulo {
        text-align: center;
        color: #b89445 !important;
        font-size: 1rem;
        letter-spacing: 3px;
        margin-bottom: 25px;
    }


    /* =====================================================
       BOTONES STREAMLIT
       ===================================================== */

    div[data-testid="stButton"] > button {
        background: #173629 !important;
        color: #f5e8c5 !important;
        border: 2px solid #8f7538 !important;
        border-radius: 12px !important;
        box-shadow: none !important;
        opacity: 1 !important;
    }

    div[data-testid="stButton"] > button:hover {
        background: #214b38 !important;
        color: #ffffff !important;
        border-color: #b89445 !important;
    }

    div[data-testid="stButton"] > button p,
    div[data-testid="stButton"] > button span {
        color: #f5e8c5 !important;
    }


    /* =====================================================
       BOTONES MCR / RIICHI
       ===================================================== */

    .boton-juego {
        margin-top: 5px;
        margin-bottom: 25px;
    }

    .boton-juego div[data-testid="stButton"] > button {
        height: 85px !important;
        min-height: 85px !important;
        font-size: 1.8rem !important;
        font-weight: 900 !important;
        letter-spacing: 2px !important;
        border-radius: 16px !important;
        border-width: 3px !important;
    }


    /* =====================================================
       BOTÓN ACTIVO
       ===================================================== */

    .boton-activo div[data-testid="stButton"] > button {
        background: #f2c94c !important;
        background-color: #f2c94c !important;
        color: #b00020 !important;
        border: 3px solid #b00020 !important;
        box-shadow: 0 0 12px rgba(242, 201, 76, 0.35) !important;
    }

    .boton-activo div[data-testid="stButton"] > button p,
    .boton-activo div[data-testid="stButton"] > button span,
    .boton-activo div[data-testid="stButton"] > button div {
        color: #b00020 !important;
        font-weight: 900 !important;
    }


    /* =====================================================
       BOTONES DE JUGADORES
       ===================================================== */

    .boton-jugador div[data-testid="stButton"] > button {
        height: 48px !important;
        min-height: 48px !important;
        background: #173629 !important;
        background-color: #173629 !important;
        color: #f5e8c5 !important;
        border: 1px solid #8f7538 !important;
        border-radius: 9px !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        text-align: left !important;
        padding-left: 14px !important;
        padding-right: 14px !important;
    }

    .boton-jugador div[data-testid="stButton"] > button:hover {
        background: #214b38 !important;
        border-color: #b89445 !important;
    }

    .boton-jugador div[data-testid="stButton"] > button p {
        color: #f5e8c5 !important;
    }


    /* =====================================================
       CABECERA DEL RANKING
       ===================================================== */

    .cabecera-ranking {
        background: #173629;
        border: 1px solid #8f7538;
        border-radius: 10px;
        padding: 10px 12px;
        margin-bottom: 8px;
        color: #b89445 !important;
        font-weight: 900;
        font-size: 0.85rem;
    }


    /* =====================================================
       PANEL DEL JUGADOR
       ===================================================== */

    .panel-jugador {
        background: #122d22;
        border: 2px solid #8f7538;
        border-radius: 16px;
        padding: 25px;
        margin-top: 25px;
        margin-bottom: 20px;
    }

    .nombre-jugador {
        color: #f5e8c5 !important;
        font-size: 2rem;
        font-weight: 900;
        margin-bottom: 3px;
    }

    .info-jugador {
        color: #b89445 !important;
        font-size: 0.95rem;
        letter-spacing: 1px;
        margin-bottom: 20px;
    }


    /* =====================================================
       MÉTRICAS
       ===================================================== */

    [data-testid="stMetric"] {
        background: #173629 !important;
        border: 1px solid #8f7538 !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }

    [data-testid="stMetricLabel"] {
        color: #b89445 !important;
    }

    [data-testid="stMetricValue"] {
        color: #f5e8c5 !important;
    }


    /* =====================================================
       TABLA
       ===================================================== */

    [data-testid="stDataFrame"] {
        border: 1px solid #8f7538 !important;
        border-radius: 10px !important;
    }


    /* =====================================================
       SEPARADORES
       ===================================================== */

    hr {
        border-color: #8f7538 !important;
    }


    /* =====================================================
       PIE
       ===================================================== */

    .footer {
        text-align: center;
        color: #8f7538 !important;
        font-size: 0.8rem;
        margin-top: 35px;
        padding-bottom: 20px;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# BUSCAR LOGO
# =========================================================

BASE_DIR = Path(__file__).resolve().parent


def buscar_logo():

    nombres = [
        "logo_mahjong_madrid.png",
        "logo_mahjong_madrid.PNG",
        "Logo_Mahjong_Madrid.png",
        "Logo Mahjong Madrid.png",
        "logo mahjong madrid.png"
    ]

    for nombre in nombres:

        ruta = BASE_DIR / nombre

        if ruta.exists():
            return ruta

    # Búsqueda más flexible

    for ruta in BASE_DIR.iterdir():

        if not ruta.is_file():
            continue

        if ruta.suffix.lower() not in [
            ".png",
            ".jpg",
            ".jpeg",
            ".webp"
        ]:
            continue

        nombre = (
            ruta.stem.lower()
            .replace("_", "")
            .replace("-", "")
            .replace(" ", "")
        )

        if "mahjong" in nombre and "madrid" in nombre:
            return ruta

    return None


# =========================================================
# CONEXIÓN SUPABASE
# =========================================================

SUPABASE_URL = "https://gauqwlrsmxynqcokblaw.supabase.co/rest/v1"


def supabase_get(tabla):

    try:

        key = st.secrets["SUPABASE_KEY"]

        url = f"{SUPABASE_URL}/{tabla}"

        request = urllib.request.Request(
            url,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
        )

        with urllib.request.urlopen(request) as response:

            datos = json.loads(
                response.read().decode("utf-8")
            )

        return pd.DataFrame(datos)

    except Exception as e:

        st.error(f"Error conectando con Supabase: {e}")

        return pd.DataFrame()


# =========================================================
# CARGAR DATOS
# =========================================================

jugadores = supabase_get("jugadores")

partidas = supabase_get("partidas")

resultados = supabase_get("resultados_partidas")


if jugadores.empty or partidas.empty or resultados.empty:

    st.error(
        "No se han podido cargar los datos de Supabase."
    )

    st.stop()


# =========================================================
# PREPARAR DATOS
# =========================================================

resultados["puntuacion"] = pd.to_numeric(
    resultados["puntuacion"],
    errors="coerce"
)

resultados["posicion"] = pd.to_numeric(
    resultados["posicion"],
    errors="coerce"
)

partidas["tipo_juego"] = (
    partidas["tipo_juego"]
    .astype(str)
    .str.upper()
)


# =========================================================
# UNIR TABLAS
# =========================================================

datos = resultados.merge(
    jugadores,
    left_on="jugador_id",
    right_on="id",
    how="left"
)

datos = datos.merge(
    partidas[
        [
            "id",
            "fecha",
            "tipo_juego"
        ]
    ],
    left_on="partida_id",
    right_on="id",
    how="left",
    suffixes=("", "_partida")
)


# =========================================================
# RANKING
# =========================================================

def crear_ranking(tipo):

    df = datos[
        datos["tipo_juego"] == tipo
    ].copy()

    if df.empty:
        return pd.DataFrame()

    ranking = (
        df.groupby(
            [
                "jugador_id",
                "nombre"
            ],
            as_index=False
        )
        .agg(
            Puntos=("puntuacion", "sum"),
            Partidas=("partida_id", "nunique"),
            Media=("puntuacion", "mean")
        )
    )

    # Número de victorias

    primeros = (
        df[df["posicion"] == 1]
        .groupby("jugador_id")
        .size()
        .rename("Primero")
    )

    ranking = ranking.merge(
        primeros,
        on="jugador_id",
        how="left"
    )

    ranking["Primero"] = (
        ranking["Primero"]
        .fillna(0)
        .astype(int)
    )

    # Orden

    ranking = ranking.sort_values(
        by=[
            "Puntos",
            "Primero"
        ],
        ascending=[
            False,
            False
        ]
    ).reset_index(drop=True)

    ranking["Pos."] = (
        ranking.index + 1
    )

    ranking["Puntos"] = (
        ranking["Puntos"]
        .round(0)
        .astype(int)
    )

    ranking["Media"] = (
        ranking["Media"]
        .round(1)
    )

    return ranking


# =========================================================
# MOSTRAR RANKING
# =========================================================

def mostrar_ranking(tipo):

    ranking = crear_ranking(tipo)

    if ranking.empty:

        st.info(
            f"No hay partidas de {tipo} todavía."
        )

        return

    # Cabecera

    st.markdown("""
    <div class="cabecera-ranking">
        <div style="display:grid;
                    grid-template-columns:70px 1fr 100px 100px 100px 70px;
                    gap:10px;
                    align-items:center;">
            <div>POS.</div>
            <div>JUGADOR</div>
            <div>PUNTOS</div>
            <div>PARTIDAS</div>
            <div>MEDIA</div>
            <div>🥇</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Filas

    for _, fila in ranking.iterrows():

        jugador_id = int(
            fila["jugador_id"]
        )

        nombre = str(
            fila["nombre"]
        )

        posicion = int(
            fila["Pos."]
        )

        puntos = int(
            fila["Puntos"]
        )

        partidas_jugadas = int(
            fila["Partidas"]
        )

        media = float(
            fila["Media"]
        )

        primero = int(
            fila["Primero"]
        )

        if primero > 0:
            medalla = f"🥇 {primero}"
        else:
            medalla = "-"

        st.markdown(
            '<div class="boton-jugador">',
            unsafe_allow_html=True
        )

        if st.button(
            f"{posicion}.   {nombre}    ·    {puntos} pts",
            key=f"jugador_{tipo}_{jugador_id}",
            use_container_width=True
        ):

            st.session_state[
                "jugador_seleccionado"
            ] = jugador_id

            st.session_state[
                "jugador_tipo"
            ] = tipo

            st.rerun()

        st.markdown(
            f"""
            <div style="
                display:grid;
                grid-template-columns:70px 1fr 100px 100px 100px 70px;
                gap:10px;
                margin-top:-45px;
                margin-bottom:8px;
                padding-left:12px;
                padding-right:12px;
                pointer-events:none;
                color:#f5e8c5;
                font-size:0.9rem;
            ">
                <div></div>
                <div></div>
                <div></div>
                <div>{partidas_jugadas}</div>
                <div>{media:.1f}</div>
                <div>{medalla}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# MOSTRAR JUGADOR
# =========================================================

def mostrar_jugador(jugador_id, tipo):

    ranking = crear_ranking(tipo)

    if ranking.empty:
        return

    jugador = ranking[
        ranking["jugador_id"] == jugador_id
    ]

    if jugador.empty:
        return

    jugador = jugador.iloc[0]

    posicion = int(
        jugador["Pos."]
    )

    nombre = str(
        jugador["nombre"]
    )

    puntos = int(
        jugador["Puntos"]
    )

    partidas_jugadas = int(
        jugador["Partidas"]
    )

    media = float(
        jugador["Media"]
    )

    df_jugador = datos[
        (datos["jugador_id"] == jugador_id)
        &
        (datos["tipo_juego"] == tipo)
    ].copy()

    # =====================================================
    # PANEL
    # =====================================================

    st.markdown(
        '<div class="panel-jugador">',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="nombre-jugador">
            {nombre}
        </div>

        <div class="info-jugador">
            RANKING {tipo} · POSICIÓN #{posicion}
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # MÉTRICAS
    # =====================================================

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "PUNTOS",
            f"{puntos}"
        )

    with c2:
        st.metric(
            "PARTIDAS",
            f"{partidas_jugadas}"
        )

    with c3:
        st.metric(
            "MEDIA",
            f"{media:.1f}"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================================
    # POSICIONES
    # =====================================================

    conteo = (
        df_jugador["posicion"]
        .value_counts()
        .to_dict()
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            "🥇 1º",
            int(conteo.get(1, 0))
        )

    with c2:
        st.metric(
            "🥈 2º",
            int(conteo.get(2, 0))
        )

    with c3:
        st.metric(
            "🥉 3º",
            int(conteo.get(3, 0))
        )

    with c4:
        st.metric(
            "4º",
            int(conteo.get(4, 0))
        )

    with c5:
        st.metric(
            "5º",
            int(conteo.get(5, 0))
        )

    # =====================================================
    # HISTORIAL
    # =====================================================

    st.markdown(
        "### Historial de partidas"
    )

    historial = df_jugador[
        [
            "fecha",
            "posicion",
            "puntuacion"
        ]
    ].copy()

    historial = historial.rename(
        columns={
            "fecha": "Fecha",
            "posicion": "Posición",
            "puntuacion": "Puntos"
        }
    )

    historial = historial.sort_values(
        by="Fecha",
        ascending=False
    )

    st.dataframe(
        historial,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================
    # CERRAR
    # =====================================================

    if st.button(
        "← Volver al ranking",
        key="cerrar_jugador",
        use_container_width=True
    ):

        st.session_state[
            "jugador_seleccionado"
        ] = None

        st.rerun()


# =========================================================
# SESSION STATE
# =========================================================

if "tipo_juego" not in st.session_state:
    st.session_state["tipo_juego"] = "MCR"

if "jugador_seleccionado" not in st.session_state:
    st.session_state["jugador_seleccionado"] = None

if "jugador_tipo" not in st.session_state:
    st.session_state["jugador_tipo"] = None


# =========================================================
# CABECERA
# =========================================================

logo = buscar_logo()

col_logo, col_titulo = st.columns(
    [1, 4]
)

with col_logo:

    if logo is not None:

        st.image(
            str(logo),
            width=130
        )

with col_titulo:

    st.markdown(
        '<div class="titulo-principal">'
        'LIGA MAHJONG MADRID'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitulo">'
        'RANKING OFICIAL'
        '</div>',
        unsafe_allow_html=True
    )


# =========================================================
# BOTONES MCR / RIICHI
# =========================================================

col_mcr, col_riichi = st.columns(2)


# ---------------------------------------------------------
# MCR
# ---------------------------------------------------------

with col_mcr:

    if st.session_state["tipo_juego"] == "MCR":

        st.markdown(
            '<div class="boton-juego boton-activo">',
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            '<div class="boton-juego">',
            unsafe_allow_html=True
        )

    if st.button(
        "🀄  MCR",
        key="boton_mcr",
        use_container_width=True
    ):

        st.session_state[
            "tipo_juego"
        ] = "MCR"

        st.session_state[
            "jugador_seleccionado"
        ] = None

        st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ---------------------------------------------------------
# RIICHI
# ---------------------------------------------------------

with col_riichi:

    if st.session_state["tipo_juego"] == "RIICHI":

        st.markdown(
            '<div class="boton-juego boton-activo">',
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            '<div class="boton-juego">',
            unsafe_allow_html=True
        )

    if st.button(
        "🎴  RIICHI",
        key="boton_riichi",
        use_container_width=True
    ):

        st.session_state[
            "tipo_juego"
        ] = "RIICHI"

        st.session_state[
            "jugador_seleccionado"
        ] = None

        st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# =========================================================
# TÍTULO DEL RANKING
# =========================================================

tipo_actual = st.session_state[
    "tipo_juego"
]

st.markdown(
    f"""
    <h2 style="
        color:#f5e8c5;
        text-align:center;
        letter-spacing:2px;
        margin-top:10px;
        margin-bottom:20px;
    ">
        RANKING {tipo_actual}
    </h2>
    """,
    unsafe_allow_html=True
)


# =========================================================
# JUGADOR SELECCIONADO
# =========================================================

if st.session_state[
    "jugador_seleccionado"
] is not None:

    mostrar_jugador(
        st.session_state[
            "jugador_seleccionado"
        ],
        st.session_state[
            "jugador_tipo"
        ]
    )

else:

    mostrar_ranking(
        tipo_actual
    )


# =========================================================
# PIE
# =========================================================

st.markdown(
    """
    <div class="footer">
        LIGA MAHJONG MADRID · MCR & RIICHI
    </div>
    """,
    unsafe_allow_html=True
)
