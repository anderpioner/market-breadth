import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import traceback

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Market Breadth B3",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Market Breadth B3: Indicador de Amplitude")
st.markdown("""
Esta ferramenta analisa **quantas ações da B3 estão negociando acima de suas médias móveis** de 5, 10, 20, 50 e 200 dias.
Isso ajuda a identificar a força real da tendência do mercado, além do que o IBOVESPA mostra.
""")

# --- SIDEBAR (CONTROLES) ---
st.sidebar.header("Configurações")

# Input de dias para visualização
dias_visualizacao = st.sidebar.slider(
    "Período do Gráfico (dias)", 
    min_value=30, 
    max_value=500, 
    value=100,
    step=10
)

# Lista de Tickers (Fixa no código, mas exibida aqui)
lista_parte_1 = "ORVR3, CBAV3, VVEO3, ONCO3, RCSL4, RCSL3, ENEV3, JALL3, CASH3, EVEN3, AGRO3, AZZA3, VAMO3, BPAN4, LJQQ3, JSLG3, SOJA3, TUPY3, PGMN3, IRBR3, PLPL3, TTEN3, ALPA4, MYPK3, HBSA3, ISAE4, VLID3, DXCO3, CVCB3, BLAU3, BRKM5, GGPS3, VBBR3, CURY3, IGTI11, VIVA3, CPLE3, ANIM3, AURE3, SBFG3, BRAP4, ASAI3, CYRE3, SEER3, YDUQ3, SBSP3, CPFE3, SYNE3, LEVE3, EQTL3, MOVI3, CEAB3, POSI3, SLCE3, SIMH3, CMIN3, RECV3, MDNE3, AMOB3, USIM5, CSNA3, GFSA3, RDOR3, RAIL3, NEOE3, TOTS3, CSMG3, CMIG4, TFCO4, GMAT3, HYPE3, PSSA3, QUAL3, MULT3, SAPR11, ABCB4, PCAR3, NATU3, LREN3, RADL3, PNVL3, FRAS3, PETZ3, SUZB3, SANB11, RAPT4, GUAR3, HAPV3, WEGE3, TIMS3, SMTO3, INTB3, CXSE3, ECOR3, MOTV3, TGMA3"
lista_parte_2 = "TEND3, ABEV3, BPAC11, ODPV3, RANI3, KLBN11, PRIO3, LOGG3, DIRR3, MGLU3, GGBR4, KEPL3, GOAU4, BBAS3, VALE3, FLRY3, UNIP6, ENGI11, BRBI11, EZTC3, ALUP11, LAVV3, BBSE3, TAEE11, MILS3, LWSA3, ARML3, BMOB3, PETR3, GRND3, PETR4, UGPA3, ALOS3, MDIA3, EGIE3, BEEF3, RAIZ4, MRVE3, VIVT3, POMO4, ITSA4, ITUB3, JHSF3, ITUB4, BBDC3, BBDC4, FESA4, CAML3, BHIA3, CSAN3, RENT3, B3SA3, VULC3, BRSR6, BRAV3, SMFT3, COGN3, MBRF3, EMBJ3, CPLE5, AXIA6, AXIA3, BMEB4, VTRU3, ROMI3, DEXP3, HBRE3, REAG3, BRSR3, BRKM3, MEAL3, ALPA3, DOTZ3, TRAD3, DEXP4, GOAU3, GOAU3, CLSC4, PTBL3, TECN3, ETER3, AERI3, AERI3, SHOW3, HBOR3, PDTC3, WIZC3, RNEW3, MATD3, WDCN3, CCTY3, PFRM3, AALR3, ALPK3, BMEB3, MLAS3, ADMF3, DESK3, OFSA3, OFSA3, RDNI3, EUCA4, RVEE3, VITT3, ALLD3, ALLD3, POMO3, SCAR3, WEST3, TASA3, BRAP3, TPIS3, FHER3, LPSB3, MTRE3, LAND3, RNEW4, RNEW4, ISAE3, LOGN3, RAPT3, CSED3, BRST3, AMAR3, USIM3, VSTE3, MELK3, CEDO4, CEDO4, GGBR3, UCAS3, ITSA3, TASA4, LUPA3, FIQE3, FIQE3, BMGB4, OPCT3, ENJU3, DASA3, SEQL3, SEQL3, TRIS3, CMIG3, TCSA3, PINE3, ESPA3, ESPA3, EUCA3, PINE4, TOKY3, AVLL3, CSUD3, NGRD3, NGRD3, DMVF3"
lista_bruta = lista_parte_1 + ", " + lista_parte_2

