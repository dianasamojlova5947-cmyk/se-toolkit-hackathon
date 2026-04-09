"""
Database module for SQLite operations.
Provides async database access with aiosqlite.
"""

import asyncio
import aiosqlite
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

from config import DATABASE_FILE

logger = logging.getLogger("matrix_bot")


class Database:
    """SQLite database manager for Matrix Bot."""

    _instance: Optional["Database"] = None
    _db: Optional[aiosqlite.Connection] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self) -> None:
        """Establish database connection and create tables."""
        self._db = await aiosqlite.connect(DATABASE_FILE)
        self._db.row_factory = aiosqlite.Row
        await self._create_tables()
        logger.info(f"Database connected: {DATABASE_FILE}")

    async def close(self) -> None:
        """Close database connection."""
        if self._db:
            await self._db.close()
            logger.info("Database connection closed")

    async def _create_tables(self) -> None:
        """Create necessary tables if they don't exist."""
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'ru',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS dishes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day_key TEXT,
                name TEXT NOT NULL,
                price TEXT NOT NULL,
                ingredients TEXT,
                weight TEXT,
                is_fasting INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await self._db.commit()
        logger.debug("Database tables created/verified")

    # User operations
    async def get_user_language(self, user_id: int) -> str:
        """Get user's preferred language."""
        async with self._db.execute(
            "SELECT language FROM users WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row["language"] if row else "ru"

    async def set_user_language(self, user_id: int, language: str) -> None:
        """Set user's preferred language."""
        await self._db.execute("""
            INSERT INTO users (user_id, language, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                language = excluded.language,
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, language))
        await self._db.commit()
        logger.debug(f"User {user_id} language set to {language}")

    # Dish operations
    async def get_menu_by_day(self, day_key: str) -> List[Dict[str, Any]]:
        """Get all dishes for a specific day."""
        async with self._db.execute(
            "SELECT * FROM dishes WHERE day_key = ? AND is_fasting = 0 ORDER BY id",
            (day_key,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_fasting_menu(self) -> List[Dict[str, Any]]:
        """Get all fasting dishes."""
        async with self._db.execute(
            "SELECT * FROM dishes WHERE is_fasting = 1 ORDER BY id"
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_full_menu(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get the complete menu organized by day."""
        menu = {}

        # Get regular menu
        async with self._db.execute(
            "SELECT * FROM dishes WHERE is_fasting = 0 ORDER BY day_key, id"
        ) as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                day = row["day_key"]
                if day not in menu:
                    menu[day] = []
                menu[day].append(dict(row))

        # Get fasting menu
        menu["fasting_menu"] = await self.get_fasting_menu()

        return menu

    async def add_dish(
        self,
        day_key: str,
        name: str,
        price: str,
        ingredients: str,
        weight: Optional[str] = None,
        is_fasting: bool = False
    ) -> int:
        """Add a new dish to the menu."""
        cursor = await self._db.execute("""
            INSERT INTO dishes (day_key, name, price, ingredients, weight, is_fasting)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (day_key, name, price, ingredients, weight, 1 if is_fasting else 0))
        await self._db.commit()
        dish_id = cursor.lastrowid
        logger.info(f"Dish added: {name} (id={dish_id})")
        return dish_id

    async def update_dish(
        self,
        dish_id: int,
        name: Optional[str] = None,
        price: Optional[str] = None,
        ingredients: Optional[str] = None,
        weight: Optional[str] = None
    ) -> bool:
        """Update an existing dish."""
        updates = []
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if price is not None:
            updates.append("price = ?")
            params.append(price)
        if ingredients is not None:
            updates.append("ingredients = ?")
            params.append(ingredients)
        if weight is not None:
            updates.append("weight = ?")
            params.append(weight)

        if not updates:
            return False

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(dish_id)

        await self._db.execute(
            f"UPDATE dishes SET {', '.join(updates)} WHERE id = ?",
            params
        )
        await self._db.commit()
        logger.info(f"Dish updated: id={dish_id}")
        return True

    async def delete_dish(self, dish_id: int) -> bool:
        """Delete a dish from the menu."""
        cursor = await self._db.execute(
            "DELETE FROM dishes WHERE id = ?", (dish_id,)
        )
        await self._db.commit()
        deleted = cursor.rowcount > 0
        if deleted:
            logger.info(f"Dish deleted: id={dish_id}")
        return deleted

    async def get_dish_by_id(self, dish_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific dish by ID."""
        async with self._db.execute(
            "SELECT * FROM dishes WHERE id = ?", (dish_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def clear_day_menu(self, day_key: str) -> int:
        """Clear all dishes for a specific day."""
        cursor = await self._db.execute(
            "DELETE FROM dishes WHERE day_key = ?", (day_key,)
        )
        await self._db.commit()
        count = cursor.rowcount
        logger.info(f"Cleared {count} dishes from {day_key}")
        return count

    # Migration from JSON
    async def import_from_json(self, menu_data: Dict) -> None:
        """Import menu data from JSON format."""
        for day_key, dishes in menu_data.items():
            if day_key == "fasting_menu":
                for dish in dishes:
                    await self.add_dish(
                        day_key="",
                        name=dish.get("name", ""),
                        price=dish.get("price", ""),
                        ingredients=dish.get("ingredients", ""),
                        weight=dish.get("weight"),
                        is_fasting=True
                    )
            else:
                for dish in dishes:
                    await self.add_dish(
                        day_key=day_key,
                        name=dish.get("name", ""),
                        price=dish.get("price", ""),
                        ingredients=dish.get("ingredients", ""),
                        weight=dish.get("weight"),
                        is_fasting=False
                    )
        logger.info("Menu imported from JSON")


# Global database instance
db = Database()