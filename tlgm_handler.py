import json
from telethon import TelegramClient, events
from dotenv import load_dotenv
from signal_parser import SignalParser  # your parser class

load_dotenv()

class TelegramHandler:
    def __init__(self, api_id, api_hash, session_name, channels: list):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.channels = channels

        # Initialize the Telethon client
        self.client = TelegramClient('sessions/'+self.session_name, self.api_id, self.api_hash)

        # Register the event handler
        self.client.add_event_handler(self.signal_handler, events.NewMessage(chats=self.channels))

    
    async def signal_handler(self, event):
        """
        Called on every new message from the subscribed channels.
        """
        raw_text = event.raw_text
        print("\n📩 New message:")
        print(raw_text)

        # Parse the signal using your SignalParser
        parser = SignalParser()
        parsed = parser.parse(raw_text)

        if parsed:
            print("\n📌 Parsed Signal:")
            print(json.dumps(parsed, indent=4))
            #print(parsed)
            # TODO: send parsed signal to trade executor
        else:
            print("❌ Message ignored (not a signal alert)")

    async def start(self):
        """
        Start the client and listen for messages indefinitely.
        """
        await self.client.start()
        print("✅ Telegram client started. Listening for signals...")
        await self.client.run_until_disconnected()

