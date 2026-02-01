import json
import logging
from telethon import TelegramClient, events
from dotenv import load_dotenv
from .signal_parser import SignalParser

# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------
logger = logging.getLogger('TELEGRAM_HANDLER')

load_dotenv()

class TelegramHandler:
    def __init__(self, api_id, api_hash, session_name, executor, channels=None, channels_path="config/channels.json"):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.channels_path = channels_path
        
        #store the executor
        self.executor = executor

        # Load channels (either passed directly or from JSON)
        self.channels = channels if channels else self.load_channels_from_json()

        # Validate before creating client
        if not self.channels:
            print("❌ ERROR: No channels found. Cannot start Telegram client.")
            logger.error('❌ ERROR: No channels found. Cannot start Telegram client.')
            self.client = None
            return
        
        # Initialize the client only if channels exist
        self.client = TelegramClient(f'sessions/{self.session_name}', self.api_id, self.api_hash)

        # Register the event handler
        self.client.add_event_handler(self.signal_handler, events.NewMessage(chats=self.channels))


    # ---------------------------
    # Load Channels from JSON
    # ---------------------------
    def load_channels_from_json(self):
        try:
            with open(self.channels_path, "r") as f:
                data = json.load(f)
                channels = data.get("channels", [])
                print(f"📌 Loaded {len(channels)} channel(s) from JSON.")
                logger.info(f"📌 Loaded {len(channels)} channel(s) from JSON : {channels}.")
                return channels
        except FileNotFoundError:
            print(f"❌ channel file not found: {self.channels_path}")
            logger.error(f"❌ channel file not found: {self.channels_path}")
        except json.JSONDecodeError:
            print(f"❌ JSON format error in: {self.channels_path}")
            logger.error(f"❌ JSON format error in: {self.channels_path}")
        except Exception as e:
            print(f"❌ Unexpected error loading channels: {e}")

        return []


    # ---------------------------
    # New Message Handler
    # ---------------------------
    async def signal_handler(self, event):
        raw_text = event.raw_text
        print("\n📩 New message:")
        print(raw_text)

        parser = SignalParser()
        parsed = parser.parse(raw_text)

        if parsed and parsed.get("symbol") and parsed.get("action"):
                    print("📌 Parsed Signal:")
                    logger.info(f' Parsed Signal {parsed}')
                    print(json.dumps(parsed, indent=4))
                    
                    #  NEW: Trigger the Trade_Executor
                    if self.executor:
                        print(">>> 🚀 Passing signal to Trade Executor...")
                        # The executor handles retrieving the price and sending the order
                        trade_result = self.executor.execute_signal(parsed)
                        
                        # Send confirmation message back to the chat (optional)
                        if trade_result.get("status") == "success":
                            await event.respond(f"✅ TRADE EXECUTED: {parsed['action']} {parsed['symbol']} (Order: {trade_result['order_id']})")
                            print((f"✅ TRADE EXECUTED: {parsed['action']} {parsed['symbol']} (Order: {trade_result['order_id']})"))
                            logger.info(f"✅ TRADE EXECUTED: {parsed['action']} {parsed['symbol']} (Order: {trade_result['order_id']})")
                        else:
                            await event.respond(f"❌ TRADE FAILED: {parsed['action']} {parsed['symbol']} ({trade_result.get('comment', trade_result.get('msg', 'Check logs for details.'))})")
                    else:
                        print("❌ Executor not initialized. Trade execution skipped.")

        else:
            print("❌ Not a valid signal → ignored")


    # ---------------------------
    # Start Listening
    # ---------------------------
    async def start(self):
        """Start the Telegram client only if valid."""
        if not self.client:
            print("❌ Telegram client was not created. Fix channels and restart.")
            return
        
        if not self.channels:
            print("❌ Cannot start client — channel list is empty.")
            return

        await self.client.start()
        print("✅ Telegram client started. Listening for signals...")
        await self.client.run_until_disconnected()
