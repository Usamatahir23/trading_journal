"""
Tests for TradeCalculator
"""
import unittest
from src.trading_journal.calculator import TradeCalculator


class TestTradeCalculator(unittest.TestCase):
    """Test cases for TradeCalculator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.calculator = TradeCalculator(pip_value=0.1, pip_value_usd=1.0)
    
    def test_calculate_take_profit_long(self):
        """Test take profit calculation for long position"""
        entry = 2000.50
        stop_loss = 1995.00
        multiplier = 2.0
        
        tp = self.calculator.calculate_take_profit(entry, stop_loss, multiplier)
        expected = 2000.50 + (2000.50 - 1995.00) * 2.0
        self.assertEqual(tp, round(expected, 2))
    
    def test_calculate_take_profit_short(self):
        """Test take profit calculation for short position"""
        entry = 2000.50
        stop_loss = 2005.00
        multiplier = 2.0
        
        tp = self.calculator.calculate_take_profit(entry, stop_loss, multiplier)
        expected = 2000.50 - (2005.00 - 2000.50) * 2.0
        self.assertEqual(tp, round(expected, 2))
    
    def test_calculate_lot_size(self):
        """Test lot size calculation"""
        account_balance = 10000.0
        risk_percent = 1.0
        entry = 2000.50
        stop_loss = 1995.00
        
        lot_size = self.calculator.calculate_lot_size(account_balance, risk_percent, entry, stop_loss)
        self.assertGreater(lot_size, 0)
    
    def test_calculate_amount_at_risk(self):
        """Test amount at risk calculation"""
        account_balance = 10000.0
        risk_percent = 1.0
        
        amount = self.calculator.calculate_amount_at_risk(account_balance, risk_percent)
        self.assertEqual(amount, 100.0)
    
    def test_calculate_pips_long(self):
        """Test pips calculation for long position"""
        entry = 2000.50
        exit_price = 2010.00
        is_long = True
        
        pips = self.calculator.calculate_pips(entry, exit_price, is_long)
        expected = (2010.00 - 2000.50) / 0.1
        self.assertEqual(pips, round(expected, 2))
    
    def test_calculate_usd_pl(self):
        """Test USD P/L calculation"""
        pips = 50.0
        lot_size = 1.0
        
        usd_pl = self.calculator.calculate_usd_pl(pips, lot_size)
        self.assertEqual(usd_pl, 50.0)
    
    def test_calculate_return_ratio(self):
        """Test return ratio calculation"""
        usd_pl = 200.0
        amount_at_risk = 100.0
        
        ratio = self.calculator.calculate_return_ratio(usd_pl, amount_at_risk)
        self.assertEqual(ratio, 2.0)


if __name__ == "__main__":
    unittest.main()
