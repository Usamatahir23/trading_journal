"""
Database service for MongoDB integration
"""
from typing import List, Optional
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from .models import Trade


class DatabaseService:
    """Service for MongoDB database operations"""
    
    def __init__(self, connection_string: str = "mongodb://localhost:27017/", 
                 database_name: str = "trading_journal"):
        """
        Initialize database service
        
        Args:
            connection_string: MongoDB connection string (default: localhost:27017)
            database_name: Database name
        """
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None
        self.trades_collection = None
        self.summaries_collection = None
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=2000)
            # Test connection
            self.client.server_info()
            self.db = self.client[self.database_name]
            self.trades_collection = self.db["trades"]
            self.summaries_collection = self.db["summaries"]
            print("Connected to MongoDB successfully")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"Warning: Could not connect to MongoDB: {e}")
            print("Running in offline mode - data will not be persisted")
            self.client = None
            self.db = None
            self.trades_collection = None
            self.summaries_collection = None
    
    def is_connected(self) -> bool:
        """Check if connected to MongoDB"""
        return self.client is not None
    
    def save_trade(self, trade: Trade) -> bool:
        """
        Save a trade to database
        
        Args:
            trade: Trade object to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        if not self.is_connected():
            return False
        
        try:
            trade_dict = trade.to_dict()
            result = self.trades_collection.insert_one(trade_dict)
            return result.inserted_id is not None
        except Exception as e:
            print(f"Error saving trade: {e}")
            return False
    
    def load_trades(self) -> List[Trade]:
        """
        Load all trades from database
        
        Returns:
            List of Trade objects
        """
        if not self.is_connected():
            return []
        
        try:
            trades_data = self.trades_collection.find().sort("date", -1)
            trades = []
            for trade_dict in trades_data:
                # Remove MongoDB _id field
                trade_dict.pop("_id", None)
                try:
                    trade = Trade.from_dict(trade_dict)
                    trades.append(trade)
                except Exception as e:
                    print(f"Error loading trade: {e}")
                    continue
            return trades
        except Exception as e:
            print(f"Error loading trades: {e}")
            return []
    
    def delete_trade(self, trade_date: str) -> bool:
        """
        Delete a trade from database
        
        Args:
            trade_date: Date string of the trade to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        if not self.is_connected():
            return False
        
        try:
            result = self.trades_collection.delete_one({"date": trade_date})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting trade: {e}")
            return False
    
    def save_summary(self, summary_data: dict) -> bool:
        """
        Save summary statistics to database
        
        Args:
            summary_data: Dictionary containing summary statistics
            
        Returns:
            True if saved successfully, False otherwise
        """
        if not self.is_connected():
            return False
        
        try:
            summary_data["timestamp"] = datetime.now().isoformat()
            summary_data["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result = self.summaries_collection.insert_one(summary_data)
            return result.inserted_id is not None
        except Exception as e:
            print(f"Error saving summary: {e}")
            return False
    
    def get_latest_summary(self) -> Optional[dict]:
        """
        Get the latest summary from database
        
        Returns:
            Latest summary dictionary or None
        """
        if not self.is_connected():
            return None
        
        try:
            summary = self.summaries_collection.find_one(sort=[("timestamp", -1)])
            if summary:
                summary.pop("_id", None)
            return summary
        except Exception as e:
            print(f"Error getting latest summary: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
