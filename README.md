# 🧠 Pair-Trading Strategy Project

Một framework Python để xây dựng, tính toán **regime**, sinh **signal z-score**, chạy **backtest spread-based strategy** và xuất **rolling performance metrics**. Project tập trung vào phân tích chiến lược thị trường trung tính (market-neutral) sử dụng cointegration/correlation.

---

## 📌 Mục lục

1. [Giới thiệu](#introduction)
2. [Tính năng chính](#features)
3. [Cấu trúc thư mục](#structure)
4. [Cài đặt & Yêu cầu](#installation)
5. [Hướng dẫn sử dụng](#usage)

   * Chuẩn bị dữ liệu
   * Tính Regime & Signal
   * Chạy Backtest
   * Rolling Metrics & Visualization
6. [Output & Metrics](#output)
7. [Lưu ý & Gợi ý mở rộng](#notes)
8. [License](#license)

---

## 📎 1. Giới thiệu <a name="introduction"></a>

Repo này chứa một framework cho chiến lược **Pair-Trading**, giúp:

* Chọn cặp tài sản phù hợp (cointegration / correlation).
* Tính *regime* (NORMAL / DEGRADED / RESET).
* Sinh *signal* dựa trên z-score và regime.
* Backtest chiến lược trên spread với cost và slippage.
* Xuất các metrics như equity curve, Sharpe, volatility và nhiều hơn. ([GitHub][1])

---

## ⚙️ 2. Tính năng chính <a name="features"></a>

✔ Tính regime và position multiplier từ các metric như p-value, Hurst, half-life, correlation… ([GitHub][1])
✔ Sinh signal z-score regime-aware. ([GitHub][1])
✔ Backtest chiến lược spread-based với các chi phí thực tế. ([GitHub][1])
✔ Rolling performance và regime-aware performance metrics. ([GitHub][1])
✔ Xuất kết quả dưới dạng CSV để dễ visualize. ([GitHub][1])

---

## 📁 3. Cấu trúc thư mục <a name="structure"></a>

````
pair_trading_project/
├── data/                 # Dữ liệu giá, spread, signals
├── execution/
│   └── backtest.py       # Engine backtest SpreadBacktest
├── performance/
│   └── rolling_metrics.py# Rolling / regime-aware metrics
├── modules/
│   ├── signal_engine.py  # Tạo signal từ z-score / regime
│   └── regime_classifier.py # Tính regime & position multiplier
├── notebooks/            # Notebook demo / ví dụ
├── results/              # Output CSV
├── README.md
├── VNI.csv
├── data_10y.csv
└── place_holder
``` :contentReference[oaicite:8]{index=8}

---

## 🛠 4. Cài đặt & Yêu cầu <a name="installation"></a>

**Yêu cầu Python:** ≥ 3.10  
Cài đặt packages cần thiết:

```bash
pip install pandas numpy matplotlib
````

Có thể thêm package khác như `scipy` nếu code phụ thuộc vào các hàm phân tích thống kê. ([GitHub][1])

---

## 🚀 5. Hướng dẫn sử dụng <a name="usage"></a>

### 🔸 5.1 Chuẩn bị dữ liệu

Bạn cần chuẩn bị:

* `price_x`, `price_y`: giá của hai tài sản.
* `spread`: spread được tính (raw spread hoặc log spread).
* Dữ liệu thời gian tương ứng với các giá. ([GitHub][1])

---

### 🧮 5.2 Tính Regime & Signal

Example Python:

````python
from modules.regime_classifier import RegimeClassifier
from modules.signal_engine import SignalEngine

regime_clf = RegimeClassifier(...)
signal_engine = SignalEngine(...)

from modules.walk_forward import WalkForwardEngine
wf = WalkForwardEngine(
    data={'x': price_x, 'y': price_y, 'spread': spread, 'dates': price_x.index, 'pair': 'KO_PEP'},
    modules=[regime_clf, signal_engine]
)
results = wf.run()

import pandas as pd
df_signal = pd.json_normalize(results)
df_signal['position'] = df_signal['signal'] * df_signal['position_multiplier']
``` :contentReference[oaicite:11]{index=11}

---

### 📊 5.3 Chạy Backtest

```python
from execution.backtest import SpreadBacktest

backtester = SpreadBacktest(cost_per_turnover=0.0005, slippage=0.0001, output_path="results/backtest.csv")

for t in range(len(df_signal)):
    signal_dict = {"position": df_signal.iloc[t]['position']}
    backtester.step(t=t, spread=spread, ZScoreSignal=signal_dict)

df_backtest = backtester.finalize(index=df_signal.index)
``` :contentReference[oaicite:12]{index=12}

---

### 📈 5.4 Rolling Metrics & Visualization

```python
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

import matplotlib.pyplot as plt
df_rolling['equity'].plot(title='Equity Curve')
df_rolling['rolling_sharpe_60'].plot(title='Rolling Sharpe')
plt.show()
``` :contentReference[oaicite:13]{index=13}

---

## 📥 6. Output & Metrics <a name="output"></a>

✔ `results/backtest.csv` — equity, pnl, position, turnover, cost…  
✔ `results/rolling_metrics.csv` — rolling Sharpe, volatility, drawdown, exposure, % time in NORMAL regime… :contentReference[oaicite:14]{index=14}

---

## ⚠️ 7. Lưu ý & Mở rộng <a name="notes"></a>

- Chiến lược **market-neutral** nhưng hiệu quả vẫn phụ thuộc vào biến động spread. :contentReference[oaicite:15]{index=15}  
- Transaction cost và slippage ảnh hưởng lớn đến PnL. :contentReference[oaicite:16]{index=16}  
- Có thể mở rộng để thêm:
  - Multi-pair trading  
  - Dynamic thresholds  
  - Machine learning regime detection

---

## 📜 8. License <a name="license"></a>

Distributed under the **MIT License**. :contentReference[oaicite:17]{index=17}

---

Nếu bạn muốn, mình cũng có thể **tối ưu nội dung README theo chuẩn *Markdown README Template*** (bao gồm badges, cách chạy demo, example dataset mẫu, code snippet interactive). Just tell me!
::contentReference[oaicite:18]{index=18}
````

[1]: https://github.com/quann8407-cyber/CF_Quan23280080_Nguyen23280073/tree/main "GitHub - quann8407-cyber/CF_Quan23280080_Nguyen23280073"
