from fastapi import FastAPI, Request
import config
import uvicorn
import datetime
import requests

app = FastAPI()

LAMPORTS_PER_SOL = 1_000_000_000

def get_latest_transaction(address):
    # Lấy signature giao dịch mới nhất
    sig_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [address, {"limit": 1}]
    }
    sig_res = requests.post(config.SOLANA_RPC, json=sig_payload, timeout=10).json()
    signatures = sig_res.get("result", [])
    if not signatures:
        return None

    signature = signatures[0]["signature"]

    # Lấy chi tiết giao dịch
    tx_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [signature, {"encoding": "jsonParsed"}]
    }
    tx_res = requests.post(config.SOLANA_RPC, json=tx_payload, timeout=10).json()
    tx = tx_res.get("result", None)
    if not tx:
        return None

    return signature, tx

def format_tx_log(signature, tx):
    meta = tx.get("meta", {})
    tx_data = tx.get("transaction", {})
    if not meta or not tx_data:
        return None

    try:
        sender = tx_data["message"]["accountKeys"][0]["pubkey"]
        instructions = tx_data["message"]["instructions"]
        receiver = "?"
        lamports = 0
        for ix in instructions:
            if ix.get("program") == "system":
                info = ix.get("parsed", {}).get("info", {})
                receiver = info.get("destination", "?")
                lamports = info.get("lamports", 0) / LAMPORTS_PER_SOL
                break
    except:
        sender, receiver, lamports = "?", "?", 0

    fee = meta.get("fee", 0) / LAMPORTS_PER_SOL
    status = "✅ Thành công" if meta.get("err") is None else "❌ Thất bại"
    time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return (
        "────────────────────────────\n"
        f"🔗 Tx Hash      : {signature}\n"
        f"🕒 Thời gian    : {time_str}\n"
        f"👤 Người gửi    : {sender}\n"
        f"📥 Người nhận   : {receiver}\n"
        f"💰 Số tiền      : {lamports:.6f} SOL\n"
        f"⛽ Phí giao dịch: {fee:.6f} SOL\n"
        f"{status}\n"
        "────────────────────────────\n"
    )

@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()
    try:
        address = config.MONITORED_ADDRESS
        tx_data = get_latest_transaction(address)
        if not tx_data:
            print("⚠️ Không lấy được giao dịch mới nhất.")
            return {"status": "no_tx"}

        signature, tx = tx_data
        log = format_tx_log(signature, tx)

        if log:
            print(log)
            # Ghi log mới vào đầu file (nếu file đã tồn tại)
            try:
                with open(f"{address}.txt", "r", encoding="utf-8") as f:
                    old = f.read()
            except FileNotFoundError:
                old = ""

            with open(f"{address}.txt", "w", encoding="utf-8") as f:
                f.write(log + "\n" + old)
        else:
            print("⚠️ Không thể phân tích giao dịch.")

    except Exception as e:
        print(f"❌ Lỗi xử lý webhook: {e}")

    return {"status": "ok"}

def run_webhook_server():
    uvicorn.run("webhook_server:app", host="0.0.0.0", port=8000, log_level="error")
