# monitor.py
import asyncio
import json
import datetime
import websockets
from config import SOLANA_WS, WEBHOOK_URL
from webhook_sender import send_webhook

stop_event = asyncio.Event()

def format_realtime_log(data):
    owner = data["params"]["result"]["value"]["owner"]
    lamports = data["params"]["result"]["value"].get("lamports", 0)
    time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return (
        "\n📌 GIAO DỊCH MỚI (Real-time)\n"
        "────────────────────────────\n"
        f"🕒 Thời gian    : {time_str}\n"
        f"👛 Chủ sở hữu   : {owner}\n"
        f"💰 Số dư mới    : {lamports / 1_000_000_000:.6f} SOL\n"
        "────────────────────────────\n"
    )

async def monitor_account(address):
    async with websockets.connect(SOLANA_WS) as websocket:
        await websocket.send(json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "accountSubscribe",
            "params": [address, {"encoding": "jsonParsed"}]
        }))

        print(f"🔄 Đang theo dõi ví {address} (ấn Ctrl+C để dừng)...")

        try:
            while not stop_event.is_set():
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)

                    if "method" in data and data["method"] == "accountNotification":
                        print("📡 Giao dịch mới phát hiện:")
                        print(format_realtime_log(data))

                        await send_webhook(data)

                except asyncio.TimeoutError:
                    continue

        except asyncio.CancelledError:
            print("🛑 Đã dừng giám sát.")
        finally:
            print("👋 Ngắt kết nối websocket.")

async def run_monitor(address):
    task = asyncio.create_task(monitor_account(address))
    try:
        await task
    except KeyboardInterrupt:
        print("\n🧹 Dừng theo dõi...")
        stop_event.set()
        task.cancel()
        await asyncio.sleep(0.5)
