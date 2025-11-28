import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Market Breadth B3",
    layout="wide",
    page_icon="📈"
)

# --- ESTILOS CSS PERSONALIZADOS (OPCIONAL) ---
st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LISTA DE ATIVOS ---
lista_parte_1 = "ORVR3, CBAV3, VVEO3, ONCO3, RCSL4, RCSL3, ENEV3, JALL3, CASH3, EVEN3, AGRO3, AZZA3, VAMO3, BPAN4, LJQQ3, JSLG3, SOJA3, TUPY3, PGMN3, IRBR3, PLPL3, TTEN3, ALPA4, MYPK3, HBSA3, ISAE4, VLID3, DXCO3, CVCB3, BLAU3, BRKM5, GGPS3, VBBR3, CURY3, IGTI11, VIVA3, CPLE3, ANIM3, AURE3, SBFG3, BRAP4, ASAI3, CYRE3, SEER3, YDUQ3, SBSP3, CPFE3, SYNE3, LEVE3, EQTL3, MOVI3, CEAB3, POSI3, SLCE3, SIMH3, CMIN3, RECV3, MDNE3, AMOB3, USIM5, CSNA3, GFSA3, RDOR3, RAIL3, NEOE3, TOTS3, CSMG3, CMIG4, TFCO4, GMAT3, HYPE3, PSSA3, QUAL3, MULT3, SAPR11, ABCB4, PCAR3, NATU3, LREN3, RADL3, PNVL3, FRAS3, PETZ3, SUZB3, SANB11, RAPT4, GUAR3, HAPV3, WEGE3, TIMS3, SMTO3, INTB3, CXSE3, ECOR3, MOTV3, TGMA3"
lista_parte_2 = "TEND3, ABEV3, BPAC11, ODPV3, RANI3, KLBN11, PRIO3, LOGG3, DIRR3, MGLU3, GGBR4, KEPL3, GOAU4, BBAS3, VALE3, FLRY3, UNIP6, ENGI11, BRBI11, EZTC3, ALUP11, LAVV3, BBSE3, TAEE11, MILS3, LWSA3, ARML3, BMOB3, PETR3, GRND3, PETR4, UGPA3, ALOS3, MDIA3, EGIE3, BEEF3, RAIZ4, MRVE3, VIVT3, POMO4, ITSA4, ITUB3, JHSF3, ITUB4, BBDC3, BBDC4, FESA4, CAML3, BHIA3, CSAN3, RENT3, B3SA3, VULC3, BRSR6, BRAV3, SMFT3, COGN3, MBRF3, EMBJ3, CPLE5, AXIA6, AXIA3, BMEB4, VTRU3, ROMI3, DEXP3, HBRE3, REAG3, BRSR3, BRKM3, MEAL3, ALPA3, DOTZ3, TRAD3, DEXP4, GOAU3, GOAU3, CLSC4, PTBL3, TECN3, ETER3, AERI3, AERI3, SHOW3, HBOR3, PDTC3, WIZC3, RNEW3, MATD3, WDCN3, CCTY3, PFRM3, AALR3, ALPK3, BMEB3, MLAS3, ADMF3, DESK3, OFSA3, OFSA3, RDNI3, EUCA4, RVEE3, VITT3, ALLD3, ALLD3, POMO3, SCAR3, WEST3, TASA3, BRAP3, TPIS3, FHER3, LPSB3, MTRE3, LAND3, RNEW4, RNEW4, ISAE3, LOGN3, RAPT3, CSED3, BRST3, AMAR3, USIM3, VSTE3, MELK3, CEDO4, CEDO4, GGBR3, UCAS3, ITSA3, TASA4, LUPA3, FIQE3, FIQE3, BMGB4, OPCT3, ENJU3, DASA3, SEQL3, SEQL3, TRIS3, CMIG3, TCSA3, PINE3, ESPA3, ESPA3, EUCA3, PINE4, TOKY3, AVLL3, CSUD3, NGRD3, NGRD3, DMVF3"
lista_bruta = lista_parte_1 + ", " + lista_parte_2

# Processa lista
tickers_br = list(set([ticker.strip() + ".SA" for ticker in lista_bruta.split(',') if ticker.strip()]))
tickers_br.sort() # Ordenar alfabeticamente para melhor visualização

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.header("Configurações")
dias_visualizacao = st.sidebar.slider("Período de Análise (Dias)", min_value=30, max_value=1825, value=365, step=30)
mostrar_grid = st.sidebar.checkbox("Mostrar Grid nos Gráficos", value=True)

st.sidebar.markdown("---")
st.sidebar.header("Ativos Monitorados")
with st.sidebar.expander("Ver lista de ações"):
    st.write(f"Total: {len(tickers_br)}")
    st.write(", ".join([t.replace('.SA', '') for t in tickers_br]))

st.title("📊 Análise Market Breadth B3")
st.markdown(f"**Total de ativos monitorados:** {len(tickers_br)} ações da B3.")