# Processa lista
tickers_br = list(set([ticker.strip() + ".SA" for ticker in lista_bruta.split(',') if ticker.strip()]))

with st.sidebar.expander(f"Ver lista de ativos ({len(tickers_br)})"):
    st.text(", ".join(tickers_br))

# Botão de atualizar
if st.sidebar.button("🔄 Atualizar Dados"):
    st.cache_data.clear()

# --- FUNÇÃO DE CARREGAMENTO DE DADOS (COM CACHE) ---
@st.cache_data(ttl=3600) # Cache dura 1 hora
def carregar_dados(lista_tickers, dias_retro):
    # Define datas
    data_fim = datetime.now()
    # Buffer de 300 dias para garantir o cálculo da MM200
    data_inicio = data_fim - timedelta(days=dias_retro + 365) 
    
    status_msg = st.empty()
    status_msg.info("⏳ Baixando dados do Yahoo Finance... (Isso pode levar alguns segundos na primeira execução)")
    
    try:
        # 1. Baixa Ações
        dados_brutos = yf.download(lista_tickers, start=data_inicio, end=data_fim, auto_adjust=False, progress=False)
        # 2. Baixa IBOV
        ibov_bruto = yf.download("^BVSP", start=data_inicio, end=data_fim, auto_adjust=False, progress=False)
        
        if dados_brutos.empty:
            status_msg.error("Erro: Tabela de ações vazia.")
            return None, None

        # Tratamento Colunas Ações
        if 'Adj Close' in dados_brutos:
            dados = dados_brutos['Adj Close']
        elif 'Close' in dados_brutos:
            dados = dados_brutos['Close']
        else:
            status_msg.error("Erro: Coluna de preço não encontrada.")
            return None, None
            
        # Tratamento Coluna IBOV
        if 'Adj Close' in ibov_bruto:
            ibov = ibov_bruto['Adj Close']
        elif 'Close' in ibov_bruto:
            ibov = ibov_bruto['Close']
        else:
            ibov = ibov_bruto.iloc[:, 0]

        dados = dados.dropna(axis=1, how='all')
        status_msg.success(f"Dados carregados! {dados.shape[1]} ativos processados.")
        return dados, ibov

    except Exception as e:
        status_msg.error(f"Erro ao baixar dados: {e}")
        return None, None

# --- LÓGICA PRINCIPAL ---

# Carrega os dados
dados, ibov = carregar_dados(tickers_br, dias_visualizacao)

