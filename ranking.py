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

    /* Fondo general */
    .stApp {
        background:
            radial-gradient(circle at top, #234d3b 0%, #102b21 45%, #081812 100%);
        color: #f4ead0;
    }

    /* Ocultar elementos innecesarios de Streamlit */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }

    /* Contenedor principal */
    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Cabecera */
    .titulo-principal {
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
        letter-spacing: 5px;
        color: #e8c978;
        text-shadow: 2px 2px 8px #000000;
        margin-bottom: 0.2rem;
    }

    .subtitulo {
        text-align: center;
        color: #d8d0b8;
        font-size: 1.05rem;
        letter-spacing: 2px;
        margin-bottom: 1.8rem;
    }

    .linea-dorada {
        height: 2px;
        background: linear-gradient(
            90deg,
            transparent,
            #caa84e,
            #f0d88a,
            #caa84e,
            transparent
        );
        margin: 10px 0 25px 0;
    }

    /* Logo */
    .logo-container {
        text-align: center;
        margin-bottom: 5px;
    }

    /* Títulos MCR / RIICHI */
    .seccion-titulo {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        color: #e6c76a;
        letter-spacing: 3px;
        margin-top: 10px;
        margin-bottom: 4px;
    }

    .seccion-subtitulo {
        text-align: center;
        color: #cfc7ad;
        margin-bottom: 20px;
    }

    /* Tarjetas métricas */
    div[data-testid="stMetric"] {
        background: rgba(15, 42, 31, 0.82);
        border: 1px solid rgba(214, 180, 85, 0.45);
        border-radius: 12px;
        padding: 12px 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.25);
    }

    div[data-testid="stMetricLabel"] {
        color: #cfc7ad !important;
    }

    div[data-testid="stMetricValue"] {
        color: #e8c978 !important;
    }

    /* Botones de jugadores */
    .stButton > button {
        background: rgba(27, 65, 49, 0.95);
        color: #f2df9c;
        border: 1px solid #a9893c;
        border-radius: 8px;
        font-weight: 600;
        text-align: left;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background: #315e47;
        border-color: #e8c978;
        color: white;
        transform: translateY(-1px);
    }

    /* Cabecera de tabla */
    .tabla-header {
        background: rgba(8, 25, 18, 0.9);
        border-top: 1px solid #a9893c;
        border-bottom: 1px solid #a9893c;
        border-radius: 8px;
        padding: 10px 8px;
        color: #e5ca79;
        font-weight: 700;
        font-size: 0.85rem;
        margin-bottom: 6px;
    }

    /* Fila */
    .fila-ranking {
        background: rgba(20, 53, 40, 0.75);
        border-bottom: 1px solid rgba(202,168,78,0.15);
        padding: 5px;
        border-radius: 6px;
        margin-bottom: 3px;
    }

    /* Posición */
    .posicion {
        color: #e8c978;
        font-weight: 700;
        font-size: 1.1rem;
        padding-top: 7px;
        text-align: center;
    }

    .dato {
        color: #eee5cd;
        padding-top: 8px;
        text-align: center;
    }

    /* Panel jugador */
    .jugador-panel {
        background:
            linear-gradient(
                135deg,
                rgba(29,70,51,0.96),
                rgba(10,31,22,0.98)
            );
        border: 1px solid #b49343;
        border-radius: 16px;
        padding: 25px;
        margin-top: 25px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.35);
    }

    .jugador-nombre {
        color: #edcf76;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: 2px;
        margin-bottom: 4px;
    }

    .jugador-posicion {
        color: #d7ceb4;
        font-size: 1rem;
        margin-bottom: 20px;
    }

    .estadistica {
        background: rgba(7, 25, 18, 0.65);
        border: 1px solid rgba(202,168,78,0.35);
        border-radius: 10px;
        padding: 13px;
        text-align: center;
        margin-bottom: 10px;
    }

    .estadistica-numero {
        color: #e8c978;
        font-size: 1.5rem;
        font-weight: 700;
    }

    .estadistica-texto {
        color: #cfc7ad;
        font-size: 0.8rem;
    }

    /* Separadores */
    hr {
        border-color: rgba(202,168,78,0.3);
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
    }

    /* Info */
    .stAlert {
        background: rgba(20, 55, 41, 0.8);
        border: 1px solid rgba(202,168,78,0.3);
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
        "logo mahjong madrid.png",
    ]

    for nombre in nombres:
        ruta = BASE_DIR / nombre
        if ruta.exists():
            return ruta

    # Buscar automáticamente cualquier imagen que contenga
    # mahjong y madrid en el nombre
    for ruta in BASE_DIR.iterdir():

        if not ruta.is_file():
            continue

        if ruta.suffix.lower() not in [".png", ".jpg", ".jpeg", ".webp"]:
            continue

        nombre = ruta.stem.lower()
        nombre = nombre.replace("_", "")
        nombre = nombre.replace("-", "")
        nombre = nombre.replace(" ", "")

        if "mahjong" in nombre and "madrid" in nombre:
            return ruta

    return None


