"""
Configuration module for Matrix Bot.
Handles environment variables and constants.
"""

import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID", "").strip()

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in .env file")

# File paths
MENU_FILE = "menu.json"
USERS_FILE = "users.json"
ADMINS_FILE = "admins.json"
DATABASE_FILE = "matrix_bot.db"

# Day order for weekly menu
DAY_ORDER = [
    "monday", "tuesday", "wednesday",
    "thursday", "friday", "saturday", "sunday"
]

# Day names for localization
DAY_NAMES = {
    "ru": {
        "monday": "Понедельник",
        "tuesday": "Вторник",
        "wednesday": "Среда",
        "thursday": "Четверг",
        "friday": "Пятница",
        "saturday": "Суббота",
        "sunday": "Воскресенье"
    },
    "en": {
        "monday": "Monday",
        "tuesday": "Tuesday",
        "wednesday": "Wednesday",
        "thursday": "Thursday",
        "friday": "Friday",
        "saturday": "Saturday",
        "sunday": "Sunday"
    }
}

# Logging configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.INFO

def is_admin(user_id: int | str) -> bool:
    """Check if user is admin."""
    user_id_str = str(user_id).strip()
    if ADMIN_ID and user_id_str == ADMIN_ID.strip():
        return True

    try:
        if os.path.exists(ADMINS_FILE):
            with open(ADMINS_FILE, "r", encoding="utf-8") as f:
                admins = json.load(f)
                if isinstance(admins, list):
                    return user_id_str in {str(item).strip() for item in admins}
    except (json.JSONDecodeError, IOError):
        return False

    return False
