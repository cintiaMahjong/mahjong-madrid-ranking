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
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE_DIR = Path(__file__).parent


# ============================================================
# ESTILO
# ============================================================

st.markdown("""
<style>

    /* ========================================================
       GENERAL
       ======================================================== */

    .stApp {
        background: #102b21;
        color: #f5edd9;
    }

    .block-container {
        max-width: 1150px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }


    /* ========================================================
       CABECERA
       ======================================================== */

    .titulo-principal {
        text-align: left;
        color: #e2c36c;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: 4px;
        margin-top: 0;
        margin-bottom: 4px;
        text-shadow: 0 2px 5px rgba(0,0,0,0.5);
    }

    .subtitulo {
        text-align: left;
        color: #d8d0bd;
        font-size: 0.9rem;
        letter-spacing: 2px;
        margin-bottom: 0;
    }

    .linea-dorada {
        height: 1px;
        background: #b99a48;
        margin: 15px 0 25px 0;
    }


    /* ========================================================
       PESTAÑAS GRANDES
       ======================================================== */

    div[data-baseweb="tab-list"] {
        width: 100%;
        background: #091b14;
        border: 2px solid #8f7538;
        border-radius: 14px;
        padding: 7px;
        gap: 8px;
        margin-top: 20px;
        margin-bottom: 30px;
    }

    button[data-baseweb="tab"] {
        flex: 1;
        color: #eee5d0 !important;
        font-size: 1.45rem !important;
        font-weight: 700 !important;
        letter-spacing: 3px;
        padding: 16px 25px !important;
        min-height: 62px !important;
        border-radius: 10px !important;
        background: transparent !important;
    }

    button[data-baseweb="tab"]:hover {
        color: #ffffff !important;
        background: #214936 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #17271e !important;
        background: #e2c36c !important;
    }

    div[data-baseweb="tab-highlight"] {
        background: transparent !important;
    }

    div[data-baseweb="tab-border"] {
        background: transparent !important;
    }


    /* ========================================================
       TÍTULO DEL JUEGO
       ======================================================== */

    .titulo-juego {
        text-align: center;
        color: #e2c36c;
        font-size: 1.8rem;
        font-weight: 700;
        letter-spacing: 3px;
        margin-top: 5px;
        margin-bottom: 20px;
    }


    /* ========================================================
       TABLA
       ======================================================== */

    .cabecera-tabla {
        background: #0b2118;
        border-top: 1px solid #9f833d;
        border-bottom: 1px solid #9f833d;
        border-radius: 6px;
        padding: 10px 5px;
        color: #e2c36c;
        font-size: 0.78rem;
        font-weight: 700;
        text-align: center;
    }

    .dato-tabla {
        color: #f3ead5;
        text-align: center;
        padding-top: 9px;
        font-size: 0.95rem;
    }

    .posicion-tabla {
        color: #e2c36c;
        font-weight: 700;
        text-align: center;
        padding-top: 8px;
        font-size: 1rem;
    }


    /* ========================================================
       BOTÓN JUGADOR
       ======================================================== */

    .stButton > button {
        background: #183b2c;
        color: #f4e5b6;
        border: 1px solid #8e7538;
        border-radius: 6px;
        font-size: 0.95rem;
        font-weight: 600;
        text-align: left;
        padding: 6px 12px;
        min-height: 38px;
    }

    .stButton > button:hover {
        background: #24543e;
        color: #ffffff;
        border-color: #d9ba62;
    }


    /* ========================================================
       PANEL JUGADOR
       ======================================================== */

    .panel-jugador {
        background: #0b2118;
        border: 1px solid #9f833d;
        border-radius: 12px;
        padding: 22px;
        margin-top: 25px;
        margin-bottom: 20px;
    }

    .nombre-jugador {
        color: #e2c36c;
        font-size: 1.7rem;
        font-weight: 700;
        margin-bottom: 3px;
    }

    .posicion-jugador {
        color: #cfc6af;
        font-size: 0.9rem;
    }


    /* ========================================================
       ESTADÍSTICAS
       ======================================================== */

    .estadistica-box {
        background: #143528;
        border: 1px solid #6f7046;
        border-radius: 9px;
        padding: 15px 8px;
        text-align: center;
        min-height: 75px;
    }

    .estadistica-numero {
        color: #e2c36c;
        font-size: 1.5rem;
        font-weight: 700;
    }

    .estadistica-label {
        color: #ddd4bf;
        font-size: 0.75rem;
        margin-top: 4px;
    }


    /* ========================================================
       HISTORIAL
       ======================================================== */

    .titulo-historial {
        color: #e2c36c;
        font-size: 1.15rem;
        font-weight: 600;
        margin-top: 25px;
        margin-bottom: 10px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOGO
# ============================================================

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
            ruta.stem
            .lower()
            .replace("_", "")
            .replace("-", "")
            .replace(" ", "")
        )

        if "mahjong" in nombre and "madrid" in nombre:
            return ruta

    return None


LOGO = buscar_logo()


# ============================================================
# SUPABASE
# ============================================================

SUPABASE_URL = (
    "https://gauqwlrsmxynqcokblaw.supabase.co/rest/v1"
)

try:

    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

except Exception:

    st.error(
        "No se encuentra SUPABASE_KEY en los Secrets de Streamlit."
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

            datos = json.loads(
                response.read().decode("utf-8")
            )

        return pd.DataFrame(datos)

    except Exception as e:

        st.error(
            f"Error al conectar con Supabase: {e}"
        )

        st.stop()


# ============================================================
# CARGAR DATOS
# ============================================================

jugadores = supabase_get("jugadores")
partidas = supabase_get("partidas")
resultados = supabase_get("resultados_partidas")


# ============================================================
# COMPROBAR COLUMNAS
# ============================================================

for columna in ["id", "nombre"]:

    if columna not in jugadores.columns:
        st.error(
            f"Falta la columna '{columna}' en jugadores."
        )
        st.stop()


for columna in ["id", "fecha", "tipo_juego"]:

    if columna not in partidas.columns:
        st.error(
            f"Falta la columna '{columna}' en partidas."
        )
        st.stop()


for columna in [
    "partida_id",
    "jugador_id",
    "posicion",
    "puntuacion"
]:

    if columna not in resultados.columns:
        st.error(
            f"Falta la columna '{columna}' "
            "en resultados_partidas."
        )
        st.stop()


# ============================================================
# CONVERSIÓN
# ============================================================

jugadores["id"] = pd.to_numeric(
    jugadores["id"],
    errors="coerce"
)

partidas["id"] = pd.to_numeric(
    partidas["id"],
    errors="coerce"
)

resultados["partida_id"] = pd.to_numeric(
    resultados["partida_id"],
    errors="coerce"
)

resultados["jugador_id"] = pd.to_numeric(
    resultados["jugador_id"],
    errors="coerce"
)

resultados["posicion"] = pd.to_numeric(
    resultados["posicion"],
    errors="coerce"
)

resultados["puntuacion"] = pd.to_numeric(
    resultados["puntuacion"],
    errors="coerce"
).fillna(0)


# ============================================================
# UNIR TABLAS
# ============================================================

datos = resultados.merge(
    partidas[["id", "fecha", "tipo_juego"]],
    left_on="partida_id",
    right_on="id",
    how="left"
)

datos = datos.merge(
    jugadores[["id", "nombre"]],
    left_on="jugador_id",
    right_on="id",
    how="left"
)

datos["tipo_juego"] = (
    datos["tipo_juego"]
    .astype(str)
    .str.strip()
    .str.upper()
)


# ============================================================
# CREAR RANKING
# ============================================================

def crear_ranking(tipo):

    df = datos[
        datos["tipo_juego"] == tipo
    ].copy()

    if df.empty:
        return pd.DataFrame()

    ranking = (
        df.groupby(
            ["jugador_id", "nombre"],
            dropna=False
        )
        .agg(
            Partidas=("partida_id", "nunique"),

            Puntos=("puntuacion", "sum"),

            Primero=(
                "posicion",
                lambda x: (x == 1).sum()
            ),

            Segundo=(
                "posicion",
                lambda x: (x == 2).sum()
            ),

            Tercero=(
                "posicion",
                lambda x: (x == 3).sum()
            ),

            Cuarto=(
                "posicion",
                lambda x: (x == 4).sum()
            ),

            Quinto=(
                "posicion",
                lambda x: (x == 5).sum()
            ),

            MejorPosicion=(
                "posicion",
                "min"
            )
        )
        .reset_index()
    )

    ranking["Media"] = (
        ranking["Puntos"] /
        ranking["Partidas"]
    ).round(1)

    ranking = ranking.sort_values(
        by=["Puntos", "Primero"],
        ascending=[False, False]
    ).reset_index(drop=True)

    ranking["Pos."] = ranking.index + 1

    ranking = ranking.rename(
        columns={
            "nombre": "Jugador",
            "Primero": "1º",
            "Segundo": "2º",
            "Tercero": "3º",
            "Cuarto": "4º",
            "Quinto": "5º",
            "MejorPosicion": "Mejor posición"
        }
    )

    return ranking


# ============================================================
# MOSTRAR ESTADÍSTICAS DEL JUGADOR
# ============================================================

def mostrar_jugador(
    jugador_id,
    tipo,
    ranking
):

    fila = ranking[
        ranking["jugador_id"] == jugador_id
    ]

    if fila.empty:
        return

    jugador = fila.iloc[0]

    # --------------------------------------------------------
    # NOMBRE
    # --------------------------------------------------------

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
        f'<div class="posicion-jugador">'
        f'{tipo} · Posición {int(jugador["Pos."])}'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # ESTADÍSTICAS PRINCIPALES
    # --------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(
            '<div class="estadistica-box">',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="estadistica-numero">'
            f'{int(jugador["Puntos"])}'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="estadistica-label">'
            'PUNTOS'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            '<div class="estadistica-box">',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="estadistica-numero">'
            f'{int(jugador["Partidas"])}'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="estadistica-label">'
            'PARTIDAS'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    with c3:

        st.markdown(
            '<div class="estadistica-box">',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="estadistica-numero">'
            f'{jugador["Media"]:.1f}'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="estadistica-label">'
            'MEDIA'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # RESULTADOS
    # --------------------------------------------------------

    st.markdown(
        '<div class="titulo-historial">'
        'Resultados'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    resultados_posicion = [
        ("🥇", jugador["1º"]),
        ("🥈", jugador["2º"]),
        ("🥉", jugador["3º"]),
        ("4º", jugador["4º"]),
        ("5º", jugador["5º"])
    ]

    for col, (posicion, cantidad) in zip(
        [c1, c2, c3, c4, c5],
        resultados_posicion
    ):

        with col:

            # IMPORTANTE:
            # No usamos HTML para el número.
            # Streamlit lo muestra directamente.

            st.markdown(
                f"""
                <div class="estadistica-box">
                    <div style="font-size:1.15rem;">
                        {posicion}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                f"### {int(cantidad)}",
            )

    # --------------------------------------------------------
    # HISTORIAL
    # --------------------------------------------------------

    st.markdown(
        '<div class="titulo-historial">'
        'Historial de partidas'
        '</div>',
        unsafe_allow_html=True
    )

    historial = datos[
        (datos["jugador_id"] == jugador_id) &
        (datos["tipo_juego"] == tipo)
    ].copy()

    if historial.empty:

        st.info(
            "No hay partidas registradas."
        )

    else:

        historial = historial.sort_values(
            by="fecha",
            ascending=False
        )

        historial["Fecha"] = (
            historial["fecha"]
            .astype(str)
        )

        historial["Posición"] = (
            historial["posicion"]
            .apply(
                lambda x:
                f"{int(x)}º"
                if pd.notna(x)
                else "-"
            )
        )

        historial["Puntos"] = (
            historial["puntuacion"]
            .astype(int)
        )

        historial = historial[
            [
                "Fecha",
                "Posición",
                "Puntos"
            ]
        ]

        st.dataframe(
            historial,
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # CERRAR
    # --------------------------------------------------------

    if st.button(
        "Cerrar estadísticas",
        key=f"cerrar_{tipo}_{jugador_id}"
    ):

        st.session_state.pop(
            "jugador_seleccionado",
            None
        )

        st.session_state.pop(
            "tipo_seleccionado",
            None
        )

        st.rerun()


# ============================================================
# MOSTRAR RANKING
# ============================================================

def mostrar_ranking(tipo):

    ranking = crear_ranking(tipo)

    if ranking.empty:

        st.info(
            f"No hay partidas de {tipo}."
        )

        return

    icono = "🀄" if tipo == "MCR" else "🎴"

    st.markdown(
        f'<div class="titulo-juego">'
        f'{icono} {tipo}'
        f'</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # CABECERA
    # --------------------------------------------------------

    columnas = st.columns(
        [0.7, 3.5, 1.3, 1.3, 1.3, 0.8]
    )

    nombres = [
        "POS.",
        "JUGADOR",
        "PUNTOS",
        "PARTIDAS",
        "MEDIA",
        "🥇"
    ]

    for col, nombre in zip(
        columnas,
        nombres
    ):

        with col:

            st.markdown(
                f'<div class="cabecera-tabla">'
                f'{nombre}'
                f'</div>',
                unsafe_allow_html=True
            )

    # --------------------------------------------------------
    # FILAS
    # --------------------------------------------------------

    for _, jugador in ranking.iterrows():

        jugador_id = jugador["jugador_id"]

        columnas = st.columns(
            [0.7, 3.5, 1.3, 1.3, 1.3, 0.8]
        )

        # POSICIÓN
        with columnas[0]:

            posicion = int(jugador["Pos."])

            if posicion == 1:
                texto = "🥇"
            elif posicion == 2:
                texto = "🥈"
            elif posicion == 3:
                texto = "🥉"
            else:
                texto = str(posicion)

            st.markdown(
                f'<div class="posicion-tabla">'
                f'{texto}'
                f'</div>',
                unsafe_allow_html=True
            )

        # JUGADOR
        with columnas[1]:

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

        # PUNTOS
        with columnas[2]:

            st.markdown(
                f'<div class="dato-tabla">'
                f'<strong>{int(jugador["Puntos"])}</strong>'
                f'</div>',
                unsafe_allow_html=True
            )

        # PARTIDAS
        with columnas[3]:

            st.markdown(
                f'<div class="dato-tabla">'
                f'{int(jugador["Partidas"])}'
                f'</div>',
                unsafe_allow_html=True
            )

        # MEDIA
        with columnas[4]:

            st.markdown(
                f'<div class="dato-tabla">'
                f'{jugador["Media"]:.1f}'
                f'</div>',
                unsafe_allow_html=True
            )

        # PRIMEROS
        with columnas[5]:

            st.markdown(
                f'<div class="dato-tabla">'
                f'{int(jugador["1º"])}'
                f'</div>',
                unsafe_allow_html=True
            )

    # --------------------------------------------------------
    # JUGADOR SELECCIONADO
    # --------------------------------------------------------

    if (
        "jugador_seleccionado" in st.session_state
        and
        st.session_state.get(
            "tipo_seleccionado"
        ) == tipo
    ):

        st.markdown(
            '<div class="linea-dorada"></div>',
            unsafe_allow_html=True
        )

        mostrar_jugador(
            st.session_state[
                "jugador_seleccionado"
            ],
            tipo,
            ranking
        )


# ============================================================
# CABECERA PRINCIPAL
# ============================================================

cabecera_logo, cabecera_titulo = st.columns(
    [1, 5],
    vertical_alignment="center"
)

with cabecera_logo:

    if LOGO is not None:

        st.image(
            str(LOGO),
            width=150
        )

with cabecera_titulo:

    st.markdown(
        """
        <div class="titulo-principal">
            LIGA MAHJONG MADRID
        </div>

        <div class="subtitulo">
            CLASIFICACIÓN Y ESTADÍSTICAS
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown(
    '<div class="linea-dorada"></div>',
    unsafe_allow_html=True
)


# ============================================================
# PESTAÑAS
# ============================================================

tab_mcr, tab_riichi = st.tabs(
    ["🀄   MCR", "🎴   RIICHI"]
)

with tab_mcr:

    mostrar_ranking("MCR")


with tab_riichi:

    mostrar_ranking("RIICHI")


# ============================================================
# PIE
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#8f927f;
        font-size:0.75rem;
        margin-top:40px;
        letter-spacing:1px;
    ">
        @C. HORCAJO
    </div>
    """,
    unsafe_allow_html=True
)
