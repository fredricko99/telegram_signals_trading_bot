import re
import json

class SignalParser:
    '''Parses the telegram text message and extracts the necessary information
        '''
    
    
    def __init__(self):
        self.patterns = {
            # Regex to find the anchor phrase, handling emojis/spaces around it
            'anchor': r'(?i)SIGNAL\s+ALERT',
            
            # Action: Captures the type (e.g., 'SELL', 'BUY LIMIT')
            'action': r'(?i)\b(SELL|BUY|SELL LIMIT|BUY LIMIT|SELL STOP|BUY STOP)\b',
            
            # Price: Captures the number immediately following an action (used for pending orders)
            # Example: SELL LIMIT 1.2345
            'entry_price': r'(?i)(?:SELL\s+LIMIT|BUY\s+LIMIT|SELL\s+STOP|BUY\s+STOP)\s*(\d+[\.,]?\d*)',
            
            'sl': r'(?i)(?:SL|Stop Loss)\s*[:=]?\s*(\d+[\.,]?\d*)',
            'tp': r'(?i)(?:TP|Take Profit)\s*(?:\d+)?\s*[:=]\s*(\d+[\.,]?\d*)'
        }

    def parse(self, text:str) ->object:
        '''Parsed in a string from the text message returns an Object
            containing data from the parsed text'''
        
        # 1. Clean Emojis and normalization
        clean_text = text.encode('ascii', 'ignore').decode('ascii')
        clean_text = clean_text.replace('\n', ' ').strip()
        
        # 2. Locate the Anchor "SIGNAL ALERT" and extract Symbol (remains the same)
        anchor_search = re.search(self.patterns['anchor'], clean_text)
        symbol = None
        
        if anchor_search:
            post_alert_text = clean_text[anchor_search.end():]
            symbol_match = re.search(r'\b([A-Z0-9]{3,6})\b', post_alert_text)
            if symbol_match:
                symbol = symbol_match.group(1).upper()
        
        # Fallback for symbol
        if not symbol:
            symbol_match = re.search(r'\b([A-Z0-9]{3,6})\s*:', clean_text)
            if symbol_match:
                symbol = symbol_match.group(1).upper()

        # 3. Extract Action
        action_match = re.search(self.patterns['action'], clean_text)
        action = action_match.group(1).upper() if action_match else None

        # 4. Determine Entry Type and Price
        entry_type = "MARKET_EXECUTION" if "NOW" in clean_text.upper() else "PENDING"
        entry_price = None

        if entry_type == "PENDING":
            price_match = re.search(self.patterns['entry_price'], clean_text)
            if price_match:
                 # Convert and clean the pending entry price
                 entry_price = float(price_match.group(1).replace(',', '.'))

        # 5. Extract SL and TP
        sl_match = re.search(self.patterns['sl'], clean_text)
        sl = float(sl_match.group(1).replace(',', '.')) if sl_match else None

        tp_matches = re.findall(self.patterns['tp'], clean_text)
        tps = [float(tp.replace(',', '.')) for tp in tp_matches]

        return {
            "symbol": symbol,
            "action": action,
            "entry_type": entry_type,
            "entry_price": entry_price,
            "stop_loss": sl,
            "take_profit_1": tps[0] if len(tps) > 0 else None,
            "take_profit_2": tps[1] if len(tps) > 1 else None,
            "take_profit_3": tps[2] if len(tps) > 2 else None,
            "raw_tps": tps,
            "notes": "Low Lot" if "LOW LOT" in clean_text.upper() else ""
        }