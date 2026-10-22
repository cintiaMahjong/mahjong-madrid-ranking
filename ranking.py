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
 
            # El ID se codifica para que cualquier UUID/valor especial sea seguro en la URL. 
            jugador_url = urllib.parse.quote(jugador_id, safe="") 
 
            filas_html.append( 
                f'''<a class="mobile-ranking-row" href="?jugador_id={jugador_url}"> 
                        <div class="mobile-pos">{simbolo}</div> 
                        <div class="mobile-name">{nombre}</div> 
                        <div class="mobile-value">{valor}</div> 
                    </a>''' 
            ) 
 
        st.markdown( 
            '<div class="mobile-ranking">' + ''.join(filas_html) + '</div>', 
            unsafe_allow_html=True 
        ) 
        if not segundo_ranking:
            st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)
            mostrar_ranking(tipo_juego, temporada, segundo_ranking=True)
        return 
 
    # ===================================================== 
    # ESCRITORIO: TABLA COMPLETA 
    # ===================================================== 
    filas_html = [ 
        '''<div class="ranking-header"> 
            <div style="text-align:center;">Pos.</div> 
            <div>Jugador</div> 
            <div style="text-align:center;">Puntos</div> 
            <div style="text-align:center;">Part.</div> 
            <div style="text-align:center;">Gan.</div> 
            <div style="text-align:center;">Winrate</div> 
            <div style="text-align:center;">Media</div> 
            <div style="text-align:center;">Máx.</div> 
            <div style="text-align:center;">Media pos.</div> 
        </div>''' 
    ] 
 
    for _, fila in ranking.iterrows(): 
        posicion = int(fila["Posición"]) 
        jugador_id = str(fila["jugador_id"]) 
        nombre = html.escape(str(fila["nombre_jugador"]).strip()) 
        puntos = int(fila["Puntos"]) 
        partidas = int(fila["Partidas"]) 
        ganadas = int(fila["Ganadas"]) 
        winrate = float(fila["Winrate"]) 
        media = float(fila["Media"]) 
        maxima = int(fila["PuntuacionMaxima"]) 
        media_pos = float(fila["MediaPosicion"]) 
        jugador_url = urllib.parse.quote(jugador_id, safe="") 
 
        filas_html.append( 
            f'''<div class="ranking-row"> 
                <div class="ranking-cell ranking-position">{posicion}</div> 
                <div class="ranking-cell"> 
                    <a class="ranking-player-link" href="?jugador_id={jugador_url}">{nombre}</a> 
                </div> 
                <div class="ranking-cell ranking-value">{puntos}</div> 
                <div class="ranking-cell ranking-value">{partidas}</div> 
                <div class="ranking-cell ranking-value">{ganadas}</div> 
                <div class="ranking-cell ranking-value">{winrate:.1f}%</div> 
                <div class="ranking-cell ranking-value">{media:.1f}</div> 
                <div class="ranking-cell ranking-value">{maxima}</div> 
                <div class="ranking-cell ranking-value">{media_pos:.2f}</div> 
            </div>''' 
        ) 
 
    st.markdown( 
        '<div class="ranking-box">' + ''.join(filas_html) + '</div>', 
        unsafe_allow_html=True 
    ) 

    if not segundo_ranking:
        st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)
        mostrar_ranking(tipo_juego, temporada, segundo_ranking=True)
 
if st.session_state.jugador_seleccionado is not None: 
    mostrar_ficha(st.session_state.jugador_seleccionado) 
    st.stop() 
if os.path.exists(RUTA_LOGO): 
    import base64 
    with open(RUTA_LOGO, "rb") as archivo_logo: 
        logo_base64 = base64.b64encode(archivo_logo.read()).decode() 
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" style="width:100%;height:auto;display:block;">' 
else: 
    logo_html = '<div style="font-size:2.2rem;text-align:center;">🀄</div>' 
 
st.markdown( 
    f'''<div class="main-header"> 
        <div class="main-header-logo">{logo_html}</div> 
        <div class="main-header-title"> 
            <div style="font-size:2rem;line-height:1.08;font-weight:800;color:#151515;">Liga Mahjong Madrid</div> 
            <div class="main-header-subtitle">Ranking de jugadores · MCR y RIICHI</div> 
        </div> 
    </div>''', 
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
