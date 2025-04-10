import pandas as pd
import json
import os

def realizar_backtest(df_sinais):
    timeframes = ['1m', '5m', '15m', '1h', '2h', '4h', '1d']
    results = {tf: {'total_trades': 0, 'lucro_total': 0, 'taxa_acerto': 0, 'max_drawdown': 0, 'trades': []} for tf in timeframes}
    
    for _, trade in df_sinais.iterrows():
        tf = trade['timeframe']
        if tf not in results or pd.isna(trade['lucro_percentual']):
            continue
        results[tf]['total_trades'] += 1
        lucro = trade['pnl_realizado']  # Usar PNL realizado
        results[tf]['lucro_total'] += lucro
        results[tf]['trades'].append(lucro)
        if trade['resultado'] == "TP":
            results[tf]['taxa_acerto'] += 1
    
    for tf in results:
        if results[tf]['total_trades'] > 0:
            results[tf]['taxa_acerto'] = (results[tf]['taxa_acerto'] / results[tf]['total_trades']) * 100
            cumsum = pd.Series(results[tf]['trades']).cumsum()
            results[tf]['max_drawdown'] = min(0, cumsum.min())
    
    with open("backtest_results.json", "w") as f:
        json.dump(results, f)