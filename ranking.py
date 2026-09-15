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

html,
body {
    background-color: #0b2418 !important;
}

.stApp {
    background-color: #0b2418 !important;
}

[data-testid="stAppViewContainer"] {
    background-color: #0b2418 !important;
}

[data-testid="stMain"] {
    background-color: #0b2418 !important;
}

.main {
    background-color: #0b2418 !important;
}

.block-container {
    background-color: #0b2418 !important;
    max-width: 1250px;
    padding-top: 25px;
    padding-bottom: 40px;
}

header[data-testid="stHeader"] {
    background-color: #0b2418 !important;
}

footer {
    background-color: #0b2418 !important;
}


/* =====================================================
   TEXTO GENERAL
   ===================================================== */

p,
label,
span,
div {
    color: #f5e8c5;
}


/* =====================================================
   CABECERA
   ===================================================== */

.titulo-principal {
    color: #e2c36c !important;
    font-size: 3rem !important;
    font-weight: 900 !important;
    letter-spacing: 4px !important;
    line-height: 1.1 !important;
}

.subtitulo {
    color: #d9cfae !important;
    font-size: 1rem !important;
    letter-spacing: 2px !important;
}


/* =====================================================
   TODOS LOS BOTONES
   ===================================================== */

.stButton > button {
    background-color: #173629 !important;
    background: #173629 !important;

    color: #f5e8c5 !important;

    border: 2px solid #b89445 !important;
    border-radius: 14px !important;

    box-shadow: none !important;
    opacity: 1 !important;
}


/* Texto dentro de los botones */

.stButton > button p,
.stButton > button span,
.stButton > button div {
    color: #f5e8c5 !important;
}


/* Hover */

.stButton > button:hover {
    background-color: #234c39 !important;
    background: #234c39 !important;

    color: #ffffff !important;

    border-color: #e2c36c !important;
}


/* Texto hover */

.stButton > button:hover p,
.stButton > button:hover span,
.stButton > button:hover div {
    color: #ffffff !important;
}


/* =====================================================
   BOTONES MCR / RIICHI
   ===================================================== */

.boton-juego .stButton > button {
    min-height: 90px !important;
    height: 90px !important;

    font-size: 1.9rem !important;
    font-weight: 900 !important;

    letter-spacing: 2px !important;

    background-color: #173629 !important;
    background: #173629 !important;

    color: #f5e8c5 !important;

    border: 3px solid #b89445 !important;
    border-radius: 16px !important;
}


/* =====================================================
   RANKING
   ===================================================== */

.numero-posicion {
    color: #e2c36c !important;
    font-size: 1.2rem;
    font-weight: 800;
    text-align: center;
}

.valor-ranking {
    color: #f5e8c5 !important;
    font-size: 1.1rem;
    font-weight: 700;
    text-align: center;
}


/* =====================================================
   BOTONES DE JUGADORES
   ===================================================== */

.boton-jugador .stButton > button {
    min-height: 45px !important;
    height: 45px !important;

    background-color: #173629 !important;
    background: #173629 !important;

    color: #f5e8c5 !important;

    border: 1px solid #8f7538 !important;
    border-radius: 9px !important;

    font-size: 1.05rem !important;
    font-weight: 700 !important;

    text-align: left !important;

    padding-left: 14px !important;
    padding-right: 14px !important;
}


/* =====================================================
   MÉTRICAS
   ===================================================== */

[data-testid="stMetric"] {
    background-color: #173629 !important;

    border: 1px solid #8f7538 !important;

    border-radius: 12px !important;

    padding: 16px !important;
}

[data-testid="stMetricLabel"] {
    color: #d9cfae !important;
}

[data-testid="stMetricValue"] {
    color: #e2c36c !important;
}


/* =====================================================
   PANEL DEL JUGADOR
   ===================================================== */

.panel-jugador {
    background-color: #10291d !important;

    border: 2px solid #b89445 !important;

    border-radius: 18px !important;

    padding: 25px !important;

    margin-top: 30px !important;

    margin-bottom: 30px !important;
}

.nombre-jugador {
    color: #e2c36c !important;

    font-size: 2.2rem !important;

    font-weight: 900 !important;

    letter-spacing: 2px !important;
}

.tipo-jugador {
    color: #d9cfae !important;

    font-size: 1rem !important;

    letter-spacing: 2px !important;
}


/* =====================================================
   TÍTULOS
   ===================================================== */