LOGO = buscar_logo()


# ============================================================
# SUPABASE
# ============================================================

SUPABASE_URL = "https://gauqwlrsmxynqcokblaw.supabase.co/rest/v1"

try:
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    st.error("No se encuentra SUPABASE_KEY en los Secrets de Streamlit.")
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
            datos = json.loads(response.read().decode("utf-8"))

        return pd.DataFrame(datos)

    except Exception as e:

        st.error(f"Error al conectar con Supabase: {e}")
        st.stop()


# ============================================================
# CARGAR DATOS
# ============================================================

jugadores = supabase_get("jugadores")
partidas = supabase_get("partidas")
resultados = supabase_get("resultados_partidas")


# Comprobar columnas
columnas_jugadores = ["id", "nombre"]
columnas_partidas = ["id", "fecha", "tipo_juego"]
columnas_resultados = [
    "partida_id",
    "jugador_id",
    "posicion",
    "puntuacion"
]

for columna in columnas_jugadores:
    if columna not in jugadores.columns:
        st.error(f"Falta la columna '{columna}' en jugadores.")
        st.stop()

for columna in columnas_partidas:
    if columna not in partidas.columns:
        st.error(f"Falta la columna '{columna}' en partidas.")
        st.stop()

for columna in columnas_resultados:
    if columna not in resultados.columns:
        st.error(f"Falta la columna '{columna}' en resultados_partidas.")
        st.stop()


# ============================================================
# LIMPIEZA
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
            Primero=("posicion", lambda x: (x == 1).sum()),
            Segundo=("posicion", lambda x: (x == 2).sum()),
            Tercero=("posicion", lambda x: (x == 3).sum()),
            Cuarto=("posicion", lambda x: (x == 4).sum()),
            Quinto=("posicion", lambda x: (x == 5).sum()),
            MejorPosicion=("posicion", "min")
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
# ESTADÍSTICAS DEL JUGADOR
# ============================================================

