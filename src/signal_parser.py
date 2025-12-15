import re
import json

class SignalParser:
    def __init__(self):
        self.patterns = {
            # Regex to find the anchor phrase, handling emojis/spaces around it
            'anchor': r'(?i)SIGNAL\s+ALERT',
            
            # Action, TP, SL patterns remain the same
            'action': r'(?i)\b(SELL|BUY|SELL LIMIT|BUY LIMIT|SELL STOP|BUY STOP)\b',
            'sl': r'(?i)(?:SL|Stop Loss)\s*[:=]?\s*(\d+[\.,]?\d*)',
            'tp': r'(?i)(?:TP|Take Profit)\s*(?:\d+)?\s*[:=]\s*(\d+[\.,]?\d*)'
        }

    def parse(self, text):
        # 1. Clean Emojis and normalization
        # This removes non-ASCII characters (emojis) to make text processing safer
        clean_text = text.encode('ascii', 'ignore').decode('ascii')
        clean_text = clean_text.replace('\n', ' ').strip()
        
        # 2. Locate the Anchor "SIGNAL ALERT"
        anchor_search = re.search(self.patterns['anchor'], clean_text)
        
        symbol = None
        
        if anchor_search:
            # Slice the text: start looking ONLY AFTER "SIGNAL ALERT"
            # .end() gives the index where "SIGNAL ALERT" finishes
            post_alert_text = clean_text[anchor_search.end():]
            
            # Find the first word that looks like a Symbol (3-6 chars) followed by a colon or space
            # We look for A-Z letters, 3 to 6 chars long
            symbol_match = re.search(r'\b([A-Z0-9]{3,6})\b', post_alert_text)
            
            if symbol_match:
                symbol = symbol_match.group(1).upper()
        
        # Fallback: If no anchor found, try to find a word followed strictly by a colon (e.g. "NZDUSD:")
        if not symbol:
             symbol_match = re.search(r'\b([A-Z0-9]{3,6})\s*:', clean_text)
             if symbol_match:
                 symbol = symbol_match.group(1).upper()

        # 3. Extract Action
        action_match = re.search(self.patterns['action'], clean_text)
        action = action_match.group(1).upper() if action_match else None

        # 4. Extract SL and TP
        sl_match = re.search(self.patterns['sl'], clean_text)
        sl = float(sl_match.group(1).replace(',', '.')) if sl_match else None

        tp_matches = re.findall(self.patterns['tp'], clean_text)
        tps = [float(tp.replace(',', '.')) for tp in tp_matches]

        return {
            "symbol": symbol,
            "action": action,
            "entry_type": "MARKET_EXECUTION" if "NOW" in clean_text.upper() else "PENDING",
            "stop_loss": sl,
            "take_profit_1": tps[0] if len(tps) > 0 else None,
            "take_profit_2": tps[1] if len(tps) > 1 else None,
            "take_profit_3": tps[2] if len(tps) > 2 else None,
            "raw_tps": tps,
            "notes": "Low Lot" if "LOW LOT" in clean_text.upper() else ""
        }