# --- FUNÇÃO DE DADOS COM CACHE ---
@st.cache_data(ttl=3600)  # Cache de 1 hora
def carregar_dados(lista_tickers, dias_retro):
    # AJUSTE DATA: Somamos 1 dia para o yf incluir o dia atual (end é exclusivo)
    data_fim = datetime.now() + timedelta(days=1)
    
    # Baixamos um buffer extra (365 dias) para calcular as médias móveis corretamente
    data_inicio = datetime.now() - timedelta(days=dias_retro + 365) 
    
    try:
        with st.spinner('Baixando dados do Yahoo Finance... isso pode levar alguns segundos.'):
            dados_brutos = yf.download(lista_tickers, start=data_inicio, end=data_fim, auto_adjust=False, progress=False)
            ibov_bruto = yf.download("^BVSP", start=data_inicio, end=data_fim, auto_adjust=False, progress=False)
        
        if dados_brutos.empty:
            return None, None

        # Tratamento para diferentes versões do yfinance
        if 'Adj Close' in dados_brutos:
            dados = dados_brutos['Adj Close']
        elif 'Close' in dados_brutos:
            dados = dados_brutos['Close']
        else:
            return None, None
            
        if 'Adj Close' in ibov_bruto:
            ibov = ibov_bruto['Adj Close']
        elif 'Close' in ibov_bruto:
            ibov = ibov_bruto['Close']
        else:
            ibov = ibov_bruto.iloc[:, 0]

        dados = dados.dropna(axis=1, how='all')
        return dados, ibov

    except Exception as e:
        st.error(f"Erro ao baixar dados: {e}")
        return None, None

# --- PROCESSAMENTO ---
dados, ibov = carregar_dados(tickers_br, dias_visualizacao)

if dados is not None and ibov is not None:
    # Cálculo dos indicadores
    medias_moveis = [5, 10, 20, 50, 200]
    resultados = pd.DataFrame(index=dados.index)

    for mm in medias_moveis:
        df_mm = dados.rolling(window=mm).mean()
        total_validos = df_mm.count(axis=1)
        acima_da_media = dados > df_mm
        qtd_acima = acima_da_media.sum(axis=1)
        
        # Evita divisão por zero
        resultados[f'MM{mm}_Pct'] = (qtd_acima / total_validos) * 100

    # Limpeza e corte para o período selecionado
    resultados = resultados.dropna()
    resultados_limpos = resultados.tail(dias_visualizacao)
    ibov_limpo = ibov.reindex(resultados_limpos.index)

    # --- DASHBOARD DE MÉTRICAS ---
    st.subheader("Situação Atual do Mercado")
    cols = st.columns(5)
    
    mapa_cores = {5: '#1f77b4', 10: '#00bfa5', 20: '#2ca02c', 50: '#ff7f0e', 200: '#000000'}
    
    for i, mm in enumerate(medias_moveis):
        valor_atual = resultados_limpos[f'MM{mm}_Pct'].iloc[-1]
        if len(resultados_limpos) > 1:
            valor_anterior = resultados_limpos[f'MM{mm}_Pct'].iloc[-2]
            delta = valor_atual - valor_anterior
        else:
            delta = 0
        
        cols[i].metric(
            label=f"> MM{mm}",
            value=f"{valor_atual:.1f}%",
            delta=f"{delta:.1f} p.p."
        )

    st.markdown("---")

    # --- GRÁFICOS ---
    
    # Função auxiliar de plotagem
    def criar_grafico(mms_para_plotar, titulo_grafico):
        # Altura reduzida para (12, 3.5) para caber mais gráficos na tela
        fig, ax1 = plt.subplots(figsize=(12, 3.5)) 
        
        # Plot das Porcentagens
        for mm in mms_para_plotar:
            coluna = f'MM{mm}_Pct'
            cor = mapa_cores.get(mm, 'blue')
            ax1.plot(resultados_limpos.index, resultados_limpos[coluna], 
                     color=cor, label=f'> MM{mm} (%)', linewidth=2)
            
            # Área sombreada suave
            ax1.fill_between(resultados_limpos.index, resultados_limpos[coluna], alpha=0.1, color=cor)
            
            # Anotação do último valor
            ultimo_valor = resultados_limpos[coluna].iloc[-1]
            ultima_data = resultados_limpos.index[-1]
            ax1.annotate(f"{ultimo_valor:.1f}%", xy=(ultima_data, ultimo_valor), 
                         xytext=(5, 0), textcoords='offset points', 
                         color=cor, fontweight='bold', fontsize=9)

        ax1.set_ylabel('% de Ações acima da Média')
        ax1.set_ylim(0, 100)
        ax1.axhline(y=50, color='gray', linestyle='--', linewidth=1, alpha=0.5)
        
        if mostrar_grid:
            ax1.grid(True, linestyle=':', alpha=0.6)

        # Plot do IBOV (Eixo secundário) - ESTILO ATUALIZADO
        ax2 = ax1.twinx()
        ax2.plot(ibov_limpo.index, ibov_limpo, 
                 color='#444444', alpha=0.8, linewidth=1.5, linestyle='-', label='IBOV')
        ax2.set_ylabel('Pontos IBOV', color='#444444')
        ax2.grid(False) # Desliga grid do eixo secundário

        # Legendas combinadas
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True)
        
        plt.title(titulo_grafico)
        plt.tight_layout()
        return fig

    # Abas para organização
    tab1, tab2, tab3 = st.tabs(["Curto Prazo (5/10)", "Médio Prazo (20)", "Longo Prazo (50/200)"])

    with tab1:
        st.write("Visão de curtíssimo prazo. Indica sobrecompra/sobrevenda rápida.")
        # Gráficos Separados
        st.pyplot(criar_grafico([5], "Ações acima da Média Móvel de 5 dias"))
        st.pyplot(criar_grafico([10], "Ações acima da Média Móvel de 10 dias"))

    with tab2:
        st.write("Visão tática. Acompanha a tendência mensal.")
        st.pyplot(criar_grafico([20], "Ações acima da Média Móvel de 20 dias"))

    with tab3:
        st.write("Visão estrutural. Define a saúde da tendência primária.")
        # Gráficos Separados
        st.pyplot(criar_grafico([50], "Ações acima da Média Móvel de 50 dias"))
        st.pyplot(criar_grafico([200], "Ações acima da Média Móvel de 200 dias"))

else:
    st.warning("Não foi possível carregar os dados. Tente recarregar a página.")