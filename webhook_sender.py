# webhook_sender.py
import aiohttp
from config import WEBHOOK_URL

async def send_webhook(data):
    if not WEBHOOK_URL:
        return
        
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(WEBHOOK_URL, json=data) as response:
                if response.status == 200:
                    print("✅ Gửi webhook thành công!")
                else:
                    print(f"⚠️ Lỗi webhook: {response.status}")
    except Exception as e:
        print(f"❌ Lỗi gửi webhook: {e}")