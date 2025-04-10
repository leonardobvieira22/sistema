import streamlit as st
import pandas as pd
import json
import plotly.express as px
from config import CONFIG
import os
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()

TRADES_REAIS_FILE = "trades_reais.csv"
BACKTEST_RESULTS_FILE = "backtest_results.json"

def inicializar_client():
    if CONFIG['dry_run']:
        return Client(os.getenv("TESTNET_API_KEY"), os.getenv("TESTNET_API_SECRET"), testnet=True)
    else:
        return Client(os.getenv("REAL_API_KEY"), os.getenv("REAL_API_SECRET"), testnet=False)

def load_trades_reais():
    if not os.path.exists(TRADES_REAIS_FILE):
        return pd.DataFrame()
    return pd.read_csv(TRADES_REAIS_FILE)

def calcular_confiabilidade_indicadores(df_sinais):
    confiabilidade = {}
    for ind in ["rsi", "bollinger", "estocastico", "volume", "ema", "sentimento", "vwap", "fibonacci"]:
        acertos = df_sinais[df_sinais["motivos"].str.contains(ind, case=False, na=False) & (df_sinais["resultado"] == "TP")].shape[0]
        total = df_sinais[df_sinais["motivos"].str.contains(ind, case=False, na=False)].shape[0]
        confiabilidade[ind] = acertos / total * 100 if total > 0 else 0
    return confiabilidade

st.title("UltraBot Dashboard - Futures Trading")

client = inicializar_client()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Trades", "Backtest", "Carteira", "Posições", "Sinais Detalhados"])

with tab1:
    st.subheader("📈 Trades Executados")
    if os.path.exists("sinais_detalhados.csv"):
        df_trades = pd.read_csv("sinais_detalhados.csv")
        st.dataframe(df_trades[['timestamp', 'par', 'direcao', 'preco_entrada', 'preco_saida', 'lucro_percentual', 'resultado']])
        fig = px.scatter(df_trades, x="timestamp", y="lucro_percentual", color="direcao", title="Lucro por Trade")
        st.plotly_chart(fig)
    else:
        st.write("Nenhum trade registrado.")

with tab2:
    st.subheader("📊 Resultados do Backtest")
    if os.path.exists(BACKTEST_RESULTS_FILE):
        with open(BACKTEST_RESULTS_FILE, 'r') as f:
            results = json.load(f)
        for tf in ["1m", "5m", "15m", "1h", "2h", "4h", "1d"]:
            res = results.get(tf, {'total_trades': 0, 'lucro_total': 0, 'taxa_acerto': 0})
            st.write(f"**{tf}**: Trades: {res['total_trades']}, Lucro: {res['lucro_total']:.2f} USDT, Taxa de Acerto: {res['taxa_acerto']:.2f}%")
    
    st.subheader("📈 Confiabilidade dos Indicadores")
    if os.path.exists("sinais_detalhados.csv"):
        df_sinais = pd.read_csv("sinais_detalhados.csv")
        confiabilidade = calcular_confiabilidade_indicadores(df_sinais)
        fig = px.bar(pd.DataFrame(confiabilidade.items(), columns=["Indicador", "Taxa de Acerto"]), 
                     x="Indicador", y="Taxa de Acerto", title="Confiabilidade por Indicador")
        st.plotly_chart(fig)

with tab3:
    st.subheader("💰 Carteira")
    try:
        account = client.futures_account()
        saldo_total = float(account['totalWalletBalance'])
        margem_usada = float(account['totalMarginBalance']) - float(account['totalCrossUnPnl'])
        pnl_nao_realizado = float(account['totalCrossUnPnl'])
        st.write(f"**Saldo Total**: {saldo_total:.2f} USDT")
        st.write(f"**Margem Usada**: {margem_usada:.2f} USDT")
        st.write(f"**PNL Não Realizado**: {pnl_nao_realizado:.2f} USDT")
        if os.path.exists("sinais_detalhados.csv"):
            df_trades = pd.read_csv("sinais_detalhados.csv")
            lucro_total = df_trades['pnl_realizado'].sum()
            st.write(f"**Lucro Total Realizado**: {lucro_total:.2f} USDT")
    except Exception as e:
        st.write(f"Erro ao carregar carteira: {e}")

with tab4:
    st.subheader("📌 Posições Abertas")
    try:
        positions = client.futures_position_information()
        df_positions = pd.DataFrame([p for p in positions if float(p['positionAmt']) != 0])
        if not df_positions.empty:
            st.dataframe(df_positions[['symbol', 'positionAmt', 'entryPrice', 'unRealizedProfit', 'leverage']])
            fig = px.bar(df_positions, x="symbol", y="unRealizedProfit", title="PNL Não Realizado por Posição")
            st.plotly_chart(fig)
        else:
            st.write("Nenhuma posição aberta.")
    except Exception as e:
        st.write(f"Erro ao carregar posições: {e}")

with tab5:
    st.subheader("🔍 Sinais Detalhados")
    if os.path.exists("sinais_detalhados.csv"):
        df_sinais = pd.read_csv("sinais_detalhados.csv").tail(5)
        for _, sinal in df_sinais.iterrows():
            with st.expander(f"{sinal['par']} - {sinal['timeframe']} - {sinal['direcao']}"):
                score_class = "Alto" if sinal['score_tecnico'] >= 75 else "Médio" if sinal['score_tecnico'] >= 50 else "Baixo"
                st.write(f"**Timestamp**: {sinal['timestamp']}")
                st.write(f"**Preço Entrada**: {sinal['preco_entrada']:.4f}")
                st.write(f"**Preço Saída**: {sinal.get('preco_saida', 'N/A')}")
                st.write(f"**Score Total**: {sinal['score_tecnico']:.2f} ({score_class})")
                st.write(f"**Motivos**: {sinal['motivos']}")
                st.write(f"**Funding Rate**: {sinal.get('funding_rate', 'N/A'):.4f}")
                st.write(f"**Resultado**: {'✅ Aceito' if sinal['aceito'] else '❌ Recusado'}")
                st.write(f"**Ação**: {'Executado' if sinal['aceito'] else 'Não Executado'} ({'Dry Run' if CONFIG['dry_run'] else 'Real'})")
    else:
        st.write("Nenhum sinal registrado ainda.")

with st.sidebar:
    st.subheader("⚙️ Configurações")
    CONFIG["dry_run"] = st.checkbox("Dry Run", value=CONFIG["dry_run"])
    CONFIG["mercado"] = st.selectbox("Mercado", ["futures", "spot"], index=0 if CONFIG["mercado"] == "futures" else 1)
    CONFIG["leverage"] = st.slider("Alavancagem", 1, 125, CONFIG["leverage"])
    for ind in ["rsi", "vwap", "fibonacci", "bollinger", "estocastico", "volume", "ema", "sentimento"]:
        CONFIG[f"usar_{ind}"] = st.checkbox(f"Usar {ind.capitalize()}", value=CONFIG[f"usar_{ind}"])