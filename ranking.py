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
    background: #0b2418 !important;
    color: #f5e8c5 !important;
}

.main {
    background: #0b2418 !important;
}

.block-container {
    background: #0b2418 !important;
    max-width: 1250px;
    padding-top: 25px;
    padding-bottom: 40px;
}

[data-testid="stAppViewContainer"] {
    background: #0b2418 !important;
}

[data-testid="stMain"] {
    background: #0b2418 !important;
}

header[data-testid="stHeader"] {
    background: #0b2418 !important;
}

footer {
    background: #0b2418 !important;
}


/* =====================================================
   CABECERA
   ===================================================== */

.cabecera {
    padding: 10px 0 20px 0;
}

.titulo-principal {
    color: #e2c36c;
    font-size: 3rem;
    font-weight: 900;
    letter-spacing: 4px;
    margin: 0;
    line-height: 1.1;
}

.subtitulo {
    color: #d9cfae;
    font-size: 1rem;
    letter-spacing: 2px;
    margin-top: 8px;
}


/* =====================================================
   BOTONES MCR / RIICHI
   ===================================================== */

.selector-juego {
    margin-top: 20px;
    margin-bottom: 25px;
}

.selector-juego button {
    width: 100%;
    min-height: 90px !important;
    height: 90px !important;

    border-radius: 16px !important;

    font-size: 1.9rem !important;
    font-weight: 900 !important;
    letter-spacing: 3px !important;

    transition: all 0.2s ease;
}


/* NO SELECCIONADO */

.selector-normal button {
    background-color: #173629 !important;
    color: #f5e8c5 !important;

    border: 3px solid #b89445 !important;
}

.selector-normal button:hover {
    background-color: #234c39 !important;
    border-color: #e2c36c !important;
    color: #ffffff !important;
}


/* SELECCIONADO */

.selector-activo button {
    background-color: #e2c36c !important;
    color: #17271e !important;

    border: 3px solid #e2c36c !important;
}

.selector-activo button:hover {
    background-color: #efd47f !important;
    color: #17271e !important;
}


/* =====================================================
   CABECERA DEL RANKING
   ===================================================== */

.ranking-cabecera {
    background: #10291d;
    border: 1px solid #8f7538;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 8px;
    color: #e2c36c;
    font-weight: 800;
    letter-spacing: 1px;
}


/* =====================================================
   FILAS DEL RANKING
   ===================================================== */

.ranking-fila {
    background: #133123;
    border: 1px solid rgba(184, 148, 69, 0.45);
    border-radius: 12px;
    padding: 8px 12px;
    margin-bottom: 7px;
    align-items: center;
}

.ranking-fila:hover {
    background: #1c4734;
}


/* =====================================================
   POSICIONES Y VALORES
   ===================================================== */

.numero-posicion {
    color: #e2c36c;
    font-size: 1.2rem;
    font-weight: 800;
    text-align: center;
}

.valor-ranking {
    color: #f5e8c5;
    font-size: 1.1rem;
    font-weight: 700;
    text-align: center;
}


/* =====================================================
   NOMBRE DEL JUGADOR
   ===================================================== */

.jugador-boton button {
    background: transparent !important;
    border: none !important;
    color: #f5e8c5 !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    text-align: left !important;
    padding: 8px 4px !important;
}

.jugador-boton button:hover {
    color: #e2c36c !important;
    background: transparent !important;
}


/* =====================================================
   PANEL DEL JUGADOR
   ===================================================== */

.panel-jugador {
    background: #10291d;
    border: 2px solid #b89445;
    border-radius: 18px;
    padding: 25px;
    margin-top: 25px;
    margin-bottom: 30px;
}

.nombre-jugador {
    color: #e2c36c;
    font-size: 2.2rem;
    font-weight: 900;
    letter-spacing: 2px;
    margin-bottom: 5px;
}

.tipo-jugador {
    color: #d9cfae;
    font-size: 1rem;
    letter-spacing: 2px;
    margin-bottom: 20px;
}


/* =====================================================
   MÉTRICAS
   ===================================================== */

[data-testid="stMetric"] {
    background: #173629 !important;
    border: 1px solid #8f7538 !important;
    border-radius: 12px;
    padding: 16px;
}

[data-testid="stMetricLabel"] {
    color: #d9cfae !important;
    font-weight: 700 !important;
}

[data-testid="stMetricValue"] {
    color: #e2c36c !important;
    font-weight: 900 !important;
}


