import os
import asyncio
from dotenv import load_dotenv

# 1. Import Handlers and Parsers from your source directory (src)
from src.tlgm_handler import TelegramHandler
from src.trade_executor import Trade_Executor 

async def main():
    # Load environment variables from .env file
    load_dotenv()

    # 2. Get secrets/config
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    session = os.getenv("TELEGRAM_SESSION")
    
    mt5_account = os.getenv('Mt5_ACCOUNT')
    mt5_password = os.getenv('MT5_PASSWORD')
    mt5_server = os.getenv('MT5_SERVER')
    
    if not (api_id and api_hash):
        print("❌ ERROR: TELEGRAM_API_ID or TELEGRAM_API_HASH not found in environment variables.")
        return

    # 3. Initialize Core Components (MT5/Trade Executor first)
    # The TradeExecutor will handle MT5 connection and order sending logic
    executor = Trade_Executor(
        login=int(mt5_account),
        password=mt5_password,
        server=mt5_server
    )
    if not executor.initialize_mt5():
        print("❌ CRITICAL: Could not initialize MetaTrader 5 connection. Exiting.")
        return
    
    # 4. Initialize Bot Handler
    handler = TelegramHandler(
        api_id=int(api_id),
        api_hash=api_hash,
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