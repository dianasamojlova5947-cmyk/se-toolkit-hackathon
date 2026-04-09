"""
Menu service module.
Handles menu-related operations including CRUD for dishes.
"""

import json
import os
from typing import Dict, List, Optional, Any
import logging

from services.database import Database
from config import DAY_ORDER, MENU_FILE

logger = logging.getLogger("matrix_bot")


class MenuService:
    """Service for managing menu data."""

    def __init__(self, db: Database, use_database: bool = True):
        """
        Initialize menu service.

        Args:
            db: Database instance
            use_database: If True, use SQLite; if False, use JSON files
        """
        self.db = db
        self.use_database = use_database
        self.menu_file = MENU_FILE

    async def get_day_menu(self, day_key: str) -> List[Dict[str, Any]]:
        """
        Get all dishes for a specific day.

        Args:
            day_key: Day key (monday, tuesday, etc.)

        Returns:
            List of dishes
        """
        if self.use_database:
            dishes = await self.db.get_menu_by_day(day_key)
            # Convert to simplified format
            return [
                {
                    "id": dish["id"],
                    "name": dish["name"],
                    "price": dish["price"],
                    "ingredients": dish["ingredients"],
                    "weight": dish.get("weight")
                }
                for dish in dishes
            ]
        else:
            return self._get_day_menu_json(day_key)

    async def get_fasting_menu(self) -> List[Dict[str, Any]]:
        """
        Get all fasting dishes.

        Returns:
            List of fasting dishes
        """
        if self.use_database:
            dishes = await self.db.get_fasting_menu()
            return [
                {
                    "id": dish["id"],
                    "name": dish["name"],
                    "price": dish["price"],
                    "ingredients": dish["ingredients"],
                    "weight": dish.get("weight")
                }
                for dish in dishes
            ]
        else:
            return self._get_fasting_menu_json()

    async def get_full_menu(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get the complete menu organized by day.

        Returns:
            Dictionary with days as keys and dish lists as values
        """
        if self.use_database:
            return await self.db.get_full_menu()
        else:
            return self._get_full_menu_json()

    async def add_dish(
        self,
        day_key: str,
        name: str,
        price: str,
        ingredients: str,
        weight: Optional[str] = None,
        is_fasting: bool = False
    ) -> bool:
        """
        Add a new dish to the menu.

        Args:
            day_key: Day key (monday, etc.) or empty for fasting
            name: Dish name
            price: Dish price
            ingredients: Dish ingredients
            weight: Optional dish weight
            is_fasting: Whether dish is for fasting menu

        Returns:
            True if successful, False otherwise
        """
        if self.use_database:
            dish_id = await self.db.add_dish(
                day_key, name, price, ingredients, weight, is_fasting
            )
            return dish_id > 0
        else:
            return self._add_dish_json(
                day_key, name, price, ingredients, weight, is_fasting
            )

    async def update_dish(
        self,
        dish_id: int,
        name: Optional[str] = None,
        price: Optional[str] = None,
        ingredients: Optional[str] = None,
        weight: Optional[str] = None
    ) -> bool:
        """
        Update an existing dish.

        Args:
            dish_id: Dish ID
            name: New name (optional)
            price: New price (optional)
            ingredients: New ingredients (optional)
            weight: New weight (optional)

        Returns:
            True if successful
        """
        if self.use_database:
            return await self.db.update_dish(dish_id, name, price, ingredients, weight)
        else:
            return self._update_dish_json(dish_id, name, price, ingredients, weight)

    async def delete_dish(self, dish_id: int, day_key: Optional[str] = None) -> bool:
        """
        Delete a dish from the menu.

        Args:
            dish_id: Dish ID
            day_key: Day key (for JSON mode)

        Returns:
            True if successful
        """
        if self.use_database:
            return await self.db.delete_dish(dish_id)
        else:
            return self._delete_dish_json(dish_id, day_key)

    async def get_dish_by_id(self, dish_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific dish by ID.

        Args:
            dish_id: Dish ID

        Returns:
            Dish dictionary or None
        """
        if self.use_database:
            return await self.db.get_dish_by_id(dish_id)
        else:
            # For JSON, dish_id is not reliable; return None
            return None

    # JSON file operations (fallback)
    def _load_menu_json(self) -> Dict:
        """Load menu from JSON file."""
        try:
            if os.path.exists(self.menu_file):
                with open(self.menu_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading menu.json: {e}")
        return {}

    def _save_menu_json(self, menu: Dict) -> bool:
        """Save menu to JSON file."""
        try:
            with open(self.menu_file, "w", encoding="utf-8") as f:
                json.dump(menu, f, ensure_ascii=False, indent=2)
            logger.info("Menu saved to JSON file")
            return True
        except IOError as e:
            logger.error(f"Error saving menu.json: {e}")
            return False

    def _get_day_menu_json(self, day_key: str) -> List[Dict]:
        """Get day menu from JSON."""
        menu = self._load_menu_json()
        return menu.get(day_key, [])

    def _get_fasting_menu_json(self) -> List[Dict]:
        """Get fasting menu from JSON."""
        menu = self._load_menu_json()
        return menu.get("fasting_menu", [])

    def _get_full_menu_json(self) -> Dict[str, List[Dict]]:
        """Get full menu from JSON."""
        return self._load_menu_json()

    def _add_dish_json(
        self,
        day_key: str,
        name: str,
        price: str,
        ingredients: str,
        weight: Optional[str] = None,
        is_fasting: bool = False
    ) -> bool:
        """Add dish to JSON file."""
        menu = self._load_menu_json()

        dish = {
            "name": name,
            "price": price,
            "ingredients": ingredients
        }
        if weight:
            dish["weight"] = weight

        if is_fasting:
            if "fasting_menu" not in menu:
                menu["fasting_menu"] = []
            menu["fasting_menu"].append(dish)
        else:
            if day_key not in menu:
                menu[day_key] = []
            menu[day_key].append(dish)

        return self._save_menu_json(menu)

    def _update_dish_json(
        self,
        dish_index: int,
        name: Optional[str] = None,
        price: Optional[str] = None,
        ingredients: Optional[str] = None,
        weight: Optional[str] = None,
        day_key: Optional[str] = None,
        is_fasting: bool = False
    ) -> bool:
        """Update dish in JSON file."""
        menu = self._load_menu_json()

        if is_fasting:
            dishes = menu.get("fasting_menu", [])
        else:
            dishes = menu.get(day_key, [])

        if dish_index < 0 or dish_index >= len(dishes):
            return False

        dish = dishes[dish_index]
        if name:
            dish["name"] = name
        if price:
            dish["price"] = price
        if ingredients:
            dish["ingredients"] = ingredients
        if weight is not None:
            dish["weight"] = weight

        return self._save_menu_json(menu)

    def _delete_dish_json(
        self,
        dish_index: int,
        day_key: Optional[str] = None,
        is_fasting: bool = False
    ) -> bool:
        """Delete dish from JSON file."""
        menu = self._load_menu_json()

        if is_fasting:
            if "fasting_menu" in menu and 0 <= dish_index < len(menu["fasting_menu"]):
                menu["fasting_menu"].pop(dish_index)
                return self._save_menu_json(menu)
        else:
            if day_key and day_key in menu and 0 <= dish_index < len(menu[day_key]):
                menu[day_key].pop(dish_index)
                return self._save_menu_json(menu)

        return False