h1,
h2,
h3,
h4 {
    color: #e2c36c !important;
}


/* =====================================================
   TABLA
   ===================================================== */

[data-testid="stDataFrame"] {
    background-color: #10291d !important;

    border: 1px solid #8f7538 !important;

    border-radius: 10px !important;
}


/* =====================================================
   FOOTER
   ===================================================== */

.footer {
    color: #8f9d91 !important;

    text-align: center;

    margin-top: 40px;

    padding-top: 20px;

    border-top: 1px solid rgba(184,148,69,0.25);
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# LOGO
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


logo = buscar_logo()


# =========================================================
# SUPABASE
# =========================================================

SUPABASE_URL = (
    "https://gauqwlrsmxynqcokblaw.supabase.co/rest/v1"
)


try:

    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

except Exception:

    st.error(
        "No se ha encontrado SUPABASE_KEY "
        "en los secretos de Streamlit."
    )

    st.stop()


def supabase_get(tabla):

    url = f"{SUPABASE_URL}/{tabla}"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    request = urllib.request.Request(
        url,
        headers=headers,
        method="GET"
    )

    try:

        with urllib.request.urlopen(request) as response:

            datos = response.read().decode("utf-8")

            return json.loads(datos)

    except Exception as e:

        st.error(
            f"Error al conectar con Supabase "
            f"({tabla}): {e}"
        )

        st.stop()


# =========================================================
# CARGAR DATOS
# =========================================================

jugadores_data = supabase_get("jugadores")
partidas_data = supabase_get("partidas")
resultados_data = supabase_get("resultados_partidas")


jugadores = pd.DataFrame(jugadores_data)
partidas = pd.DataFrame(partidas_data)
resultados = pd.DataFrame(resultados_data)


# =========================================================
# COMPROBAR COLUMNAS
# =========================================================

columnas_jugadores = [
    "id",
    "nombre"
]

columnas_partidas = [
    "id",
    "fecha",
    "creado_por",
    "tipo_juego"
]

columnas_resultados = [
    "partida_id",
    "jugador_id",
    "posicion",
    "puntuacion"
]


for columna in columnas_jugadores:

    if columna not in jugadores.columns:

        st.error(
            f"Falta la columna '{columna}' "
            f"en jugadores."
        )

        st.stop()


for columna in columnas_partidas:

    if columna not in partidas.columns:

        st.error(
            f"Falta la columna '{columna}' "
            f"en partidas."
        )

        st.stop()


for columna in columnas_resultados:

    if columna not in resultados.columns:

        st.error(
            f"Falta la columna '{columna}' "
            f"en resultados_partidas."
        )

        st.stop()


# =========================================================
# PREPARAR DATOS
# =========================================================

resultados["puntuacion"] = pd.to_numeric(
    resultados["puntuacion"],
    errors="coerce"
).fillna(0)


resultados["posicion"] = pd.to_numeric(
    resultados["posicion"],
    errors="coerce"
)


partidas["tipo_juego"] = (
    partidas["tipo_juego"]
    .astype(str)
    .str.upper()
    .str.strip()
)


# =========================================================
# UNIR TABLAS
# =========================================================

datos = resultados.merge(
    jugadores[["id", "nombre"]],
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


datos["nombre"] = datos["nombre"].fillna(
    "Jugador desconocido"
)


# =========================================================
# CREAR RANKING
# =========================================================

def crear_ranking(tipo):

    datos_tipo = datos[
        datos["tipo_juego"] == tipo
    ].copy()


    if datos_tipo.empty:
        return pd.DataFrame()


    ranking = (
        datos_tipo
        .groupby(
            ["jugador_id", "nombre"],
            as_index=False
        )
        .agg(
            Puntos=("puntuacion", "sum"),
            Partidas=("partida_id", "nunique"),
            Media=("puntuacion", "mean")
        )
    )


    primeros = (
        datos_tipo[
            datos_tipo["posicion"] == 1
        ]
        .groupby("jugador_id")
        .size()
        .rename("Primeros")
    )


    ranking = ranking.merge(
        primeros,
        on="jugador_id",
        how="left"
    )


    ranking["Primeros"] = (
        ranking["Primeros"]
        .fillna(0)
        .astype(int)
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


    ranking = ranking.sort_values(
        by=[
            "Puntos",
            "Primeros"
        ],
        ascending=[
            False,
            False
        ]
    ).reset_index(drop=True)


    ranking.insert(
        0,
        "Pos.",
        ranking.index + 1
    )


    ranking = ranking.rename(
        columns={
            "nombre": "Jugador"
        }
    )


    return ranking


# =========================================================
# MOSTRAR RANKING
# =========================================================

def mostrar_ranking(tipo):

    ranking = crear_ranking(tipo)


    if ranking.empty:

        st.info(
            f"No hay partidas registradas de {tipo}."
        )

        return


    # -----------------------------------------------------
    # CABECERA
    # -----------------------------------------------------

    cabecera = st.columns(
        [0.7, 3, 1.2, 1.2, 1.2, 0.8]
    )


    with cabecera[0]:
        st.markdown("**POS.**")


    with cabecera[1]:
        st.markdown("**JUGADOR**")


    with cabecera[2]:
        st.markdown("**PUNTOS**")


    with cabecera[3]:
        st.markdown("**PARTIDAS**")


    with cabecera[4]:
        st.markdown("**MEDIA**")


    with cabecera[5]:
        st.markdown("**🥇**")


    # -----------------------------------------------------
    # JUGADORES
    # -----------------------------------------------------

    for _, jugador in ranking.iterrows():

        jugador_id = jugador["jugador_id"]


        fila = st.columns(
            [0.7, 3, 1.2, 1.2, 1.2, 0.8]
        )


        # POSICIÓN

        with fila[0]:

            st.markdown(
                f"""
                <div class="numero-posicion">
                    {int(jugador["Pos."])}
                </div>
                """,
                unsafe_allow_html=True
            )


        # JUGADOR

        with fila[1]:

            st.markdown(
                '<div class="boton-jugador">',
                unsafe_allow_html=True
            )


            if st.button(
                str(jugador["Jugador"]),
                key=f"jugador_{tipo}_{jugador_id}",
                use_container_width=True
            ):

                st.session_state[
                    "jugador_seleccionado"
                ] = jugador_id

                st.session_state[
                    "tipo_seleccionado"
                ] = tipo

                st.rerun()


            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )


        # PUNTOS

        with fila[2]:

            st.markdown(
                f"""
                <div class="valor-ranking">
                    {int(jugador["Puntos"])}
                </div>
                """,
                unsafe_allow_html=True
            )


        # PARTIDAS

        with fila[3]:

            st.markdown(
                f"""
                <div class="valor-ranking">
                    {int(jugador["Partidas"])}
                </div>
                """,
                unsafe_allow_html=True
            )


        # MEDIA

        with fila[4]:

            st.markdown(
                f"""
                <div class="valor-ranking">
                    {jugador["Media"]:.1f}
                </div>
                """,
                unsafe_allow_html=True
            )


        # PRIMEROS

        with fila[5]:

            st.markdown(
                f"""
                <div class="valor-ranking">
                    {int(jugador["Primeros"])}
                </div>
                """,
                unsafe_allow_html=True
            )


# =========================================================
# MOSTRAR JUGADOR
# =========================================================

def mostrar_jugador(
    jugador_id,
    tipo,
    ranking
):

    jugador = ranking[
        ranking["jugador_id"] == jugador_id
    ]


    if jugador.empty:
        return


    jugador = jugador.iloc[0]


    posicion_ranking = int(
        jugador["Pos."]
    )


    st.markdown(
        '<div class="panel-jugador">',
        unsafe_allow_html=True
    )


    st.markdown(
        f"""
        <div class="nombre-jugador">
            {jugador["Jugador"]}
        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        f"""
        <div class="tipo-jugador">
            RANKING {tipo} · POSICIÓN #{posicion_ranking}
        </div>
        """,
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # MÉTRICAS
    # -----------------------------------------------------

    c1, c2, c3 = st.columns(3)


    with c1:

        st.metric(
            "PUNTOS",
            int(jugador["Puntos"])
        )


    with c2:

        st.metric(
            "PARTIDAS",
            int(jugador["Partidas"])
        )


    with c3:

        st.metric(
            "MEDIA",
            f'{jugador["Media"]:.1f}'
        )


    # -----------------------------------------------------
    # RESULTADOS
    # -----------------------------------------------------

    st.markdown("### RESULTADOS")


    datos_jugador = datos[
        (datos["jugador_id"] == jugador_id)
        &
        (datos["tipo_juego"] == tipo)
    ].copy()


    posiciones = {}


    for i in range(1, 6):

        posiciones[i] = int(
            (
                datos_jugador["posicion"] == i
            ).sum()
        )


    c1, c2, c3, c4, c5 = st.columns(5)


    resultados_posiciones = [
        (c1, "🥇", 1, "Primeros"),
        (c2, "🥈", 2, "Segundos"),
        (c3, "🥉", 3, "Terceros"),
        (c4, "4º", 4, "Cuartos"),
        (c5, "5º", 5, "Quintos")
    ]


    for columna, icono, numero, texto in resultados_posiciones:

        with columna:

            st.markdown(
                f"### {icono}"
            )

            st.markdown(
                f"## {posiciones[numero]}"
            )

            st.caption(texto)


    # -----------------------------------------------------
    # HISTORIAL
    # -----------------------------------------------------

    st.markdown(
        "### HISTORIAL DE PARTIDAS"
    )


    historial = datos_jugador[
        [
            "fecha",
            "posicion",
            "puntuacion"
        ]
    ].copy()


    historial = historial.sort_values(
        "fecha",
        ascending=False
    )


    historial = historial.rename(
        columns={
            "fecha": "Fecha",
            "posicion": "Posición",
            "puntuacion": "Puntos"
        }
    )


    historial["Puntos"] = (
        historial["Puntos"]
        .round(0)
        .astype(int)
    )


    historial["Posición"] = (
        historial["Posición"]
        .fillna("-")
    )


    st.dataframe(
        historial,
        use_container_width=True,
        hide_index=True
    )


    # -----------------------------------------------------
    # CERRAR
    # -----------------------------------------------------

    if st.button(
        "✕  Cerrar estadísticas",
        key=f"cerrar_{tipo}_{jugador_id}",
        use_container_width=True
    ):

        st.session_state[
            "jugador_seleccionado"
        ] = None

        st.rerun()


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# =========================================================
# ESTADO
# =========================================================

if "tipo_juego" not in st.session_state:

    st.session_state["tipo_juego"] = "MCR"


if "jugador_seleccionado" not in st.session_state:

    st.session_state[
        "jugador_seleccionado"
    ] = None


# =========================================================
# CABECERA
# =========================================================

col_logo, col_titulo = st.columns(
    [1, 5],
    vertical_alignment="center"
)


with col_logo:

    if logo:

        st.image(
            str(logo),
            width=125
        )

    else:

        st.markdown("🀄")


with col_titulo:

    st.markdown(
        '<div class="titulo-principal">'
        'LIGA MAHJONG MADRID'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitulo">'
        'RANKING OFICIAL · MCR & RIICHI'
        '</div>',
        unsafe_allow_html=True
    )


# =========================================================
# BOTONES MCR / RIICHI
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)


col_mcr, col_riichi = st.columns(
    2,
    gap="medium"
)


# ---------------------------------------------------------
# MCR
# ---------------------------------------------------------

with col_mcr:

    st.markdown(
        '<div class="boton-juego">',
        unsafe_allow_html=True
    )


    if st.session_state["tipo_juego"] == "MCR":

        texto_mcr = "🀄  MCR  ✓"

    else:

        texto_mcr = "🀄  MCR"


    if st.button(
        texto_mcr,
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

    st.markdown(
        '<div class="boton-juego">',
        unsafe_allow_html=True
    )


    if st.session_state["tipo_juego"] == "RIICHI":

        texto_riichi = "🎴  RIICHI  ✓"

    else:

        texto_riichi = "🎴  RIICHI"


    if st.button(
        texto_riichi,
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
# RANKING ACTUAL
# =========================================================

tipo_actual = st.session_state[
    "tipo_juego"
]


mostrar_ranking(
    tipo_actual
)


# =========================================================
# JUGADOR SELECCIONADO
# =========================================================

jugador_seleccionado = st.session_state.get(
    "jugador_seleccionado"
)


tipo_seleccionado = st.session_state.get(
    "tipo_seleccionado"
)


if jugador_seleccionado is not None:

    ranking_seleccionado = crear_ranking(
        tipo_seleccionado
    )


    mostrar_jugador(
        jugador_seleccionado,
        tipo_seleccionado,
        ranking_seleccionado
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    '<div class="footer">'
    'Liga Mahjong Madrid · Ranking MCR & RIICHI'
    '</div>',
    unsafe_allow_html=True
)
