"""
Shared configuration, constants, and utilities for the Telegram bot
"""

import os
import logging
from dotenv import load_dotenv
from database import Database

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]
SESSION_FILES_DIR = os.getenv("SESSION_FILES_DIR", "session_files")
ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", "5"))

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    handlers=[
        logging.FileHandler(os.getenv("LOG_FILE", "bot.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize database
db = Database(os.getenv("DATABASE_URL", "bot_database.db").replace("sqlite:///", ""))

# Conversation states
(WAITING_COUNTRY_NAME, WAITING_COUNTRY_CODE, WAITING_PHONE_CODE, WAITING_PRICE,
 WAITING_STOCK, WAITING_DESCRIPTION, WAITING_FILE, WAITING_PRODUCT_EDIT,
 WAITING_BALANCE_AMOUNT, WAITING_USER_ID, WAITING_BROADCAST_MESSAGE) = range(11)

# Country flag emojis mapping
COUNTRY_FLAGS = {
    "US": "🇺🇸", "UK": "🇬🇧", "CA": "🇨🇦", "AU": "🇦🇺", "DE": "🇩🇪",
    "FR": "🇫🇷", "ES": "🇪🇸", "IT": "🇮🇹", "BR": "🇧🇷", "IN": "🇮🇳",
    "CN": "🇨🇳", "JP": "🇯🇵", "KR": "🇰🇷", "RU": "🇷🇺", "MX": "🇲🇽",
    "NL": "🇳🇱", "SE": "🇸🇪", "NO": "🇳🇴", "FI": "🇫🇮", "DK": "🇩🇰",
    "PL": "🇵🇱", "TR": "🇹🇷", "SA": "🇸🇦", "AE": "🇦🇪", "SG": "🇸🇬",
}


def get_country_flag(country_code: str) -> str:
    """Get flag emoji for country code"""
    return COUNTRY_FLAGS.get(country_code.upper(), "🌍")


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in ADMIN_IDS
