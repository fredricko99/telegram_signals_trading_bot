import MetaTrader5 as mt5
import time
import logging
from datetime import datetime


# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------
logger = logging.getLogger('EXECUTOR')


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
        logger.info("Attempting to initialize MetaTrader 5...")
        print('Attempting to initialize MetaTrader 5..."')

        # If MT5 is already running
        if mt5.terminal_info() is not None:
            logger.info("MT5 terminal already connected.")
            print("MT5 terminal already connected.")
            return True

        # Try to initialize
        if mt5.initialize(
            login=self.login,
            password=self.password,
            server=self.server,
            path=self.path
        ):
            acc = mt5.account_info()
            logger.info(f"✅ MT5 initialized successfully. Logged in as: {acc.login}")
            print(f"✅ MT5 initialized successfully. Logged in as: {acc.login}")
            return True
        
        else:
            error = mt5.last_error()
            logger.error(f"❌ MT5 initialization failed: {error}")
            print(f"❌ MT5 initialization failed: {error}")
            return False


    # ---------------------------------------------------------
    # SYMBOL CHECK
    # ---------------------------------------------------------
    def ensure_symbol(self, symbol):
        """Ensure the symbol is available and selected in MT5."""
        try:
            selected = mt5.symbol_select(symbol, True)
            if not selected:
                logger.error(f"❌ Could not select symbol: {symbol}")
                return False
            return selected
        except Exception as e:
            logger.exception(f"❌ Error selecting symbol {symbol}: {e}")
            return False

    def _get_price(self, symbol):
            """Helper to get current Ask/Bid prices for a symbol."""
            try:
                if not self.ensure_symbol(symbol):
                    return None, None
                    
                tick = mt5.symbol_info_tick(symbol)
                print(tick)
                if tick is None:# or tick.last == 0.0:
                    logger.error(f"❌ Failed to get valid tick data for {symbol}.")
                    print(mt5.last_error())
                    return None, None
                    
                return tick.ask, tick.bid
            except Exception as e:
                logger.exception(f"❌ Exception retrieving price for {symbol}: {e}")
                return None, None

    # ---------------------------------------------------------
    # CORE EXECUTION METHOD
    # ---------------------------------------------------------
    def execute_signal(self, parsed_signal):
        """
        Processes a parsed signal and executes the corresponding market order.
        :param parsed_signal: Dictionary containing 'symbol', 'action', 'stop_loss', etc.
        """
        symbol = parsed_signal.get("symbol")
        action = parsed_signal.get("action")
        # NOTE: You MUST calculate or fetch the lot size from your risk management settings
        #TODO: calculate the risk management. 
        qty = 0.01  # LOW LOT EXAMPLE: Replace with your calculated lot size
        sl = parsed_signal.get("stop_loss", 0.0)
        tp = parsed_signal.get("take_profit_1", 0.0) # Assuming TP1 is the entry TP
        
        if not symbol or not action:
            logger.error("🚨 Signal missing Symbol or Action. Execution skipped.")
            return {"status": "error", "msg": "Incomplete signal data"}

        # 1. Get current market prices
        ask, bid = self._get_price(symbol)
        if ask is None or bid is None:
            return {"status": "error", "msg": f"Could not get valid price for {symbol}"}
        
        # 2. Determine Order Type and Entry Price
        if action == "BUY":
            order_type = mt5.ORDER_TYPE_BUY
            price = ask  # Buy orders fill at the ASK price
            logging.info(f"Preparing BUY order at ASK={ask}")
        elif action == "SELL":
            order_type = mt5.ORDER_TYPE_SELL
            price = bid  # Sell orders fill at the BID price
            logging.info(f"Preparing SELL order at BID={bid}")
        else:
            logger.error(f"⚠️ Unsupported action: {action}")
            return {"status": "error", "msg": f"Unsupported action: {action}"}

        # 3. Adjust Filling Mode (Recommended Fix)
        # The 'ORDER_FILLING_IOC' in your create_order often causes errors.
        # Change the filling mode to FOK or RETURN for better compatibility.
        # NOTE: You must update the create_order method's default filling type.
        
        # 4. Execute Order
        # The create_order method is called with all the necessary parameters
        return self.create_order(symbol, qty, order_type, price, sl, tp)
    # ---------------------------------------------------------
    # ORDER CREATION
    # ---------------------------------------------------------
    def create_order(self, symbol, qty, order_type, price, sl, tp):
        """
        Create & send a market order with error handling + logging.
        """

        # Ensure MT5 is running
        if not mt5.terminal_info():
            logger.error("❌ MT5 not initialized. Call initialize_mt5() first.")
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
                    # FIX: Changed from IOC to FOK (Fill or Kill) for market execution reliability
                    "type_filling": mt5.ORDER_FILLING_FOK, 
                    "comment": "python-open-position"
                }

        logger.info(f"📤 Sending order request: {request}")

        try:
            result = mt5.order_send(request)

            if result is None:
                logger.error("❌ order_send returned None")
                return {"status": "error", "msg": "order_send returned None"}

            # Check MT5 execution response
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(
                    f"❌ ORDER FAILED → retcode={result.retcode}, comment={result.comment}"
                )
                return {
                    "status": "error",
                    "retcode": result.retcode,
                    "comment": result.comment
                }

            logger.info(
                f"✅ ORDER SUCCESS → order_id={result.order}, price={price}, sl={sl}, tp={tp}"
            )
            print(f"✅ ORDER SUCCESS → order_id={result.order}, price={price}, sl={sl}, tp={tp}")
            
            return {
                "status": "success",
                "order_id": result.order,
                "executed_price": result.price,
                "sl": sl,
                "tp": tp
            }

        except Exception as e:
            logger.exception(f"❌ Exception during order_send: {e}")
            return {"status": "exception", "msg": str(e)}


    # ---------------------------------------------------------
    # SHUTDOWN
    # ---------------------------------------------------------
    def shutdown(self):
        """Safely shutdown the MT5 terminal."""
        try:
            mt5.shutdown()
            logger.info("🔌 MT5 terminal successfully shut down.")
        except Exception as e:
            logger.exception(f"⚠ Error shutting down MT5: {e}")
