import json
from telethon import TelegramClient, events
from dotenv import load_dotenv
from signal_parser import SignalParser  # your parser class

load_dotenv()

class TelegramHandler:
    def __init__(self, api_id, api_hash, session_name, channels=None, channels_path="config/channels.json"):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.channels_path = channels_path

        # Load channels from JSON if not provided explicitly
        self.channels = channels if channels else self.load_channels_from_json()

        # Initialize the Telethon client
        self.client = TelegramClient(f'sessions/{self.session_name}', self.api_id, self.api_hash)

        # Register event handler
        self.client.add_event_handler(self.signal_handler, events.NewMessage(chats=self.channels))


    # ---------------------------
    #   Load Channels from JSON
    # ---------------------------
    def load_channels_from_json(self):
        try:
            with open(self.channels_path, "r") as f:
                data = json.load(f)
                channels = data.get("channels", [])
                print(f"📌 Loaded {len(channels)} channel(s) from JSON.")
                return channels
        except FileNotFoundError:
            print(f"❌ channel file not found: {self.channels_path}")
        except json.JSONDecodeError:
            print(f"❌ JSON format error in: {self.channels_path}")
        except Exception as e:
            print(f"❌ Unexpected error loading channels: {e}")

        return []  # fallback


    # ---------------------------
    #   Message Handler
    # ---------------------------
    async def signal_handler(self, event):
        """
        Called on every new message from the subscribed channels.
        """
        raw_text = event.raw_text
        print("\n📩 New message:")
        print(raw_text)

        parser = SignalParser()
        parsed = parser.parse(raw_text)

        if parsed:
            print("\n📌 Parsed Signal:")
            print(json.dumps(parsed, indent=4))
            # TODO: forward parsed data to trading logic
        else:
            print("❌ Not a valid signal → ignored")


    # ---------------------------
    #   Start Listening
    # ---------------------------
    async def start(self):
        """Start the Telegram client and keep listening."""
        await self.client.start()
        print("✅ Telegram client started. Listening for signals...")
        await self.client.run_until_disconnected()
