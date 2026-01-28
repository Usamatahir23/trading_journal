"""
Data models for trading journal
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Trade:
    """Trade data model"""
    date: str
    strategy: str
    entry: float
    tp: float
    sl: float
    multiplier: float
    lot_size: float
    risk_percent: float
    risk_amount: float
    exit_reason: str  # "TP" or "SL"
    actual_exit: float
    pips: float
    usd_pl: float
    status: str  # "Win" or "Loss"
    return_ratio: float
    achieved_multiplier: float
    scenario: str = "Strong"   # "Low", "Medium", "Strong"
    comment: str = ""
    
    def to_dict(self) -> dict:
        """Convert trade to dictionary"""
        return {
            "date": self.date,
            "strategy": self.strategy,
            "entry": self.entry,
            "tp": self.tp,
            "sl": self.sl,
            "multiplier": self.multiplier,
            "lot_size": self.lot_size,
            "risk_percent": self.risk_percent,
            "risk_amount": self.risk_amount,
            "exit_reason": self.exit_reason,
            "actual_exit": self.actual_exit,
            "pips": self.pips,
            "usd_pl": self.usd_pl,
            "status": self.status,
            "return_ratio": self.return_ratio,
            "achieved_multiplier": self.achieved_multiplier,
            "scenario": self.scenario,
            "comment": self.comment,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Trade':
        """Create trade from dictionary (supports legacy docs without scenario/comment)"""
        data = dict(data)
        data.setdefault("scenario", "Strong")
        data.setdefault("comment", "")
        return cls(**data)


@dataclass
class TradeCalculation:
    """Trade calculation results"""
    take_profit: float
    lot_size: float
    amount_at_risk: float
    sl_distance_pips: float
    is_long: bool
