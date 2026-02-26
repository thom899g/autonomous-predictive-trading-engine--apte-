"""
APTE Configuration Module
Centralizes all system configurations, environment variables, and constants.
Uses Pydantic for validation to prevent runtime configuration errors.
"""
import os
from typing import Dict, List, Optional
from enum import Enum
import logging
from pydantic import BaseSettings, Field, validator
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('apte.log')
    ]
)
logger = logging.getLogger(__name__)


class ExchangeType(str, Enum):
    BINANCE = "binance"
    COINBASE = "coinbase"
    KRAKEN = "kraken"


class TradingMode(str, Enum):
    PAPER = "paper"
    LIVE = "live"
    BACKTEST = "backtest"


class APTEConfig(BaseSettings):
    """Main configuration class with validation"""
    
    # Exchange Configuration
    EXCHANGE: ExchangeType = Field(default=ExchangeType.BINANCE)
    EXCHANGE_API_KEY: Optional[str] = Field(default=None, env="EXCHANGE_API_KEY")
    EXCHANGE_API_SECRET: Optional[str] = Field(default=None, env="EXCHANGE_API_SECRET")
    
    # Trading Parameters
    TRADING_MODE: TradingMode = Field(default=TradingMode.PAPER)
    INITIAL_CAPITAL: float = Field(default=10000.0, gt=0)
    MAX_POSITION_SIZE: float = Field(default=0.1, ge=0, le=1)  # 10% of capital
    MAX_DAILY_LOSS: float = Field(default=0.02, ge=0, le=0.1)  # 2% daily loss limit
    
    # Firebase Configuration (CRITICAL - as per mission constraints)
    FIREBASE_PROJECT_ID: str = Field(..., env="FIREBASE_PROJECT_ID")
    FIREBASE_CREDENTIALS_PATH: str = Field(..., env="FIREBASE_CREDENTIALS_PATH")
    FIRESTORE_COLLECTION: str = Field(default="apte_trading")
    
    # ML Model Configuration
    MODEL_UPDATE_INTERVAL_MINUTES: int = Field(default=60, gt=0)
    PREDICTION_CONFIDENCE_THRESHOLD: float = Field(default=0.65, ge=0.5, le=1.0)
    
    # Data Collection
    DATA_SYMBOLS: List[str] = Field(default=["BTC/USDT", "ETH/USDT", "SOL/USDT"])
    DATA_INTERVAL_MINUTES: int = Field(default=5, gt=0)
    LOOKBACK_PERIODS: int = Field(default=100)  # For feature engineering
    
    # Risk Management
    STOP_LOSS_PERCENT: float = Field(default=0.02, gt=0, le=0.1)
    TAKE_PROFIT_PERCENT: float = Field(default=0.04, gt=0, le=0.2)
    MAX_OPEN_POSITIONS: int = Field(default=3, gt=0)
    
    # System Control
    HEARTBEAT_INTERVAL_SECONDS: int = Field(default=30, gt=0)
    MAX_RETRIES: int = Field(default=3)
    RETRY_DELAY_SECONDS: int = Field(default=5)
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @validator("FIREBASE_CREDENTIALS_PATH")
    def validate_firebase_creds(cls, v):
        if not os.path.exists(v):
            logger.error(f"Firebase credentials file not found: {v}")
            raise FileNotFoundError(f"Firebase credentials file not found: {v}")
        return v
    
    @validator("EXCHANGE_API_KEY", "EXCHANGE_API_SECRET", always=True)
    def validate_exchange_credentials(cls, v, values):
        if values.get('TRADING_MODE') == TradingMode.LIVE and not v:
            logger.error("Live trading requires exchange API credentials")
            raise ValueError("Exchange API credentials required for live trading")
        return v


# Global configuration instance
config = APTEConfig()