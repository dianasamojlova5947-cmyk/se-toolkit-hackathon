"""
Inline keyboard builders for Matrix Bot.
Creates inline button layouts for various interactions.
"""

from typing import List, Dict, Any, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.user_service import UserService
from utils.i18n import get_text
from config import DAY_ORDER, DAY_NAMES


async def build_week_keyboard(
    user_id: int,
    user_service: UserService,
    back_callback: str = "back:main"
) -> InlineKeyboardMarkup:
    """
    Build inline keyboard for day selection.

    Args:
        user_id: Telegram user ID
        user_service: User service for language lookup

    Returns:
        InlineKeyboardMarkup with day buttons
    """
    lang = await user_service.get_language(user_id)
    day_names = DAY_NAMES.get(lang, DAY_NAMES["ru"])

    rows = []
    for day_key in DAY_ORDER:
        rows.append([
            InlineKeyboardButton(
                text=day_names[day_key],
                callback_data=f"show_day:{day_key}"
            )
        ])

    rows.append([
        InlineKeyboardButton(
            text=f"◀️ {get_text('back', lang)}",
            callback_data=back_callback
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


async def build_ingredients_keyboard(
    day_key: str,
    dishes: List[Dict[str, Any]],
    user_id: int,
    user_service: UserService,
    back_callback: Optional[str] = None,
    back_to: str = "week"
) -> Optional[InlineKeyboardMarkup]:
    """
    Build inline keyboard with ingredient buttons for dishes.

    Args:
        day_key: Day key (for callback data)
        dishes: List of dishes
        user_id: Telegram user ID
        user_service: User service for language lookup

    Returns:
        InlineKeyboardMarkup or None if no dishes
    """
    lang = await user_service.get_language(user_id)
    rows = []

    for index, dish in enumerate(dishes):
        rows.append([
            InlineKeyboardButton(
                text=f"🧾 {get_text('ingredients_btn', lang)}: {dish['name']}",
                callback_data=f"ingredients:{day_key}:{index}:{back_to}"
            )
        ])

    if back_callback:
        rows.append([
            InlineKeyboardButton(
                text=f"◀️ {get_text('back', lang)}",
                callback_data=back_callback
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None


async def build_fasting_keyboard(
    dishes: List[Dict[str, Any]],
    user_id: int,
    user_service: UserService,
    back_callback: Optional[str] = None
) -> Optional[InlineKeyboardMarkup]:
    """
    Build inline keyboard with ingredient buttons for fasting dishes.

    Args:
        dishes: List of fasting dishes
        user_id: Telegram user ID
        user_service: User service for language lookup

    Returns:
        InlineKeyboardMarkup or None if no dishes
    """
    lang = await user_service.get_language(user_id)
    rows = []

    for index, dish in enumerate(dishes):
        rows.append([
            InlineKeyboardButton(
                text=f"🧾 {get_text('ingredients_btn', lang)}: {dish['name']}",
                callback_data=f"fasting_ingredients:{index}"
            )
        ])

    if back_callback:
        rows.append([
            InlineKeyboardButton(
                text=f"◀️ {get_text('back', lang)}",
                callback_data=back_callback
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None


async def build_back_keyboard(
    user_id: int,
    user_service: UserService,
    callback_data: str
) -> InlineKeyboardMarkup:
    """Build a single-button back keyboard."""
    lang = await user_service.get_language(user_id)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"◀️ {get_text('back', lang)}",
                    callback_data=callback_data
                )
            ]
        ]
    )


async def build_dish_select_keyboard(
    day_key: str,
    dishes: List[Dict[str, Any]],
    user_id: int,
    user_service: UserService,
    action: str = "edit"
) -> Optional[InlineKeyboardMarkup]:
    """
    Build inline keyboard for dish selection (edit/delete).

    Args:
        day_key: Day key
        dishes: List of dishes
        user_id: Telegram user ID
        user_service: User service for language lookup
        action: Action type ('edit' or 'delete')

    Returns:
        InlineKeyboardMarkup or None if no dishes
    """
    if not dishes:
        return None

    rows = []
    for index, dish in enumerate(dishes):
        rows.append([
            InlineKeyboardButton(
                text=f"🍽 {dish['name']}",
                callback_data=f"select_dish:{action}:{day_key}:{index}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


async def build_fasting_dish_select_keyboard(
    dishes: List[Dict[str, Any]],
    user_id: int,
    user_service: UserService,
    action: str = "edit"
) -> Optional[InlineKeyboardMarkup]:
    """
    Build inline keyboard for fasting dish selection.

    Args:
        dishes: List of fasting dishes
        user_id: Telegram user ID
        user_service: User service for language lookup
        action: Action type ('edit' or 'delete')

    Returns:
        InlineKeyboardMarkup or None if no dishes
    """
    if not dishes:
        return None

    rows = []
    for index, dish in enumerate(dishes):
        rows.append([
            InlineKeyboardButton(
                text=f"🌿 {dish['name']}",
                callback_data=f"select_fasting:{action}:{index}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


async def build_confirm_keyboard(
    user_id: int,
    user_service: UserService,
    callback_prefix: str = "confirm"
) -> InlineKeyboardMarkup:
    """
    Build confirmation keyboard (Yes/No).

    Args:
        user_id: Telegram user ID
        user_service: User service for language lookup
        callback_prefix: Prefix for callback data

    Returns:
        InlineKeyboardMarkup with Yes/No buttons
    """
    lang = await user_service.get_language(user_id)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"✅ {get_text('yes', lang)}",
                    callback_data=f"{callback_prefix}:yes"
                ),
                InlineKeyboardButton(
                    text=f"❌ {get_text('no', lang)}",
                    callback_data=f"{callback_prefix}:no"
                )
            ]
        ]
    )


async def build_edit_fields_keyboard(
    user_id: int,
    user_service: UserService,
    dish_index: int,
    day_key: str,
    is_fasting: bool = False
) -> InlineKeyboardMarkup:
    """
    Build keyboard for selecting which field to edit.

    Args:
        user_id: Telegram user ID
        user_service: User service for language lookup
        dish_index: Index of dish being edited
        day_key: Day key
        is_fasting: Whether editing fasting dish

    Returns:
        InlineKeyboardMarkup with field selection buttons
    """
    lang = await user_service.get_language(user_id)
    prefix = "fasting" if is_fasting else "regular"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"📝 {get_text('edit_name', lang)}",
                    callback_data=f"edit_field:{prefix}:{day_key}:{dish_index}:name"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"💰 {get_text('edit_price', lang)}",
                    callback_data=f"edit_field:{prefix}:{day_key}:{dish_index}:price"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"⚖️ {get_text('edit_weight', lang)}",
                    callback_data=f"edit_field:{prefix}:{day_key}:{dish_index}:weight"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"🧾 {get_text('edit_ingredients', lang)}",
                    callback_data=f"edit_field:{prefix}:{day_key}:{dish_index}:ingredients"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"◀️ {get_text('back', lang)}",
                    callback_data=f"back_to_admin"
                )
            ]
        ]
    )