/* =====================================================
   TÍTULOS
   ===================================================== */

h1, h2, h3 {
    color: #e2c36c !important;
}


/* =====================================================
   BOTÓN CERRAR
   ===================================================== */

.cerrar button {
    border: 1px solid #b89445 !important;
    color: #f5e8c5 !important;
    background: #173629 !important;
    border-radius: 10px !important;
}

.cerrar button:hover {
    background: #b89445 !important;
    color: #17271e !important;
}


/* =====================================================
   TABLA HISTORIAL
   ===================================================== */

[data-testid="stDataFrame"] {
    border: 1px solid #8f7538 !important;
    border-radius: 10px !important;
}


/* =====================================================
   FOOTER
   ===================================================== */

.footer {
    text-align: center;
    color: #8f9d91;
    font-size: 0.8rem;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid rgba(184, 148, 69, 0.25);
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
# MOSTRAR ESTADÍSTICAS DEL JUGADOR
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
        f'<div class="nombre-jugador">'
        f'{jugador["Jugador"]}'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="tipo-jugador">'
        f'RANKING {tipo} · '
        f'POSICIÓN #{posicion_ranking}'
        f'</div>',
        unsafe_allow_html=True
    )


    # =====================================================
    # MÉTRICAS
    # =====================================================

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


    # =====================================================
    # RESULTADOS
    # =====================================================

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


    # =====================================================
    # HISTORIAL
    # =====================================================

    st.markdown("### HISTORIAL DE PARTIDAS")

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


    # =====================================================
    # CERRAR
    # =====================================================

    st.markdown(
        '<div class="cerrar">',
        unsafe_allow_html=True
    )


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


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


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


    # =====================================================
    # CABECERA
    # =====================================================

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


    # =====================================================
    # FILAS
    # =====================================================

    for _, jugador in ranking.iterrows():

        jugador_id = jugador["jugador_id"]

        fila = st.columns(
            [0.7, 3, 1.2, 1.2, 1.2, 0.8]
        )


        # POSICIÓN

        with fila[0]:

            st.markdown(
                f'<div class="numero-posicion">'
                f'{int(jugador["Pos."])}'
                f'</div>',
                unsafe_allow_html=True
            )


        # JUGADOR

        with fila[1]:

            st.markdown(
                '<div class="jugador-boton">',
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
                f'<div class="valor-ranking">'
                f'{int(jugador["Puntos"])}'
                f'</div>',
                unsafe_allow_html=True
            )


        # PARTIDAS

        with fila[3]:

            st.markdown(
                f'<div class="valor-ranking">'
                f'{int(jugador["Partidas"])}'
                f'</div>',
                unsafe_allow_html=True
            )


        # MEDIA

        with fila[4]:

            st.markdown(
                f'<div class="valor-ranking">'
                f'{jugador["Media"]:.1f}'
                f'</div>',
                unsafe_allow_html=True
            )


        # PRIMEROS

        with fila[5]:

            st.markdown(
                f'<div class="valor-ranking">'
                f'{int(jugador["Primeros"])}'
                f'</div>',
                unsafe_allow_html=True
            )


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

        st.markdown(
            "🀄"
        )


with col_titulo:

    st.markdown(
        '<div class="cabecera">',
        unsafe_allow_html=True
    )

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

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# =========================================================
# ESTADO
# =========================================================

if "tipo_juego" not in st.session_state:

    st.session_state[
        "tipo_juego"
    ] = "MCR"


if "jugador_seleccionado" not in st.session_state:

    st.session_state[
        "jugador_seleccionado"
    ] = None


# =========================================================
# BOTONES GRANDES MCR / RIICHI
# =========================================================

col_mcr, col_riichi = st.columns(
    2,
    gap="medium"
)


# =========================================================
# MCR
# =========================================================

with col_mcr:

    if st.session_state["tipo_juego"] == "MCR":

        st.markdown(
            '<div class="selector-juego selector-activo">',
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            '<div class="selector-juego selector-normal">',
            unsafe_allow_html=True
        )


    if st.button(
        "🀄   MCR",
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


# =========================================================
# RIICHI
# =========================================================

with col_riichi:

    if st.session_state["tipo_juego"] == "RIICHI":

        st.markdown(
            '<div class="selector-juego selector-activo">',
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            '<div class="selector-juego selector-normal">',
            unsafe_allow_html=True
        )


    if st.button(
        "🎴   RIICHI",
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
# RANKING
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
