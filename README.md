# Pair Trading Backtest và Optimization cho Cổ phiếu VN

Mục tiêu của dự án:
- Xây dựng chiến lược pair trading market-neutral cho các cặp cổ phiếu VN.
- Sử dụng spread, z-score và volatility filter để ra quyết định mua/bán.
- Backtest chiến lược trong quá khứ và tối ưu tham số (window, entry_z, exit_z).
- 
Dữ liệu sử dụng:
- Giá đóng cửa hàng ngày của các cổ phiếu: BID.VN, VCB.VN, CTG.VN, MBB.VN,...
- Thời gian: 8 năm trước để tối ưu tham số, 2 năm gần đây để backtest.
- Các cột: close price, spread, beta, z-score, spread volatility.

Chiến lược pair trading:
1. Tính spread giữa 2 cổ phiếu: spread = price1 - beta * price2
2. Tính z-score của spread dựa trên rolling window
3. Entry signal:
   - z-score > entry_z → short spread (bán stock1, mua stock2)
   - z-score < -entry_z → long spread (mua stock1, bán stock2)
   - Chỉ trade khi spread volatility > vol_lower (tránh thị trường quá yên tĩnh)
4. Exit signal:
   - Sử dụng z-score
5. Quản lý rủi ro:
   - Max % vốn per trade
   - Stop-loss
   - Transaction fees: buy_fee, sell_fee

Cấu trúc
  - pair_trading_signals.py: Tính beta, spread, z-score và tạo tín hiệu
  - backtest_pair_safe_fixed_shift.py: Backtest chiến lược với quản lý vốn, stop-loss, volatility filter
  - optimize.py: Tối ưu tham số (window, entry_z, exit_z) dựa trên PNL
  - utils.py: Các hàm hỗ trợ

Cách chạy
1. Chuẩn bị dữ liệu CSV hoặc DataFrame với cột close price
2. Chạy pair_trading_signals để tạo signal
3. Chạy backtest_pair_safe_fixed_shift để xem kết quả equity, PNL
4. Chạy optimize.py để tìm bộ tham số tối ưu

Kết quả
- Cặp được chọn là XOM và CVX, PEP và KO
XOM và CVX
<img width="559" height="413" alt="image" src="https://github.com/user-attachments/assets/6df37b87-7437-427e-9856-9ca5058f50d6" />

  
Ghi chú
- Chiến lược market-neutral nhưng hiệu quả phụ thuộc vào biến động spread
- Volatility filter giúp tránh trade trong thị trường quá yên tĩnh
- Phí giao dịch và slippage ảnh hưởng đáng kể tới PNL
- Có thể mở rộng: multi-pair trading, cặp ngành khác, dynamic thresholds

