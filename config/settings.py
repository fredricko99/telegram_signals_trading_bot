import os
import json
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.TG_API_ID = int(os.getenv("TELEGRAM_API_ID"))
        self.TG_API_HASH = os.getenv("TELEGRAM_API_HASH")

        self.MT5_LOGIN = int(os.getenv("MT5_LOGIN"))
        self.MT5_PASSWORD = os.getenv("MT5_PASSWORD")
        self.MT5_SERVER = os.getenv("MT5_SERVER")
        self.MT5_PATH = os.getenv("MT5_PATH")

        self.CHANNELS = self._load_json("config/channels.json")["channels"]
        self.RISK = self._load_json("config/risk.json")

    @staticmethod
    def _load_json(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)


def load_settings():
    return Settings()