def mostrar_jugador(jugador_id, tipo, ranking):

    fila = ranking[
        ranking["jugador_id"] == jugador_id
    ]

    if fila.empty:
        return

    jugador = fila.iloc[0]

    st.markdown(
        f"""
        <div class="jugador-panel">

            <div class="jugador-nombre">
                👤 {jugador['Jugador']}
            </div>

            <div class="jugador-posicion">
                Ranking {tipo} · Posición #{int(jugador['Pos.'])}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # Métricas principales
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="estadistica">
                <div class="estadistica-numero">
                    #{int(jugador['Pos.'])}
                </div>
                <div class="estadistica-texto">
                    POSICIÓN
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="estadistica">
                <div class="estadistica-numero">
                    {int(jugador['Puntos'])}
                </div>
                <div class="estadistica-texto">
                    PUNTOS
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class="estadistica">
                <div class="estadistica-numero">
                    {int(jugador['Partidas'])}
                </div>
                <div class="estadistica-texto">
                    PARTIDAS
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            f"""
            <div class="estadistica">
                <div class="estadistica-numero">
                    {jugador['Media']:.1f}
                </div>
                <div class="estadistica-texto">
                    MEDIA
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("### 🏅 Resultados")

    c1, c2, c3, c4, c5 = st.columns(5)

    posiciones = [
        ("🥇", "1º", jugador["1º"]),
        ("🥈", "2º", jugador["2º"]),
        ("🥉", "3º", jugador["3º"]),
        ("4️⃣", "4º", jugador["4º"]),
        ("5️⃣", "5º", jugador["5º"]),
    ]

    for col, (emoji, nombre, valor) in zip(
        [c1, c2, c3, c4, c5],
        posiciones
    ):

        with col:

            st.markdown(
                f"""
                <div class="estadistica">
                    <div style="font-size:1.3rem;">
                        {emoji}
                    </div>
                    <div class="estadistica-numero">
                        {int(valor)}
                    </div>
                    <div class="estadistica-texto">
                        {nombre}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("### 📜 Historial de partidas")

    historial = datos[
        (datos["jugador_id"] == jugador_id) &
        (datos["tipo_juego"] == tipo)
    ].copy()

    if historial.empty:

        st.info("No hay partidas registradas.")

    else:

        historial = historial.sort_values(
            by="fecha",
            ascending=False
        )

        historial["Posición"] = historial["posicion"].apply(
            lambda x: f"{int(x)}º"
            if pd.notna(x)
            else "-"
        )

        historial["Puntos"] = historial[
            "puntuacion"
        ].astype(int)

        historial["Fecha"] = historial[
            "fecha"
        ].astype(str)

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


# ============================================================
# MOSTRAR RANKING
# ============================================================

def mostrar_ranking(tipo):

    ranking = crear_ranking(tipo)

    if ranking.empty:

        st.info(
            f"Todavía no hay partidas de {tipo}."
        )

        return

    # --------------------------------------------------------
    # TÍTULO
    # --------------------------------------------------------

    icono = "🀄" if tipo == "MCR" else "🎴"

    st.markdown(
        f"""
        <div class="seccion-titulo">
            {icono} {tipo}
        </div>

        <div class="seccion-subtitulo">
            Clasificación de la Liga Mahjong Madrid
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # RESUMEN
    # --------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "👥 Jugadores",
            len(ranking)
        )

    with c2:
        st.metric(
            "🎲 Partidas",
            datos[
                datos["tipo_juego"] == tipo
            ]["partida_id"].nunique()
        )

    with c3:
        st.metric(
            "🏆 Líder",
            ranking.iloc[0]["Jugador"]
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # CABECERA
    # --------------------------------------------------------

    columnas = st.columns(
        [0.6, 3.4, 1.2, 1.2, 1.2, 0.8]
    )

    cabeceras = [
        "POS.",
        "JUGADOR",
        "PUNTOS",
        "PARTIDAS",
        "MEDIA",
        "🥇"
    ]

    for col, texto in zip(columnas, cabeceras):

        with col:
            st.markdown(
                f"""
                <div class="tabla-header">
                    {texto}
                </div>
                """,
                unsafe_allow_html=True
            )

    # --------------------------------------------------------
    # FILAS
    # --------------------------------------------------------

    for _, jugador in ranking.iterrows():

        jugador_id = jugador["jugador_id"]

        columnas = st.columns(
            [0.6, 3.4, 1.2, 1.2, 1.2, 0.8]
        )

        # Posición
        with columnas[0]:

            posicion = int(jugador["Pos."])

            if posicion == 1:
                texto_pos = "🥇"
            elif posicion == 2:
                texto_pos = "🥈"
            elif posicion == 3:
                texto_pos = "🥉"
            else:
                texto_pos = str(posicion)

            st.markdown(
                f"""
                <div class="posicion">
                    {texto_pos}
                </div>
                """,
                unsafe_allow_html=True
            )

        # Nombre clickable
        with columnas[1]:

            if st.button(
                str(jugador["Jugador"]),
                key=f"btn_{tipo}_{jugador_id}",
                use_container_width=True
            ):

                st.session_state[
                    "jugador_seleccionado"
                ] = jugador_id

                st.session_state[
                    "tipo_seleccionado"
                ] = tipo

        # Puntos
        with columnas[2]:

            st.markdown(
                f"""
                <div class="dato">
                    <strong>{int(jugador['Puntos'])}</strong>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Partidas
        with columnas[3]:

            st.markdown(
                f"""
                <div class="dato">
                    {int(jugador['Partidas'])}
                </div>
                """,
                unsafe_allow_html=True
            )

        # Media
        with columnas[4]:

            st.markdown(
                f"""
                <div class="dato">
                    {jugador['Media']:.1f}
                </div>
                """,
                unsafe_allow_html=True
            )

        # Primeros
        with columnas[5]:

            st.markdown(
                f"""
                <div class="dato">
                    {int(jugador['1º'])}
                </div>
                """,
                unsafe_allow_html=True
            )

    # --------------------------------------------------------
    # JUGADOR SELECCIONADO
    # --------------------------------------------------------

    if (
        "jugador_seleccionado" in st.session_state
        and st.session_state.get(
            "tipo_seleccionado"
        ) == tipo
    ):

        st.markdown(
            '<div class="linea-dorada"></div>',
            unsafe_allow_html=True
        )

        mostrar_jugador(
            st.session_state["jugador_seleccionado"],
            tipo,
            ranking
        )

        if st.button(
            "✕ Cerrar estadísticas",
            key=f"cerrar_{tipo}"
        ):

            del st.session_state[
                "jugador_seleccionado"
            ]

            del st.session_state[
                "tipo_seleccionado"
            ]

            st.rerun()


# ============================================================
# CABECERA PRINCIPAL
# ============================================================

if LOGO is not None:

    st.markdown(
        '<div class="logo-container">',
        unsafe_allow_html=True
    )

    st.image(
        str(LOGO),
        width=180
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

else:

    st.markdown(
        """
        <div style="
            text-align:center;
            font-size:4rem;
        ">
            🀄
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown(
    '<div class="titulo-principal">LIGA MAHJONG MADRID</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">CLASIFICACIÓN · ESTADÍSTICAS · RESULTADOS</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="linea-dorada"></div>',
    unsafe_allow_html=True
)


# ============================================================
# TABS MCR / RIICHI
# ============================================================

tab_mcr, tab_riichi = st.tabs(
    ["🀄  MCR", "🎴  RIICHI"]
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
    <br><br>
    <div style="
        text-align:center;
        color:#8f927f;
        font-size:0.8rem;
        letter-spacing:1px;
    ">
        MAHJONG MADRID · LIGA OFICIAL
    </div>
    """,
    unsafe_allow_html=True
)
