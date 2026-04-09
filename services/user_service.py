"""
User service module.
Handles user-related operations including language preferences.
"""

import json
import os
from typing import Optional
import logging

from services.database import Database

logger = logging.getLogger("matrix_bot")


class UserService:
    """Service for managing user preferences."""

    def __init__(self, db: Database, use_database: bool = True):
        """
        Initialize user service.

        Args:
            db: Database instance
            use_database: If True, use SQLite; if False, use JSON files
        """
        self.db = db
        self.use_database = use_database
        self.users_file = "users.json"

    async def get_language(self, user_id: int) -> str:
        """
        Get user's preferred language.

        Args:
            user_id: Telegram user ID

        Returns:
            Language code ('ru' or 'en')
        """
        if self.use_database:
            return await self.db.get_user_language(user_id)
        else:
            return self._get_language_json(user_id)

    async def set_language(self, user_id: int, language: str) -> None:
        """
        Set user's preferred language.

        Args:
            user_id: Telegram user ID
            language: Language code ('ru' or 'en')
        """
        if self.use_database:
            await self.db.set_user_language(user_id, language)
        else:
            self._set_language_json(user_id, language)

    def _get_language_json(self, user_id: int) -> str:
        """Get language from JSON file."""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, "r", encoding="utf-8") as f:
                    users = json.load(f)
                    return users.get(str(user_id), {}).get("language", "ru")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading users.json: {e}")
        return "ru"

    def _set_language_json(self, user_id: int, language: str) -> None:
        """Save language to JSON file."""
        try:
            users = {}
            if os.path.exists(self.users_file):
                with open(self.users_file, "r", encoding="utf-8") as f:
                    users = json.load(f)

            users[str(user_id)] = {"language": language}

            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump(users, f, ensure_ascii=False, indent=2)

            logger.debug(f"Language for user {user_id} saved to JSON: {language}")
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error saving to users.json: {e}")