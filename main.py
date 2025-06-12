# main.py
import asyncio
import threading
from analyzer import analyze_wallet_history
from monitor import run_monitor
from webhook_server import run_webhook_server  # bạn sẽ tạo hàm này
import config

async def main():
    wallet = input("🔐 Nhập địa chỉ ví Solana để theo dõi: ").strip()
    config.MONITORED_ADDRESS = wallet  # thêm biến động trong config

    # Khởi động webhook server trong thread riêng
    thread = threading.Thread(target=run_webhook_server, daemon=True)
    thread.start()

    # Phân tích lịch sử và ghi vào file
    analyze_wallet_history(wallet)

    # Bắt đầu theo dõi realtime
    await run_monitor(wallet)

if __name__ == "__main__":
    asyncio.run(main())
