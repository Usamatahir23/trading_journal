"""
Calculation functions for trading journal
"""


class TradeCalculator:
    """Calculator for trade position sizing and profit/loss"""
    
    def __init__(self, pip_value: float = 0.1, pip_value_usd: float = 1.0):
        """
        Initialize calculator
        
        Args:
            pip_value: Pip value for the instrument (default 0.1 for gold)
            pip_value_usd: USD value per pip per lot (default $1 for gold)
        """
        self.pip_value = pip_value
        self.pip_value_usd = pip_value_usd
    
    def calculate_take_profit(self, entry: float, stop_loss: float, multiplier: float) -> float:
        """
        Calculate take profit based on entry, stop loss, and multiplier
        
        Args:
            entry: Entry price
            stop_loss: Stop loss price
            multiplier: Risk:Reward multiplier
            
        Returns:
            Take profit price
        """
        is_long = entry > stop_loss
        
        if is_long:
            tp_distance = (entry - stop_loss) * multiplier
            take_profit = entry + tp_distance
        else:
            tp_distance = (stop_loss - entry) * multiplier
            take_profit = entry - tp_distance
        
        return round(take_profit, 2)
    
    def calculate_lot_size(self, account_balance: float, risk_percent: float, 
                         entry: float, stop_loss: float) -> float:
        """
        Calculate lot size based on risk percentage and stop loss distance
        
        Args:
            account_balance: Account balance
            risk_percent: Risk percentage (e.g., 1.0 for 1%)
            entry: Entry price
            stop_loss: Stop loss price
            
        Returns:
            Lot size
        """
        # Determine if long or short
        is_long = entry > stop_loss
        
        # Calculate SL distance in pips
        if is_long:
            sl_distance_pips = (entry - stop_loss) / self.pip_value
        else:
            sl_distance_pips = (stop_loss - entry) / self.pip_value
        
        if sl_distance_pips <= 0:
            raise ValueError("Invalid entry/stop loss relationship")
        
        # Calculate amount at risk
        amount_at_risk = account_balance * (risk_percent / 100)
        
        # Calculate lot size
        # Risk amount = SL distance (pips) * pip_value_usd * lot_size
        # lot_size = Risk amount / (SL distance * pip_value_usd)
        lot_size = amount_at_risk / (sl_distance_pips * self.pip_value_usd)
        
        return round(lot_size, 3)
    
    def calculate_amount_at_risk(self, account_balance: float, risk_percent: float) -> float:
        """
        Calculate amount at risk
        
        Args:
            account_balance: Account balance
            risk_percent: Risk percentage
            
        Returns:
            Amount at risk in USD
        """
        return round(account_balance * (risk_percent / 100), 2)
    
    def calculate_pips(self, entry: float, exit_price: float, is_long: bool) -> float:
        """
        Calculate pips difference between entry and exit
        
        Args:
            entry: Entry price
            exit_price: Exit price
            is_long: True if long position, False if short
            
        Returns:
            Pips difference
        """
        if is_long:
            diff = exit_price - entry
        else:
            diff = entry - exit_price
        
        pips = diff / self.pip_value
        return round(pips, 2)
    
    def calculate_usd_pl(self, pips: float, lot_size: float) -> float:
        """
        Calculate USD profit/loss
        
        Args:
            pips: Pips gained/lost
            lot_size: Lot size
            
        Returns:
            USD profit/loss
        """
        return round(pips * self.pip_value_usd * lot_size, 2)
    
    def calculate_return_ratio(self, usd_pl: float, amount_at_risk: float) -> float:
        """
        Calculate return ratio (actual return / risk)
        
        Args:
            usd_pl: USD profit/loss
            amount_at_risk: Amount at risk
            
        Returns:
            Return ratio (e.g., 2.0 means 2x return on risk)
        """
        if amount_at_risk > 0:
            return round(usd_pl / amount_at_risk, 2)
        return 0.0
