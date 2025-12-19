# Pair-Trading Strategy Project

## 1. Giới thiệu
Dự án này là framework **pair-trading** với khả năng:

- Chọn cặp cổ phiếu/phái sinh có cointegration / correlation phù hợp.
- Tính **regime** (NORMAL / DEGRADED / RESET) dựa trên các metric: ADF p-value, cointegration p-value, Hurst, half-life, correlation…
- Sinh **signal z-score** với position multiplier tùy regime.
- Thực hiện **backtest spread-based strategy** với turnover, cost, slippage.
- Tính và xuất **rolling performance metrics** như equity, drawdown, Sharpe, volatility, exposure và regime-aware metrics.

---

## 2. Cấu trúc thư mục
pair_trading_project/
│
├── data/ # Thư mục dữ liệu (giá, spread, signals)
├── execution/
│ └── backtest.py # Backtest engine SpreadBacktest
├── performance/
│ └── rolling_metrics.py # Rolling / regime-aware performance metrics
├── modules/
│ ├── signal_engine.py # Tạo signal từ z-score / regime
│ └── regime_classifier.py# Tính regime & position multiplier
├── notebooks/ # Notebook demo / ví dụ chạy
├── results/ # Output CSV: backtest, rolling metrics
└── README.md


---

## 3. Cài đặt

Python ≥ 3.10. Cài đặt các package cần thiết:

bash
pip install pandas numpy matplotlib
##4. Hướng dẫn sử dụng
###4.1 Chuẩn bị dữ liệu

price_x, price_y: giá của 2 tài sản trong cặp.

spread: difference hoặc log spread.

df_signal: dataframe chứa signal, z-score và position_multiplier.

###4.2 Tính Regime và Signal
from modules.regime_classifier import RegimeClassifier
from modules.signal_engine import SignalEngine

regime_clf = RegimeClassifier(...)
signal_engine = SignalEngine(...)

# Walk-forward engine
wf = WalkForwardEngine(
    data={'x': price_x, 'y': price_y, 'spread': spread, 'dates': price_x.index, 'pair': 'KO_PEP'},
    modules=[regime_clf, signal_engine]
)

results = wf.run()  # list of dict

# Chuyển list dict → DataFrame df_signal
import pandas as pd
df_signal = pd.json_normalize(results)
df_signal['position'] = df_signal['signal'] * df_signal['position_multiplier']

#4.3 Chạy Backtest
from execution.backtest import SpreadBacktest

backtester = SpreadBacktest(cost_per_turnover=0.0005, slippage=0.0001, output_path="results/backtest.csv")

for t in range(len(df_signal)):
    signal_dict = {"position": df_signal.iloc[t]['position']}
    backtester.step(t=t, spread=spread, ZScoreSignal=signal_dict)

df_backtest = backtester.finalize(index=df_signal.index)


Kết quả: df_backtest với position, pnl, equity, turnover, cost

###4.4 Rolling Metrics & Visualization
from performance.rolling_metrics import RollingPerformanceMetrics

rolling = RollingPerformanceMetrics(
    csv_path="results/backtest.csv",
    output_path="results/rolling_metrics.csv",
    freq=252
)

df_rolling = rolling.run(
    sharpe_window=60,
    vol_window=60,
    turnover_window=20,
    exposure_window=20,
    regime_window=60
)

# Plot
import matplotlib.pyplot as plt
df_rolling['equity'].plot(title='Equity Curve')
df_rolling['rolling_sharpe_60'].plot(title='Rolling Sharpe')
plt.show()

###5. Metrics có thể phân tích

Equity curve & Drawdown

Sharpe, Volatility (rolling hoặc toàn bộ)

Turnover & Exposure

Regime-aware metrics (% thời gian NORMAL regime)

###6. Lưu ý

Backtest sử dụng position multiplier từ regime

Các chi phí giao dịch (cost_per_turnover, slippage) được tính trong SpreadBacktest.

Rolling metrics hỗ trợ tùy window (60 ngày, 20 ngày…) để phân tích động.

###7. Output

results/backtest.csv → equity, pnl, position, turnover, cost

results/rolling_metrics.csv → rolling Sharpe, vol, drawdown, exposure, pct_normal_regime

  
Ghi chú
- Chiến lược market-neutral nhưng hiệu quả phụ thuộc vào biến động spread
- Phí giao dịch và slippage ảnh hưởng đáng kể tới PNL
- Có thể mở rộng: multi-pair trading, cặp ngành khác, dynamic thresholds

