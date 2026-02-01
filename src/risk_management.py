import logging
from datetime import datetime, date
from typing import Dict, List, Optional


logger = logging.getLogger("RiskManager")


class RiskManager:
    """
    Handles all risk management logic for trading:
    - Lot size calculation
    - Risk limits
    - Daily loss protection
    - TP splitting
    """

    def __init__(
        self,
        account_balance: float,
        risk_per_trade: float = 1.0,
        max_open_trades: int = 3,
        max_daily_loss: float = 3.0,
        fixed_lot: Optional[float] = None,
        tp_distribution: List[float] = None,
    ):
        """
        :param account_balance: Current account balance
        :param risk_per_trade: % of balance risked per trade
        :param max_open_trades: Maximum allowed open trades
        :param max_daily_loss: Max daily loss (% of balance)
        :param fixed_lot: Use fixed lot size if provided
        :param tp_distribution: Volume split across TPs (must sum to 1)
        """

        self.account_balance = account_balance
        self.risk_per_trade = risk_per_trade
        self.max_open_trades = max_open_trades
        self.max_daily_loss = max_daily_loss
        self.fixed_lot = fixed_lot

        self.tp_distribution = tp_distribution or [0.5, 0.3, 0.2]

        if round(sum(self.tp_distribution), 2) != 1.0:
            raise ValueError("TP distribution must sum to 1.0")

        self.daily_loss = 0.0
        self.last_trade_day = date.today()

        logger.info("RiskManager initialized")

    # ------------------------------------------------------------------ #
    # DAILY LOSS HANDLING
    # ------------------------------------------------------------------ #

    def _reset_daily_loss_if_new_day(self):
        today = date.today()
        if today != self.last_trade_day:
            logger.info("New trading day detected — resetting daily loss")
            self.daily_loss = 0.0
            self.last_trade_day = today

    def record_loss(self, loss_amount: float):
        """Call this after a losing trade closes"""
        self._reset_daily_loss_if_new_day()
        self.daily_loss += abs(loss_amount)
        logger.warning(f"Daily loss updated: {self.daily_loss:.2f}")

    def is_daily_loss_limit_reached(self) -> bool:
        self._reset_daily_loss_if_new_day()

        max_loss_amount = self.account_balance * (self.max_daily_loss / 100)
        return self.daily_loss >= max_loss_amount

    # ------------------------------------------------------------------ #
    # LOT SIZE CALCULATION
    # ------------------------------------------------------------------ #

    def calculate_lot_size(
        self,
        entry_price: float,
        stop_loss: float,
        pip_value: float
    ) -> float:
        """
        Calculate lot size using risk model
        """

        if self.fixed_lot:
            logger.info(f"Using fixed lot size: {self.fixed_lot}")
            return self.fixed_lot

        risk_amount = self.account_balance * (self.risk_per_trade / 100)
        sl_distance = abs(entry_price - stop_loss)

        if sl_distance == 0:
            raise ValueError("Stop loss distance cannot be zero")

        lot = risk_amount / (sl_distance * pip_value)

        lot = round(lot, 2)
        logger.info(f"Calculated lot size: {lot}")

        return max(lot, 0.01)

    # ------------------------------------------------------------------ #
    # TRADE VALIDATION
    # ------------------------------------------------------------------ #

    def can_open_trade(self, open_trades_count: int) -> bool:
        """
        Check whether a new trade is allowed
        """

        if open_trades_count >= self.max_open_trades:
            logger.warning("Max open trades limit reached")
            return False

        if self.is_daily_loss_limit_reached():
            logger.warning("Daily loss limit reached — trading disabled")
            return False

        return True

    # ------------------------------------------------------------------ #
    # TP HANDLING
    # ------------------------------------------------------------------ #

    def split_lot_across_tps(self, total_lot: float) -> List[float]:
        """
        Split volume across multiple TPs
        """

        lots = []
        for portion in self.tp_distribution:
            lots.append(round(total_lot * portion, 2))

        # Fix rounding issues
        difference = total_lot - sum(lots)
        lots[0] += difference

        logger.info(f"Lot split across TPs: {lots}")
        return lots

    # ------------------------------------------------------------------ #
    # SIGNAL VALIDATION
    # ------------------------------------------------------------------ #

    def validate_signal(self, signal: Dict) -> bool:
        """
        Ensure required fields exist
        """

        required_fields = ["symbol", "direction", "entry", "sl", "tps"]

        for field in required_fields:
            if field not in signal or signal[field] is None:
                logger.error(f"Invalid signal — missing field: {field}")
                return False

        if len(signal["tps"]) == 0:
            logger.error("Signal has no take-profit targets")
            return False

        return True
