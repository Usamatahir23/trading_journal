"""
Database service for MongoDB integration
"""
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

try:
    from dotenv import load_dotenv
    # Load .env file from project root (go up 2 levels: trading_journal -> src -> root)
    env_path = Path(__file__).parent.parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass

from .models import Trade


class DatabaseService:
    """Service for MongoDB database operations"""
    
    def __init__(self, connection_string: Optional[str] = None, 
                 database_name: Optional[str] = None):
        """
        Initialize database service
        
        Args:
            connection_string: MongoDB connection string. If None, checks:
                1. MONGODB_URI from .env file or environment variable
                2. Defaults to mongodb://localhost:27017/
            database_name: Database name. If None, checks:
                1. MONGODB_DATABASE from .env file or environment variable
                2. Defaults to trading_journal
        """
        if connection_string is None:
            # Check .env file (loaded via dotenv) or environment variable, then default to localhost
            connection_string = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        
        if database_name is None:
            # Check .env file or environment variable, then default
            database_name = os.getenv("MONGODB_DATABASE", "trading_journal")
        
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None
        self.trades_collection = None
        self.summaries_collection = None
        self._connect()
    
    def reconnect(self, connection_string: str) -> bool:
        """
        Reconnect to MongoDB with a new connection string
        
        Args:
            connection_string: New MongoDB connection string
            
        Returns:
            True if connection successful, False otherwise
        """
        # Close existing connection
        self.close()
        
        # Update connection string
        self.connection_string = connection_string
        
        # Try to connect
        self._connect()
        return self.is_connected()
    
    def _connect(self):
        """Connect to MongoDB"""
        try:
            # Increase timeout for Atlas connections
            timeout_ms = 10000 if "mongodb+srv://" in self.connection_string else 2000
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=timeout_ms)
            # Test connection
            self.client.server_info()
            self.db = self.client[self.database_name]
            self.trades_collection = self.db["trades"]
            self.summaries_collection = self.db["summaries"]
            print(f"Connected to MongoDB successfully: {self.connection_string[:50]}...")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"Warning: Could not connect to MongoDB: {e}")
            print(f"Connection string: {self.connection_string[:50]}...")
            print("Running in offline mode - data will not be persisted")
            self.client = None
            self.db = None
            self.trades_collection = None
            self.summaries_collection = None
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
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
