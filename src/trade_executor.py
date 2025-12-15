import MetaTrader5 as mt5
import time
import logging
from datetime import datetime

# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------
logging.basicConfig(
    filename="logs/trade_executor.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


class Trade_Executor:
    """
    Handles connection, data retrieval, pricing, and trade execution with MetaTrader 5.
    """

    def __init__(self, login=None, password=None, server=None, path=None):
        self.login = login
        self.password = password
        self.server = server
        self.path = path
        self.magic = 10000  # Unique bot order ID


    # ---------------------------------------------------------
    # MT5 INITIALIZATION
    # ---------------------------------------------------------
    def initialize_mt5(self):
        """Initialize MT5 terminal with full logging & error handling."""
        logging.info("Attempting to initialize MetaTrader 5...")

        # If MT5 is already running
        if mt5.terminal_info() is not None:
            logging.info("MT5 terminal already connected.")
            return True

        # Try to initialize
        if mt5.initialize(
            login=self.login,
            password=self.password,
            server=self.server,
            #path=self.path
        ):
            acc = mt5.account_info()
            logging.info(f"✅ MT5 initialized successfully. Logged in as: {acc.login}")
            return True
        
        else:
            error = mt5.last_error()
            logging.error(f"❌ MT5 initialization failed: {error}")
            return False


    # ---------------------------------------------------------
    # SYMBOL CHECK
    # ---------------------------------------------------------
    def ensure_symbol(self, symbol):
        """Ensure the symbol is available and selected in MT5."""
        try:
            if not mt5.symbol_select(symbol, True):
                logging.error(f"❌ Could not select symbol: {symbol}")
                return False
            return True
        except Exception as e:
            logging.exception(f"❌ Error selecting symbol {symbol}: {e}")
            return False


    # ---------------------------------------------------------
    # ORDER CREATION
    # ---------------------------------------------------------
    def create_order(self, symbol, qty, order_type, price, sl, tp):
        """
        Create & send a market order with error handling + logging.
        """

        # Ensure MT5 is running
        if not mt5.terminal_info():
            logging.error("❌ MT5 not initialized. Call initialize_mt5() first.")
            return {"status": "error", "msg": "MT5 not initialized"}

        # Ensure symbol exists
        if not self.ensure_symbol(symbol):
            return {"status": "error", "msg": f"Symbol {symbol} not available"}

        # Build order request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": qty,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "magic": self.magic,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
            "comment": "python-open-position"
        }

        logging.info(f"📤 Sending order request: {request}")

        try:
            result = mt5.order_send(request)

            if result is None:
                logging.error("❌ order_send returned None")
                return {"status": "error", "msg": "order_send returned None"}

            # Check MT5 execution response
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logging.error(
                    f"❌ ORDER FAILED → retcode={result.retcode}, comment={result.comment}"
                )
                return {
                    "status": "error",
                    "retcode": result.retcode,
                    "comment": result.comment
                }

            logging.info(
                f"✅ ORDER SUCCESS → order_id={result.order}, price={price}, sl={sl}, tp={tp}"
            )

            return {
                "status": "success",
                "order_id": result.order,
                "executed_price": result.price,
                "sl": sl,
                "tp": tp
            }

        except Exception as e:
            logging.exception(f"❌ Exception during order_send: {e}")
            return {"status": "exception", "msg": str(e)}


    # ---------------------------------------------------------
    # SHUTDOWN
    # ---------------------------------------------------------
    def shutdown(self):
        """Safely shutdown the MT5 terminal."""
        try:
            mt5.shutdown()
            logging.info("🔌 MT5 terminal successfully shut down.")
        except Exception as e:
            logging.exception(f"⚠ Error shutting down MT5: {e}")
