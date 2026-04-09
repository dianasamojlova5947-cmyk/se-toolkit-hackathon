"""
Reply keyboard builders for Matrix Bot.
Creates keyboard layouts for main menu and admin panel.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.user_service import UserService
from utils.i18n import get_text


async def build_main_keyboard(user_id: int, user_service: UserService) -> InlineKeyboardMarkup:
    """
    Build main menu keyboard.

    Args:
        user_id: Telegram user ID
        user_service: User service for language lookup

    Returns:
        InlineKeyboardMarkup with main menu buttons
    """
    lang = await user_service.get_language(user_id)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text("today_menu", lang), callback_data="today_menu")],
            [InlineKeyboardButton(text=get_text("week_menu", lang), callback_data="week_menu")],
            [InlineKeyboardButton(text=get_text("fasting_menu", lang), callback_data="fasting_menu")],
            [InlineKeyboardButton(text=get_text("favorites", lang), callback_data="favorites")],
            [InlineKeyboardButton(text=get_text("contacts", lang), callback_data="contacts")],
            [InlineKeyboardButton(text=get_text("language_btn", lang), callback_data="change_language")],
            [InlineKeyboardButton(text=get_text("admin_panel", lang), callback_data="admin_panel")],
        ],
    )


async def build_admin_keyboard(user_id: int, user_service: UserService) -> InlineKeyboardMarkup:
    """
    Build admin panel keyboard.

    Args:
        user_id: Telegram user ID
        user_service: User service for language lookup

    Returns:
        InlineKeyboardMarkup with admin buttons
    """
    lang = await user_service.get_language(user_id)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text("add_dish", lang), callback_data="admin:add_dish")],
            [InlineKeyboardButton(text=get_text("edit_dish", lang), callback_data="admin:edit_dish")],
            [InlineKeyboardButton(text=get_text("delete_dish", lang), callback_data="admin:delete_dish")],
            [InlineKeyboardButton(text=get_text("manage_fasting", lang), callback_data="admin:manage_fasting")],
            [InlineKeyboardButton(text=get_text("view_menu", lang), callback_data="admin:view_menu")],
            [InlineKeyboardButton(text=get_text("back", lang), callback_data="admin:back")],
        ],
    )


def build_language_keyboard() -> InlineKeyboardMarkup:
    """
    Build language selection keyboard.

    Returns:
        InlineKeyboardMarkup with language buttons
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang:ru"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang:en"),
            ],
        ],
    )


async def build_admin_fasting_keyboard(
    user_id: int,
    user_service: UserService
) -> InlineKeyboardMarkup:
    """
    Build fasting menu admin keyboard.

    Args:
        user_id: Telegram user ID
        user_service: User service for language lookup

    Returns:
        InlineKeyboardMarkup with fasting menu buttons
    """
    lang = await user_service.get_language(user_id)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text("add_fasting_dish", lang), callback_data="admin_fasting:add")],
            [InlineKeyboardButton(text=get_text("edit_fasting", lang), callback_data="admin_fasting:edit")],
            [InlineKeyboardButton(text=get_text("delete_fasting", lang), callback_data="admin_fasting:delete")],
            [InlineKeyboardButton(text=get_text("back", lang), callback_data="admin:back")],
        ],
    )
