import os
import asyncio
from dotenv import load_dotenv

#Import Handlers and Parsers from your source directory (src)
from src.tlgm_handler import TelegramHandler
from src.trade_executor import Trade_Executor 

#import settings
from config.settings import load_settings

#set up the logger
from config.logging_config import setup_logging


async def main():
    # Load environment variables from .env file
    load_dotenv()
    #load logging setup
    setup_logging()
    settings = load_settings()

    # 2. Get secrets/config
    session = os.getenv("TELEGRAM_SESSION")
    
    if not (settings.TG_API_ID and settings.TG_API_HASH):
        print("❌ ERROR: TELEGRAM_API_ID or TELEGRAM_API_HASH not found in environment variables.")
        return

    # 3. Initialize Core Components (MT5/Trade Executor first)
    # The TradeExecutor handles MT5 connection and order sending logic
    executor = Trade_Executor(
        login=settings.MT5_LOGIN,
        password=settings.MT5_PASSWORD,
        server=settings.MT5_SERVER,
        path= settings.MT5_PATH
    )
    if not executor.initialize_mt5():
        print("❌ CRITICAL: Could not initialize MetaTrader 5 connection. Exiting.")
        return
    
    # 4. Initialize Bot Handler
    handler = TelegramHandler(
        api_id=settings.TG_API_ID,
        api_hash=settings.TG_API_HASH,
        #channels=CHANNELS,
        session_name=session,
        executor=executor
    )

    # 5. Start the Event Loop
    try:
        await handler.start()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped manually.")
    except Exception as e:
        print(f"\n🔥 An unhandled exception occurred: {e}")
    finally:
        # Clean up resources (shut down MT5 connection)
        executor.shutdown()
        print("✅ MT5 connection shut down.")
        
if __name__ == "__main__":
    # Ensure the asyncio loop runs until the client disconnects
    asyncio.run(main())