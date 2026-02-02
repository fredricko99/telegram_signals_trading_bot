# Telegram Signals Trading Bot

Automated trading system that listens to Telegram signal channels, parses trading signals, applies risk management rules, and executes trades on MetaTrader 5 or via FXBlue. Includes structured logging and is designed for VPS deployment.

    Listen to multiple Telegram signal channels

    Signal recognition & parsing

    Risk management ( TP splitting)

    Automated trade execution (MT5 / FXBlue)

    Structured logging per module

Python version: 3.11.4

**FILE STURCTURE**

        telegram_signals_trading_bot/
        │
        ├── main.py
        ├── requirements.txt
        ├── .env
        ├── .gitignore
        │
        ├── config/
        │   ├── settings.py
        │   ├── channels.json
        │   ├── risk.json
        │   └── logging_config.py
        │
        ├── sessions/
        │   └── signals_session.session
        │
        ├── logs/
        │   ├── app.log
        │   ├── telegram.log
        │   ├── parser.log
        │   ├── risk.log
        │   └── trades.log
        │
        ├── src/
        │   ├── telegram/
        │   ├── parser/
        │   ├── risk/
        │   └── execution/


**CONFIGURATIONS**

    env config:
        TELEGRAM_API_ID=123456
        TELEGRAM_API_HASH=your_api_hash

        MT5_LOGIN=12345678
        MT5_PASSWORD=your_password
        MT5_SERVER=Broker-Server
        MT5_PATH=your mt5 path
    
    Telegram channels config:
        channels list are in config/channels.json


**LOGGING**

        Logs are written to the logs/ directory:

        telegram.log – Telegram messages

        parser.log – Parsing decisions

        risk.log – Risk checks

        trades.log – Order execution

        app.log – General system logs