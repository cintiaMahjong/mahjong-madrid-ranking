import streamlit as st
import pandas as pd
import urllib.request
import urllib.parse
import json
import os
RUTA_LOGO = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "logo_mahjong_madrid.png"
)
st.set_page_config(
    page_title="Liga Mahjong Madrid",
    page_icon=RUTA_LOGO if os.path.exists(RUTA_LOGO) else "🀄",
    layout="centered"
)
SUPABASE_URL = "https://gauqwlrsmxynqcokblaw.supabase.co/rest/v1"
st.markdown("""
<style>
/* -----------------------------
   BASE
------------------------------ */
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}
.block-container {
    max-width: 1000px;
    padding: 1rem 1rem 2rem 1rem;
}
/* Fondo limpio */
.stApp {
    background: #ffffff;
}
/* Títulos */
h1, h2, h3 {
    color: #111111 !important;
}
h1 {
    font-size: 2rem !important;
    font-weight: 800 !important;
}
h2 {
    font-size: 1.45rem !important;
}
h3 {
    font-size: 1.15rem !important;
}
/* Botones generales */
.stButton > button {
    border-radius: 9px;
    border: 1px solid #d6d6d6;
    min-height: 42px;
    font-weight: 600;
}
.stButton > button:hover {
    border-color: #b40000;
}
/* Selector MCR / RIICHI */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    width: 100%;
}
.stTabs [data-baseweb="tab"] {
    flex: 1;
    justify-content: center;
    font-size: 1rem;
    font-weight: 700;
    min-height: 48px;
}
/* Radio de ordenación */
div[role="radiogroup"] {
    gap: 8px;
}
div[role="radiogroup"] label {
    border: 1px solid #d9d9d9;
    border-radius: 9px;
    padding: 7px 12px;
    background: #ffffff;
}
/* Métricas */
[data-testid="stMetric"] {
    border: 1px solid #e2e2e2;
    border-radius: 10px;
    padding: 10px;
    background: #fafafa;
}
[data-testid="stMetricLabel"] {
    font-size: .75rem;
}
[data-testid="stMetricValue"] {
    font-size: 1.35rem;
}
/* Cabecera del ranking */
.ranking-header {
    display: grid;
    grid-template-columns: 55px minmax(0, 1fr) 95px 70px 70px 90px 75px 75px 90px;
    gap: 6px;
    align-items: center;
    background: #b90000;
    color: white;
    border-radius: 10px 10px 0 0;
    padding: 12px 10px;
    font-weight: 800;
    font-size: .82rem;
}
.ranking-row {
    display: grid;
    grid-template-columns: 55px minmax(0, 1fr) 95px 70px 70px 90px 75px 75px 90px;
    gap: 6px;
    align-items: center;
    min-height: 54px;
    padding: 7px 10px;
    border: 1px solid #e5e5e5;
    border-top: 0;
    background: #ffffff;
    font-size: .9rem;
}
.ranking-row:nth-child(even) {
    background: #fff9df;
}
.ranking-position {
    text-align: center;
    font-weight: 800;
}
.ranking-name {
    font-weight: 600;
    line-height: 1.2;
}
.ranking-value {
    text-align: center;
    font-weight: 700;
}
/* -----------------------------
   RANKING MÓVIL
------------------------------ */
.mobile-ranking-header {
    display: grid;
    grid-template-columns: 42px minmax(0, 1fr) 78px;
    gap: 4px;
    align-items: center;
    width: 100%;
    box-sizing: border-box;
    background: #b90000;
    color: white;
    border-radius: 8px 8px 0 0;
    padding: 10px 8px;
    font-size: .74rem;
    line-height: 1;
    font-weight: 800;
}
.mobile-ranking-row {
    display: grid;
    grid-template-columns: 42px minmax(0, 1fr) 78px;
    gap: 4px;
    align-items: center;
    min-height: 54px;
    box-sizing: border-box;
    padding: 4px 7px;
    border: 1px solid #e3e3e3;
    border-top: 0;
    background: #ffffff;
}
.mobile-position {
    text-align: center;
    font-size: 1.05rem;
    line-height: 1;
    font-weight: 800;
}
.mobile-name-button button {
    width: 100%;
    min-height: 42px !important;
    height: auto !important;
    text-align: left !important;
    justify-content: flex-start !important;
    border: 0 !important;
    background: transparent !important;
    padding: 3px 2px !important;
    margin: 0 !important;
    font-size: .88rem !important;
    line-height: 1.15 !important;
    font-weight: 600 !important;
    color: #111111 !important;
    box-shadow: none !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
}
.mobile-name-button button:hover {
    color: #b40000 !important;
}
.mobile-main-value {
    text-align: right;
    padding-right: 2px;
    font-size: .88rem;
    line-height: 1;
    font-weight: 800;
    white-space: nowrap;
}
/* Ficha */
.player-title {
    font-size: 1.45rem;
    font-weight: 800;
    color: #111111;
    margin: 8px 0 12px 0;
}
.match-header {
    background: #f2f7f3;
    color: #17612e;
    border-left: 4px solid #17612e;
    padding: 9px 12px;
    border-radius: 7px;
    margin-top: 13px;
    margin-bottom: 5px;
    font-weight: 700;
}
.match-col-header {
    font-size: .78rem;
    color: #666666;
    font-weight: 700;
    padding: 4px 5px;
}
.match-cell {
    background: #ffffff;
    border-bottom: 1px solid #eeeeee;
    padding: 7px 5px;
    font-size: .9rem;
}
.match-cell-selected {
    background: #fff8d9;
    border-bottom: 1px solid #eadf9c;
    padding: 7px 5px;
    font-weight: 700;
    font-size: .9rem;
}
/* Ocultamos elementos de escritorio/móvil según ancho.
   La detección final también usa User-Agent. */
.desktop-only { display: block; }
.mobile-only { display: none; }
@media (max-width: 700px) {
    .block-container {
        max-width: 100%;
        padding: .55rem .45rem 1.5rem .45rem;
    }
    h1 {
        font-size: 1.55rem !important;
        line-height: 1.1 !important;
    }
    h2 {
        font-size: 1.25rem !important;
    }
    h3 {
        font-size: 1.05rem !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: .92rem;
        min-height: 45px;
    }
    div[role="radiogroup"] {
        display: flex;
        flex-wrap: wrap;
    }
    div[role="radiogroup"] label {
        flex: 1;
        min-width: 0;
        text-align: center;
        padding: 6px 5px;
        font-size: .78rem;
    }
    [data-testid="stMetric"] {
        padding: 7px 5px;
    }
    [data-testid="stMetricLabel"] {
        font-size: .67rem;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.05rem;
    }
    .stButton > button {
        min-height: 42px !important;
        height: auto !important;
        font-size: .90rem !important;
        padding: 4px 6px !important;
        line-height: 1.15 !important;
        white-space: normal !important;
    }

    /* Evita cualquier desbordamiento horizontal en teléfonos */
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > .main,
    [data-testid="stAppViewContainer"] .block-container {
        max-width: 100% !important;
        overflow-x: hidden !important;
    }

    /* Las columnas del ranking móvil deben poder encogerse */
    [data-testid="stHorizontalBlock"] {
        min-width: 0 !important;
        width: 100% !important;
    }
    [data-testid="column"] {
        min-width: 0 !important;
    }
}
</style>
""", unsafe_allow_html=True)
def supabase_get(tabla, parametros=None):
    key = st.secrets["SUPABASE_KEY"]
    url = f"{SUPABASE_URL}/{tabla}"
    if parametros:
        query = urllib.parse.urlencode(parametros)
        url += f"?{query}"
    request = urllib.request.Request(
        url,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(request) as response:
        contenido = response.read().decode("utf-8")
    return json.loads(contenido)
@st.cache_data(ttl=60)
def cargar_datos():
    jugadores = supabase_get("jugadores", {"select": "*"})
    partidas = supabase_get("partidas", {"select": "*"})
    resultados = supabase_get("resultados_partidas", {"select": "*"})
    return (
        pd.DataFrame(jugadores),
        pd.DataFrame(partidas),
        pd.DataFrame(resultados)
    )
try:
    df_jugadores, df_partidas, df_resultados = cargar_datos()
except Exception as e:
    st.error("No se han podido cargar los datos de Supabase.")
    st.exception(e)
    st.stop()
datos = df_resultados.copy()
if not df_partidas.empty:
    columnas_partidas = [
        c for c in [
            "id", "fecha", "tipo_juego", "temporada",
            "nombre", "nombre_partida"
        ] if c in df_partidas.columns
    ]
    if "id" in columnas_partidas:
        partidas_merge = df_partidas[columnas_partidas].copy()
        partidas_merge = partidas_merge.rename(columns={"id": "partida_id"})
        datos = datos.merge(partidas_merge, on="partida_id", how="left")
if not df_jugadores.empty:
    columnas_jugadores = [
        c for c in ["id", "nombre", "name"]
        if c in df_jugadores.columns
    ]
    if "id" in columnas_jugadores:
        jugadores_merge = df_jugadores[columnas_jugadores].copy()
        if "nombre" not in jugadores_merge.columns and "name" in jugadores_merge.columns:
            jugadores_merge["nombre"] = jugadores_merge["name"]
        if "nombre" in jugadores_merge.columns:
            jugadores_merge = jugadores_merge[["id", "nombre"]]
            jugadores_merge = jugadores_merge.rename(columns={
                "id": "jugador_id",
                "nombre": "nombre_jugador"
            })
            datos = datos.merge(jugadores_merge, on="jugador_id", how="left")
if "puntuacion" in datos.columns:
    datos["puntuacion"] = pd.to_numeric(
        datos["puntuacion"], errors="coerce"
    ).fillna(0)
else:
    datos["puntuacion"] = 0
if "posicion" in datos.columns:
    datos["posicion"] = pd.to_numeric(
        datos["posicion"], errors="coerce"
    )
else:
    datos["posicion"] = pd.NA
if "tipo_juego" not in datos.columns:
    datos["tipo_juego"] = ""
if "temporada" not in datos.columns:
    datos["temporada"] = ""
datos["tipo_juego"] = datos["tipo_juego"].fillna("").astype(str).str.strip().str.upper()
datos["temporada"] = datos["temporada"].fillna("").astype(str).str.strip()
if "nombre_jugador" not in datos.columns:
    datos["nombre_jugador"] = "Jugador"
else:
    datos["nombre_jugador"] = datos["nombre_jugador"].fillna("Jugador").astype(str)
if "jugador_id" not in datos.columns:
    datos["jugador_id"] = ""
if "jugador_seleccionado" not in st.session_state:
    st.session_state.jugador_seleccionado = None
def ordenar_temporada(valor):
    try:
        for parte in str(valor).split():
            if parte.isdigit():
                return int(parte)
        return 9999
    except Exception:
        return 9999
def obtener_temporadas():
    if "temporada" not in df_partidas.columns:
        return []
    temporadas = (
        df_partidas["temporada"]
        .dropna()
        .astype(str)
        .str.strip()
        .drop_duplicates()
        .tolist()
    )
    return sorted(temporadas, key=ordenar_temporada)
def crear_ranking(tipo_juego, temporada):
    df = datos.copy()
    df = df[
        (df["tipo_juego"] == tipo_juego) &
        (df["temporada"] == temporada)
    ].copy()
    if df.empty:
        return pd.DataFrame()
    df = df.drop_duplicates(subset=["partida_id", "jugador_id"]).copy()
    df["puntuacion"] = pd.to_numeric(
        df["puntuacion"], errors="coerce"
    ).fillna(0)
    df["posicion"] = pd.to_numeric(
        df["posicion"], errors="coerce"
    )
    ranking = (
        df.groupby(["jugador_id", "nombre_jugador"], as_index=False)
        .agg(
            Puntos=("puntuacion", "sum"),
            Partidas=("partida_id", "nunique"),
            Media=("puntuacion", "mean"),
            PuntuacionMaxima=("puntuacion", "max")
        )
    )
    ganadas = (
        df[df["posicion"] == 1]
        .groupby("jugador_id")["partida_id"]
        .nunique()
        .reset_index(name="Ganadas")
    )
    ranking = ranking.merge(ganadas, on="jugador_id", how="left")
    ranking["Ganadas"] = ranking["Ganadas"].fillna(0).astype(int)
    ranking["Winrate"] = (
        ranking["Ganadas"] / ranking["Partidas"] * 100
    ).fillna(0).round(1)
    posiciones = (
        df.groupby("jugador_id")
        .agg(SumaPosiciones=("posicion", "sum"))
        .reset_index()
    )
    ranking = ranking.merge(posiciones, on="jugador_id", how="left")
    ranking["MediaPosicion"] = (
        ranking["SumaPosiciones"] / ranking["Partidas"]
    ).round(2)
    ranking["Puntos"] = ranking["Puntos"].round().astype(int)
    ranking["Media"] = ranking["Media"].round(1)
    ranking["PuntuacionMaxima"] = ranking["PuntuacionMaxima"].round().astype(int)
    ranking["MediaPosicion"] = ranking["MediaPosicion"].fillna(0).round(2)
    ranking = ranking.sort_values(
        "Puntos", ascending=False, kind="mergesort"
    ).reset_index(drop=True)
    ranking["Posición"] = ranking.index + 1
    return ranking[[
        "Posición", "jugador_id", "nombre_jugador", "Puntos",
        "Partidas", "Ganadas", "Winrate", "Media",
        "PuntuacionMaxima", "MediaPosicion"
    ]]
def es_dispositivo_movil():
    try:
        user_agent = st.context.headers.get("User-Agent", "").lower()
    except Exception:
        user_agent = ""
    return any(x in user_agent for x in [
        "android", "iphone", "ipad", "ipod", "mobile"
    ])
def mostrar_indicadores(jugador_id, tipo_juego, temporada):
    ranking = crear_ranking(tipo_juego, temporada)
    if ranking.empty:
        st.info("No hay datos para esta temporada.")
        return
    fila_jugador = ranking[
        ranking["jugador_id"].astype(str) == str(jugador_id)
    ]
    if fila_jugador.empty:
        st.info(f"Este jugador no tiene partidas de {tipo_juego} en esta temporada.")
        return
    fila = fila_jugador.iloc[0]
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Puntos", int(fila["Puntos"]))
    with c2:
        st.metric("Partidas", int(fila["Partidas"]))
    with c3:
        st.metric("Posición", int(fila["Posición"]))
    c4, c5, c6 = st.columns(3)
    with c4:
        st.metric("WINRATE", f"{float(fila['Winrate']):.1f}%")
    with c5:
        st.metric("Ganadas", int(fila["Ganadas"]))
    with c6:
        st.metric("Media posición", f"{float(fila['MediaPosicion']):.2f}")
    c7, c8 = st.columns(2)
    with c7:
        st.metric("Puntuación media", f"{float(fila['Media']):.1f}")
    with c8:
        st.metric("Puntuación máxima", int(fila["PuntuacionMaxima"]))
def mostrar_distribucion_posiciones(jugador_id, tipo_juego, temporada):
    df = datos[
        (datos["jugador_id"].astype(str) == str(jugador_id)) &
        (datos["tipo_juego"] == tipo_juego) &
        (datos["temporada"] == temporada)
    ].copy()
    if df.empty:
        return
    df = df.drop_duplicates(subset=["partida_id", "jugador_id"])
    df["posicion"] = pd.to_numeric(df["posicion"], errors="coerce")
    valores = [int((df["posicion"] == i).sum()) for i in range(1, 6)]
    st.subheader("📊 Posiciones")
    tabla = pd.DataFrame({
        "🥇 1ª": [valores[0]],
        "🥈 2ª": [valores[1]],
        "🥉 3ª": [valores[2]],
        "4ª": [valores[3]],
        "5ª": [valores[4]]
    })
    st.table(tabla)
def mostrar_historial(jugador_id, tipo_juego, temporada):
    jugador_id_texto = str(jugador_id)
    datos_jugador = datos[
        (datos["jugador_id"].astype(str) == jugador_id_texto) &
        (datos["tipo_juego"] == tipo_juego) &
        (datos["temporada"] == temporada)
    ].copy()
    if datos_jugador.empty:
        st.info(f"Este jugador no tiene partidas de {tipo_juego} en esta temporada.")
        return
    ids_partidas = datos_jugador["partida_id"].dropna().unique()
    partidas_jugador = datos[
        datos["partida_id"].isin(ids_partidas)
    ].copy()
    partidas_jugador = partidas_jugador[
        (partidas_jugador["tipo_juego"] == tipo_juego) &
        (partidas_jugador["temporada"] == temporada)
    ].copy()
    if partidas_jugador.empty:
        st.info("No hay historial.")
        return
    partidas_info = (
        partidas_jugador[["partida_id", "fecha"]]
        .drop_duplicates()
        .copy()
    )
    partidas_info["fecha_orden"] = pd.to_datetime(
        partidas_info["fecha"], errors="coerce"
    )
    partidas_info = partidas_info.sort_values(
        "fecha_orden", ascending=False
    )
    for _, partida in partidas_info.iterrows():
        partida_id = partida["partida_id"]
        datos_partida = partidas_jugador[
            partidas_jugador["partida_id"] == partida_id
        ].copy()
        if datos_partida.empty:
            continue
        datos_partida = datos_partida.sort_values(
            "posicion", ascending=True, na_position="last"
        )
        try:
            fecha_formateada = pd.to_datetime(partida["fecha"]).strftime("%d/%m/%Y")
        except Exception:
            fecha_formateada = str(partida["fecha"])
        nombre_partida = ""
        if "nombre_partida" in datos_partida.columns:
            valores = datos_partida["nombre_partida"].dropna()
            if not valores.empty:
                nombre_partida = str(valores.iloc[0]).strip()
        if not nombre_partida and "nombre" in datos_partida.columns:
            valores = datos_partida["nombre"].dropna()
            if not valores.empty:
                nombre_partida = str(valores.iloc[0]).strip()
        titulo = (
            f"{fecha_formateada} · {nombre_partida}"
            if nombre_partida else fecha_formateada
        )
        st.markdown(
            f'<div class="match-header">{titulo}</div>',
            unsafe_allow_html=True
        )
        h1, h2, h3 = st.columns([3, 1, 1])
        with h1:
            st.markdown('<div class="match-col-header">JUGADOR</div>', unsafe_allow_html=True)
        with h2:
            st.markdown('<div class="match-col-header">PUNTOS</div>', unsafe_allow_html=True)
        with h3:
            st.markdown('<div class="match-col-header">POS.</div>', unsafe_allow_html=True)
        for _, fila in datos_partida.iterrows():
            nombre = str(fila.get("nombre_jugador", "Jugador"))
            try:
                puntuacion = int(round(float(fila.get("puntuacion", 0))))
            except Exception:
                puntuacion = 0
            try:
                posicion = int(float(fila.get("posicion", "")))
            except Exception:
                posicion = ""
            seleccionado = str(fila["jugador_id"]) == jugador_id_texto
            clase = "match-cell-selected" if seleccionado else "match-cell"
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown(f'<div class="{clase}">{nombre}</div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="{clase}" style="text-align:center">{puntuacion}</div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="{clase}" style="text-align:center">{posicion}</div>', unsafe_allow_html=True)
def mostrar_ficha(jugador_id):
    cab1, cab2 = st.columns([3, 1])
    with cab1:
        st.title("🀄 Ficha del jugador")
    with cab2:
        if st.button("← Volver", key="volver_arriba", use_container_width=True):
            st.session_state.jugador_seleccionado = None
            st.rerun()
    jugador_id_texto = str(jugador_id)
    nombre_jugador = "Jugador"
    if not df_jugadores.empty and "id" in df_jugadores.columns:
        encontrados = df_jugadores[
            df_jugadores["id"].astype(str) == jugador_id_texto
        ]
        if not encontrados.empty:
            if "nombre" in encontrados.columns:
                nombre_jugador = str(encontrados.iloc[0]["nombre"])
            elif "name" in encontrados.columns:
                nombre_jugador = str(encontrados.iloc[0]["name"])
    if nombre_jugador == "Jugador":
        encontrados = datos[
            datos["jugador_id"].astype(str) == jugador_id_texto
        ]
        if encontrados.empty:
            st.error("No se ha encontrado el jugador.")
            return
        nombre_jugador = str(encontrados.iloc[0]["nombre_jugador"])
    st.markdown(
        f'<div class="player-title">{nombre_jugador}</div>',
        unsafe_allow_html=True
    )
    temporadas_ficha = obtener_temporadas()
    if not temporadas_ficha:
        st.warning("No se han encontrado temporadas en la tabla de partidas.")
        return
    tab_mcr, tab_riichi = st.tabs(["🀄 MCR", "🀄 RIICHI"])
    with tab_mcr:
        tabs = st.tabs(temporadas_ficha)
        for temporada, tab in zip(temporadas_ficha, tabs):
            with tab:
                st.subheader(temporada)
                mostrar_indicadores(jugador_id, "MCR", temporada)
                st.divider()
                mostrar_distribucion_posiciones(jugador_id, "MCR", temporada)
                st.divider()
                st.subheader("📋 Historial")
                mostrar_historial(jugador_id, "MCR", temporada)
    with tab_riichi:
        tabs = st.tabs(temporadas_ficha)
        for temporada, tab in zip(temporadas_ficha, tabs):
            with tab:
                st.subheader(temporada)
                mostrar_indicadores(jugador_id, "RIICHI", temporada)
                st.divider()
                mostrar_distribucion_posiciones(jugador_id, "RIICHI", temporada)
                st.divider()
                st.subheader("📋 Historial")
                mostrar_historial(jugador_id, "RIICHI", temporada)
    st.divider()
    if st.button("← Volver al ranking", key="volver_abajo", use_container_width=True):
        st.session_state.jugador_seleccionado = None
        st.rerun()
def limpiar_criterio(criterio):
    return (
        criterio.replace("📈 ", "")
        .replace("🏆 ", "")
        .replace("🎯 ", "")
    )
def mostrar_ranking(tipo_juego, temporada):
    ranking = crear_ranking(tipo_juego, temporada)
    if ranking.empty:
        st.info(f"No hay datos de {tipo_juego} para {temporada}.")
        return
    criterio = st.radio(
        "Ordenar ranking por:",
        ["📈 Winrate", "🏆 Puntos", "🎯 Media posición"],
        index=0,
        horizontal=True,
        key=f"criterio_{tipo_juego}_{temporada}"
    )
    if criterio == "📈 Winrate":
        columna_orden = "Winrate"
        ascendente = False
    elif criterio == "🏆 Puntos":
        columna_orden = "Puntos"
        ascendente = False
    else:
        columna_orden = "MediaPosicion"
        ascendente = True
    ranking = ranking.sort_values(
        columna_orden,
        ascending=ascendente,
        kind="mergesort"
    ).reset_index(drop=True)
    ranking["Posición"] = ranking.index + 1
    if es_dispositivo_movil():
        nombre_valor = limpiar_criterio(criterio)

        st.markdown(
            f'<div style="font-size:.98rem;font-weight:800;margin:7px 0 7px 2px;">Ranking por {nombre_valor}</div>',
            unsafe_allow_html=True
        )

        # Cabecera compacta, similar al formato móvil de FEMJ.
        st.markdown(
            f"""<div class="mobile-ranking-header">
                <div>POS.</div>
                <div>JUGADOR</div>
                <div style="text-align:right">{nombre_valor.upper()}</div>
            </div>""",
            unsafe_allow_html=True
        )

        for _, fila in ranking.iterrows():
            posicion = int(fila["Posición"])
            jugador_id = fila["jugador_id"]
            nombre = str(fila["nombre_jugador"]).strip()

            if columna_orden == "Winrate":
                valor = f"{float(fila['Winrate']):.1f}%"
            elif columna_orden == "Puntos":
                valor = f"{int(fila['Puntos'])}"
            else:
                valor = f"{float(fila['MediaPosicion']):.2f}"

            if posicion == 1:
                simbolo = "🥇"
            elif posicion == 2:
                simbolo = "🥈"
            elif posicion == 3:
                simbolo = "🥉"
            else:
                simbolo = str(posicion)

            # Una fila compacta: posición | nombre | valor.
            # Las columnas usan proporciones para que el nombre tenga
            # siempre todo el espacio restante y pueda ocupar 2 líneas.
            fondo_fila = "#fff9df" if posicion % 2 == 0 else "#ffffff"
            c1, c2, c3 = st.columns([0.58, 3.55, 1.02], gap="small")

            with c1:
                st.markdown(
                    f"""<div style="
                        background:{fondo_fila};
                        min-height:50px;
                        height:100%;
                        box-sizing:border-box;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        border-bottom:1px solid #e3e3e3;
                        font-size:1.02rem;
                        line-height:1;
                        font-weight:800;
                    ">{simbolo}</div>""",
                    unsafe_allow_html=True
                )

            with c2:
                # El botón conserva la navegación a la ficha del jugador.
                if st.button(
                    nombre,
                    key=f"mobile_{tipo_juego}_{temporada}_{jugador_id}",
                    use_container_width=True
                ):
                    st.session_state.jugador_seleccionado = str(jugador_id)
                    st.rerun()

            with c3:
                st.markdown(
                    f"""<div style="
                        background:{fondo_fila};
                        min-height:50px;
                        height:100%;
                        box-sizing:border-box;
                        display:flex;
                        align-items:center;
                        justify-content:flex-end;
                        padding:0 5px 0 1px;
                        border-bottom:1px solid #e3e3e3;
                        font-size:.88rem;
                        line-height:1;
                        font-weight:800;
                        white-space:nowrap;
                    ">{valor}</div>""",
                    unsafe_allow_html=True
                )

        return
    st.markdown(
        f'<div style="font-weight:800;margin:8px 0;">Ranking por {limpiar_criterio(criterio)}</div>',
        unsafe_allow_html=True
    )
    st.markdown('''
    <div class="ranking-header">
        <div>Pos.</div>
        <div>Jugador</div>
        <div>Puntos</div>
        <div>Part.</div>
        <div>Gan.</div>
        <div>Winrate</div>
        <div>Media</div>
        <div>Máx.</div>
        <div>Media pos.</div>
    </div>
    ''', unsafe_allow_html=True)
    for _, fila in ranking.iterrows():
        posicion = int(fila["Posición"])
        jugador_id = fila["jugador_id"]
        nombre = str(fila["nombre_jugador"])
        puntos = int(fila["Puntos"])
        partidas = int(fila["Partidas"])
        ganadas = int(fila["Ganadas"])
        winrate = float(fila["Winrate"])
        media = float(fila["Media"])
        maxima = int(fila["PuntuacionMaxima"])
        media_pos = float(fila["MediaPosicion"])
        c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(
            [55, 2.3, .95, .75, .75, 1, .8, .8, 1]
        )
        with c1:
            st.markdown(
                f'<div class="ranking-position">{posicion}</div>',
                unsafe_allow_html=True
            )
        with c2:
            if st.button(
                nombre,
                key=f"pc_{tipo_juego}_{temporada}_{jugador_id}",
                use_container_width=True
            ):
                st.session_state.jugador_seleccionado = str(jugador_id)
                st.rerun()
        with c3:
            st.markdown(f'<div class="ranking-value">{puntos}</div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="ranking-value">{partidas}</div>', unsafe_allow_html=True)
        with c5:
            st.markdown(f'<div class="ranking-value">{ganadas}</div>', unsafe_allow_html=True)
        with c6:
            st.markdown(f'<div class="ranking-value">{winrate:.1f}%</div>', unsafe_allow_html=True)
        with c7:
            st.markdown(f'<div class="ranking-value">{media:.1f}</div>', unsafe_allow_html=True)
        with c8:
            st.markdown(f'<div class="ranking-value">{maxima}</div>', unsafe_allow_html=True)
        with c9:
            st.markdown(f'<div class="ranking-value">{media_pos:.2f}</div>', unsafe_allow_html=True)
if st.session_state.jugador_seleccionado is not None:
    mostrar_ficha(st.session_state.jugador_seleccionado)
    st.stop()
cab_logo, cab_titulo = st.columns([1, 4])
with cab_logo:
    if os.path.exists(RUTA_LOGO):
        st.image(RUTA_LOGO, width=78)
    else:
        st.markdown("🀄")
with cab_titulo:
    st.title("Liga Mahjong Madrid")
st.markdown(
    '<div style="color:#777;font-size:.9rem;margin-top:-8px;margin-bottom:8px;">Ranking de jugadores · MCR y RIICHI</div>',
    unsafe_allow_html=True
)
temporadas = obtener_temporadas()
if not temporadas:
    st.warning("No se han encontrado temporadas en la tabla de partidas.")
    st.stop()
tab_mcr, tab_riichi = st.tabs(["🀄 MCR", "🀄 RIICHI"])
with tab_mcr:
    tabs_mcr = st.tabs(temporadas)
    for temporada, tab_temporada in zip(temporadas, tabs_mcr):
        with tab_temporada:
            st.subheader(temporada)
            mostrar_ranking("MCR", temporada)
with tab_riichi:
    tabs_riichi = st.tabs(temporadas)
    for temporada, tab_temporada in zip(temporadas, tabs_riichi):
        with tab_temporada:
            st.subheader(temporada)
            mostrar_ranking("RIICHI", temporada)
