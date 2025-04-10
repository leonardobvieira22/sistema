
import pandas as pd
import json

def atualizar_pesos(caminho_csv='sinais_detalhados.csv', caminho_saida='pesos_indicadores.json'):
    try:
        df = pd.read_csv(caminho_csv)
        df = df.dropna(subset=['score_tecnico', 'lucro_percentual'])

        indicadores = ['rsi', 'adx', 'ema_curta', 'ema_longa', 'swing_high', 'swing_low', 'volume', 'ia_score']

        pesos = {}

        for indicador in indicadores:
            acertos = df[(df[indicador].notna()) & (df['lucro_percentual'] > 0)]
            erros = df[(df[indicador].notna()) & (df['lucro_percentual'] <= 0)]
            total = len(acertos) + len(erros)

            if total > 0:
                taxa_acerto = len(acertos) / total
                pesos[indicador] = round(taxa_acerto, 2)
            else:
                pesos[indicador] = 0.5  # peso neutro caso sem dados

        with open(caminho_saida, 'w') as f:
            json.dump(pesos, f, indent=4)

        print("[AUTOAPRENDIZADO] Pesos atualizados com base em histórico.")
        return pesos
    except Exception as e:
        print(f"[AUTOAPRENDIZADO] Erro: {e}")
        return {}
