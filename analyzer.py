# analyzer.py
import requests
import datetime
from config import SOLANA_RPC

LAMPORTS_PER_SOL = 1_000_000_000

def get_confirmed_signatures(address, limit=50):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [address, {"limit": limit}]
    }
    res = requests.post(SOLANA_RPC, json=payload).json()
    return res.get("result", [])

def get_tx_details(signature):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [signature, {"encoding": "jsonParsed"}]
    }
    res = requests.post(SOLANA_RPC, json=payload).json()
    return res.get("result", None)

def analyze_wallet_history(address):
    print(f"\n📊 Phân tích lịch sử giao dịch cho ví: {address}\n")
    filename = f"{address}.txt"
    with open(filename, "w", encoding="utf-8") as f:

        signatures = get_confirmed_signatures(address, limit=50)
        if not signatures:
            print("⚠️ Không tìm thấy giao dịch nào gần đây.")
            return

        for idx, entry in enumerate(signatures, 1):
            signature = entry["signature"]
            tx = get_tx_details(signature)
            if not tx:
                continue

            meta = tx.get("meta", {})
            tx_data = tx.get("transaction", {})
            if not meta or not tx_data:
                continue

            sender = tx_data["message"]["accountKeys"][0]["pubkey"]
            instructions = tx_data["message"]["instructions"]
            lamports = 0
            receiver = "?"

            for ix in instructions:
                if ix.get("program") == "system":
                    receiver = ix["parsed"]["info"]["destination"]
                    lamports = ix["parsed"]["info"]["lamports"] / LAMPORTS_PER_SOL

            fee = meta.get("fee", 0) / LAMPORTS_PER_SOL
            status = "✅ Thành công" if meta.get("err") is None else "❌ Thất bại"
            time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            f.write("────────────────────────────\n")
            f.write(f"🔗 Tx Hash      : {signature}\n")
            f.write(f"🕒 Thời gian    : {time_str}\n")
            f.write(f"👤 Người gửi    : {sender}\n")
            f.write(f"📥 Người nhận   : {receiver}\n")
            f.write(f"💰 Số tiền      : {lamports:.6f} SOL\n")
            f.write(f"⛽ Phí giao dịch: {fee:.6f} SOL\n")
            f.write(f"{status}\n")
            f.write("────────────────────────────\n")