if dados is not None and ibov is not None:
    
    # --- CÁLCULOS ---
    medias_moveis = [5, 10, 20, 50, 200]
    resultados = pd.DataFrame(index=dados.index)

    with st.spinner("Calculando indicadores..."):
        for mm in medias_moveis:
            df_mm = dados.rolling(window=mm).mean()
            total_validos = df_mm.count(axis=1)
            acima_da_media = dados > df_mm
            qtd_acima = acima_da_media.sum(axis=1)
            # Porcentagem
            resultados[f'MM{mm}_Pct'] = (qtd_acima / total_validos) * 100

        # Limpeza e filtro final
        resultados = resultados.dropna()
        resultados_limpos = resultados.tail(dias_visualizacao)
        ibov_limpo = ibov.reindex(resultados_limpos.index)

    # --- VISUALIZAÇÃO ---
    
    # Configurações visuais
    plt.style.use('ggplot')
    mapa_cores = {5: '#1f77b4', 10: '#00bfa5', 20: '#2ca02c', 50: '#ff7f0e', 200: '#000000'}
    ibov_style = {'color': '#444444', 'linestyle': '-', 'linewidth': 1.0, 'alpha': 0.8}
    
    # Configuração de limites de escala (Agora todos 5% a 95%)
    limites_escala = {
        5: (5, 95),
        10: (5, 95),
        20: (5, 95),
        50: (5, 95),
        200: (5, 95)
    }

    # GRÁFICO 1: Curto Prazo
    st.subheader("⚡ Curto Prazo (MM 5 dias)")
    fig1, ax1 = plt.subplots(figsize=(12, 5))
    
    coluna = 'MM5_Pct'
    ax1.plot(resultados_limpos.index, resultados_limpos[coluna], color=mapa_cores[5], label='Ações > MM5 (%)', linewidth=2)
    ax1.set_ylabel('% de Ações', color=mapa_cores[5])
    ax1.set_ylim(limites_escala[5])
    ax1.fill_between(resultados_limpos.index, resultados_limpos[coluna], alpha=0.1, color=mapa_cores[5])
    ax1.axhline(y=50, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)
    
    # IBOV Secundário
    ax2 = ax1.twinx()
    ax2.plot(ibov_limpo.index, ibov_limpo, label='IBOV', **ibov_style)
    ax2.set_ylabel('Pontos IBOV', color=ibov_style['color'])
    ax2.grid(False)
    
    # Legendas juntas
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    st.pyplot(fig1)

    # GRÁFICOS RESTANTES (Rolagem única)
    
    # Função auxiliar para plotar grupos
    def plot_grupo(mms, titulo):
        st.subheader(f"📅 {titulo}")
        fig, axes = plt.subplots(len(mms), 1, figsize=(12, 4 * len(mms)), sharex=True)
        if len(mms) == 1: axes = [axes]

        for i, mm in enumerate(mms):
            ax = axes[i]
            coluna = f'MM{mm}_Pct'
            cor = mapa_cores.get(mm, 'blue')

            ax.plot(resultados_limpos.index, resultados_limpos[coluna], label=f'> MM {mm} (%)', color=cor, linewidth=2)
            ax.axhline(y=50, color='gray', linestyle='--', linewidth=1.5, alpha=0.6)
            
            ax.set_title(f'Amplitude: MM {mm} Dias', fontsize=10, loc='left')
            ax.set_ylabel('% Ações')
            
            # Aplica escala fixa 5-95%
            ax.set_ylim(limites_escala.get(mm, (5, 95)))
            
            ax.grid(True, linestyle=':', linewidth=0.5)
            ax.fill_between(resultados_limpos.index, resultados_limpos[coluna], alpha=0.1, color=cor)
            
            # IBOV
            ax_ibov = ax.twinx()
            ax_ibov.plot(ibov_limpo.index, ibov_limpo, label='IBOV', **ibov_style)
            ax_ibov.set_ylabel('IBOV', color=ibov_style['color'], fontsize=8)
            ax_ibov.grid(False)

        st.pyplot(fig)

    # Chama as funções sequencialmente (sem Tabs)
    plot_grupo([10, 20], "Médio Prazo (10 e 20 dias)")
    plot_grupo([50, 200], "Longo Prazo (50 e 200 dias)")

    # --- DADOS BRUTOS ---
    with st.expander("📄 Ver Tabela de Dados Detalhada"):
        # Formata para exibir bonitinho
        df_display = pd.concat([resultados_limpos, ibov_limpo.rename("IBOV")], axis=1)
        st.dataframe(df_display.sort_index(ascending=False).style.format("{:.1f}"))

else:
    st.warning("Não foi possível carregar os dados. Verifique a conexão ou tente novamente mais tarde.")