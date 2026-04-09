"""
Menu viewing handlers for Matrix Bot.
"""

import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.reply import build_main_keyboard
from keyboards.inline import (
    build_week_keyboard,
    build_ingredients_keyboard,
    build_fasting_keyboard,
    build_back_keyboard
)
from services.user_service import UserService
from services.menu_service import MenuService
from utils.i18n import get_text
from config import DAY_ORDER, DAY_NAMES

logger = logging.getLogger("matrix_bot")
router = Router()
nav_history = {}


def set_nav_root(user_id: int, screen_token: str) -> None:
    nav_history[user_id] = [screen_token]


def push_nav(user_id: int, screen_token: str) -> None:
    stack = nav_history.setdefault(user_id, [])
    if not stack:
        stack.append(screen_token)
    elif stack[-1] != screen_token:
        stack.append(screen_token)


def pop_nav(user_id: int) -> str:
    stack = nav_history.setdefault(user_id, ["main"])
    if len(stack) > 1:
        stack.pop()
    return stack[-1]


def register_menu_handlers(dp, user_service: UserService, menu_service: MenuService) -> None:
    """
    Register menu viewing handlers.

    Args:
        dp: Dispatcher instance
        user_service: User service instance
        menu_service: Menu service instance
    """

    @dp.callback_query(F.data == "today_menu")
    async def today_menu_callback(callback: CallbackQuery):
        """Show today's menu from the main menu."""
        user_id = callback.from_user.id
        lang = await user_service.get_language(user_id)
        await show_today_menu(callback.message, user_id, lang, user_service, menu_service)
        await callback.answer()

    @dp.callback_query(F.data == "week_menu")
    async def week_menu_callback(callback: CallbackQuery):
        """Show weekly menu day selection."""
        user_id = callback.from_user.id
        lang = await user_service.get_language(user_id)
        await show_week_menu(callback.message, user_id, lang, user_service, menu_service)
        await callback.answer()

    @dp.callback_query(F.data == "fasting_menu")
    async def fasting_menu_callback(callback: CallbackQuery):
        """Show fasting menu."""
        user_id = callback.from_user.id
        lang = await user_service.get_language(user_id)
        await show_fasting_menu(callback.message, user_id, lang, user_service, menu_service)
        await callback.answer()

    @dp.callback_query(F.data == "contacts")
    async def contacts_callback(callback: CallbackQuery):
        """Show contacts."""
        user_id = callback.from_user.id
        lang = await user_service.get_language(user_id)
        push_nav(user_id, "contacts")
        back_keyboard = await build_back_keyboard(user_id, user_service, "nav:back")
        await callback.message.edit_text(
            get_text("contacts_text", lang),
            parse_mode="Markdown",
            reply_markup=back_keyboard
        )
        await callback.answer()

    @dp.callback_query(F.data == "nav:back")
    async def back_callback(callback: CallbackQuery):
        """Return to the previous menu."""
        user_id = callback.from_user.id
        token = pop_nav(user_id)
        await render_screen_from_token(callback.message, user_id, token, user_service, menu_service)
        await callback.answer()

    @dp.callback_query(F.data.startswith("show_day:"))
    async def show_day_callback(callback: CallbackQuery):
        """Handle day selection callback."""
        user_id = callback.from_user.id
        lang = await user_service.get_language(user_id)
        day_key = callback.data.split(":")[1]

        await render_day_menu(callback.message, user_id, day_key, user_service, menu_service, lang)
        await callback.answer()

    @dp.callback_query(F.data.startswith("ingredients:"))
    async def ingredients_callback(callback: CallbackQuery):
        """Handle ingredients button click."""
        user_id = callback.from_user.id
        lang = await user_service.get_language(user_id)
        parts = callback.data.split(":")
        day_key = parts[1]
        index_str = parts[2]
        index = int(index_str)

        dishes = await menu_service.get_day_menu(day_key)

        if 0 <= index < len(dishes):
            dish = dishes[index]
            push_nav(user_id, "detail")
            text = (
                f"🍽 *{dish['name']}*\n"
                f"💵 {get_text('price_label', lang)}: {dish['price']}\n"
                f"🧾 {get_text('ingredients_label', lang)}: {dish['ingredients']}"
            )
            back_keyboard = await build_back_keyboard(user_id, user_service, "nav:back")
            await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_keyboard)
        else:
            push_nav(user_id, "detail")
            back_keyboard = await build_back_keyboard(user_id, user_service, "nav:back")
            await callback.message.edit_text(get_text("dish_not_found", lang), reply_markup=back_keyboard)

        await callback.answer()

    @dp.callback_query(F.data.startswith("fasting_ingredients:"))
    async def fasting_ingredients_callback(callback: CallbackQuery):
        """Handle fasting ingredients button click."""
        user_id = callback.from_user.id
        lang = await user_service.get_language(user_id)
        index = int(callback.data.split(":")[1])

        dishes = await menu_service.get_fasting_menu()

        if 0 <= index < len(dishes):
            dish = dishes[index]
            push_nav(user_id, "detail")
            weight_text = f"⚖️ {get_text('weight_label', lang)}: {dish.get('weight', 'N/A')}\n"
            text = (
                f"🌿 *{dish['name']}*\n"
                f"💵 {get_text('price_label', lang)}: {dish['price']}\n"
                f"{weight_text}"
                f"🧾 {get_text('ingredients_label', lang)}: {dish['ingredients']}"
            )
            back_keyboard = await build_back_keyboard(user_id, user_service, "nav:back")
            await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_keyboard)
        else:
            push_nav(user_id, "detail")
            back_keyboard = await build_back_keyboard(user_id, user_service, "nav:back")
            await callback.message.edit_text(get_text("dish_not_found", lang), reply_markup=back_keyboard)

        await callback.answer()


