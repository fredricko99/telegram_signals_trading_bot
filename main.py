import asyncio
import os
from dotenv import load_dotenv
from tlgm_handler import TelegramHandler


load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION_NAME= "signals_session"


if __name__ == "__main__":
    CHANNELS = [
        "https://t.me/test_kunos"
    ]
    
    handler = TelegramHandler(API_ID, API_HASH, SESSION_NAME, CHANNELS)
    asyncio.run(handler.start())