# Solana Wallet Watcher

Một công cụ Python giúp **theo dõi giao dịch của ví Solana** theo thời gian thực, đồng thời phân tích lịch sử giao dịch và xử lý webhook linh hoạt.

---

## MỤC TIÊU DỰ ÁN

- Giám sát 1 địa chỉ ví Solana duy nhất (chỉ định từ đầu)
- In ra màn hình mọi thay đổi giao dịch theo thời gian thực
- Ghi chi tiết lịch sử giao dịch thành file `.txt`
- Gửi hoặc nhận webhook để xử lý theo mô hình client-server

---

## CÁC CHỨC NĂNG CHÍNH

### 1. Nhập địa chỉ ví và bắt đầu theo dõi

- Khi chạy `main.py`, người dùng được yêu cầu nhập địa chỉ ví
- Địa chỉ này sẽ được gán vào `config.MONITORED_ADDRESS`

---

### 2. Phân tích lịch sử giao dịch

- Gọi `getSignaturesForAddress` → lấy danh sách signature
- Gọi `getTransaction` cho từng signature
- Ghi chi tiết vào file `WALLET.txt`:
  - Tx hash
  - Người gửi, người nhận
  - Số tiền (SOL), phí giao dịch
  - Trạng thái thành công/thất bại
- Mỗi lần chạy sẽ phân tích lại và **ghi đè nội dung mới**

---

### 3. Theo dõi real-time qua WebSocket

- Dùng `accountSubscribe` từ `wss://api.mainnet-beta.solana.com`
- Khi ví có thay đổi (balance), sẽ:
  - In ra log real-time
  - Gửi dữ liệu sang webhook (nếu cấu hình)

---

### 4. Webhook xử lý nâng cao (Webhook Server)

- `webhook_server.py` chạy FastAPI tại port `8000`
- Khi nhận webhook:
  - Lấy địa chỉ ví từ `config.MONITORED_ADDRESS`
  - Truy vấn lại `getSignaturesForAddress` và `getTransaction`
  - Ghi log mới vào đầu file `.txt`
  - In ra màn hình dưới định dạng phân tích đầy đủ

---

### 5. Ghi file lịch sử rõ ràng

- File được tạo theo tên địa chỉ ví: `YOUR_WALLET.txt`
- Định dạng giống như sau:

```text
📌 GIAO DỊCH MỚI (Webhook lịch sử)
────────────────────────────
🔗 Tx Hash      : 3Fke...SDF
🕒 Thời gian    : 2025-06-11 17:30:45
👤 Người gửi    : ABC...
📥 Người nhận   : DEF...
💰 Số tiền      : 0.450000 SOL
⛽ Phí giao dịch: 0.000005 SOL
✅ Thành công
────────────────────────────
```

## 🛠 Cài đặt

```bash
git clone https://github.com/your-username/solana-wallet-watcher.git
cd solana-wallet-watcher
pip install -r requirements.txt
```