async def show_today_menu(
    message: Message,
    user_id: int,
    lang: str,
    user_service: UserService,
    menu_service: MenuService
) -> None:
    """Show today's menu."""
    push_nav(user_id, "today")
    day_key = get_today_key()
    dishes = await menu_service.get_day_menu(day_key)
    text = await build_day_menu_text(day_key, dishes, lang)
    keyboard = await build_ingredients_keyboard(
        day_key,
        dishes,
        user_id,
        user_service,
        back_callback="nav:back",
    )

    await message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)


async def show_week_menu(
    message: Message,
    user_id: int,
    lang: str,
    user_service: UserService,
    menu_service: MenuService
) -> None:
    """Show weekly menu day selection."""
    push_nav(user_id, "week")
    keyboard = await build_week_keyboard(user_id, user_service, back_callback="nav:back")
    await message.edit_text(
        get_text("choose_day", lang),
        reply_markup=keyboard
    )


async def show_fasting_menu(
    message: Message,
    user_id: int,
    lang: str,
    user_service: UserService,
    menu_service: MenuService
) -> None:
    """Show fasting menu."""
    push_nav(user_id, "fasting")
    dishes = await menu_service.get_fasting_menu()

    if not dishes:
        back_keyboard = await build_back_keyboard(user_id, user_service, "nav:back")
        await message.edit_text(get_text("fasting_empty", lang), reply_markup=back_keyboard)
        return

    text = get_text("fasting_title", lang)
    for i, dish in enumerate(dishes, start=1):
        text += f"{i}. {dish['name']} — {dish['price']}\n"
        if dish.get('weight'):
            text += f"   ⚖️ {get_text('weight_label', lang)}: {dish['weight']}\n"
        text += "\n"

    keyboard = await build_fasting_keyboard(dishes, user_id, user_service, back_callback="nav:back")
    await message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)


async def render_main_menu(
    message: Message,
    user_id: int,
    user_service: UserService
) -> None:
    """Render main menu."""
    push_nav(user_id, "main")
    keyboard = await build_main_keyboard(user_id, user_service)
    await message.edit_text(
        get_text("welcome", await user_service.get_language(user_id)),
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


async def render_day_menu(
    message: Message,
    user_id: int,
    day_key: str,
    user_service: UserService,
    menu_service: MenuService,
    lang: str | None = None
) -> None:
    """Render a day menu with ingredient buttons."""
    if lang is None:
        lang = await user_service.get_language(user_id)

    push_nav(user_id, f"day:{day_key}")
    dishes = await menu_service.get_day_menu(day_key)
    text = await build_day_menu_text(day_key, dishes, lang)
    keyboard = await build_ingredients_keyboard(
        day_key,
        dishes,
        user_id,
        user_service,
        back_callback="nav:back",
    )

    await message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)


async def render_screen_from_token(
    message: Message,
    user_id: int,
    token: str,
    user_service: UserService,
    menu_service: MenuService
) -> None:
    """Render a screen token from the navigation stack."""
    lang = await user_service.get_language(user_id)

    if token == "main":
        await render_main_menu(message, user_id, user_service)
    elif token == "today":
        await show_today_menu(message, user_id, lang, user_service, menu_service)
    elif token == "week":
        await show_week_menu(message, user_id, lang, user_service, menu_service)
    elif token == "fasting":
        await show_fasting_menu(message, user_id, lang, user_service, menu_service)
    elif token.startswith("day:"):
        day_key = token.split(":", 1)[1]
        await render_day_menu(message, user_id, day_key, user_service, menu_service, lang)
    else:
        await render_main_menu(message, user_id, user_service)


async def build_day_menu_text(
    day_key: str,
    dishes: list,
    lang: str
) -> str:
    """Build formatted text for day's menu."""
    day_names = DAY_NAMES.get(lang, DAY_NAMES["ru"])
    day_name = day_names.get(day_key, day_key)

    if not dishes:
        return get_text("menu_not_added", lang).format(day=day_name)

    text = get_text("menu_for_day", lang).format(day=day_name)
    for i, dish in enumerate(dishes, start=1):
        text += f"{i}. {dish['name']} — {dish['price']}\n"

    return text


def get_today_key() -> str:
    """Get day key for today."""
    weekday_index = datetime.now().weekday()
    return DAY_ORDER[weekday_index]
