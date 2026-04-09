"""
Start and language selection handlers for Matrix Bot.
"""

import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from keyboards.reply import build_language_keyboard, build_main_keyboard
from services.user_service import UserService
from utils.i18n import get_text, TEXTS

logger = logging.getLogger("matrix_bot")
router = Router()


def register_start_handlers(dp, user_service: UserService) -> None:
    """
    Register start and language handlers.

    Args:
        dp: Dispatcher instance
        user_service: User service instance
    """

    @dp.message(CommandStart())
    async def start_handler(message: Message):
        """Handle /start command - show language selection."""
        user_id = message.from_user.id
        lang = await user_service.get_language(user_id)

        logger.info(f"User {user_id} started the bot")

        # Check if user already has a language preference
        if lang:
            # User has language preference, show main menu
            keyboard = await build_main_keyboard(user_id, user_service)
            await message.answer(
                get_text("welcome", lang),
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        else:
            # New user, show language selection
            await message.answer(
                get_text("choose_language", lang),
                reply_markup=build_language_keyboard()
            )

    @dp.callback_query(F.data == "set_lang:ru")
    async def set_russian(callback: CallbackQuery):
        """Handle Russian language selection."""
        user_id = callback.from_user.id
        await user_service.set_language(user_id, "ru")

        logger.info(f"User {user_id} selected Russian language")

        keyboard = await build_main_keyboard(user_id, user_service)
        await callback.message.edit_text(
            get_text("language_saved", "ru"),
            reply_markup=keyboard
        )
        await callback.message.answer(
            get_text("welcome", "ru"),
            parse_mode="Markdown"
        )
        await callback.answer()

    @dp.callback_query(F.data == "set_lang:en")
    async def set_english(callback: CallbackQuery):
        """Handle English language selection."""
        user_id = callback.from_user.id
        await user_service.set_language(user_id, "en")

        logger.info(f"User {user_id} selected English language")

        keyboard = await build_main_keyboard(user_id, user_service)
        await callback.message.edit_text(
            get_text("language_saved", "en"),
            reply_markup=keyboard
        )
        await callback.message.answer(
            get_text("welcome", "en"),
            parse_mode="Markdown"
        )
        await callback.answer()

    @dp.callback_query(F.data == "change_language")
    async def change_language(callback: CallbackQuery):
        """Handle language change request."""
        user_id = callback.from_user.id
        logger.info(f"User {user_id} requested language change")
        await callback.message.edit_text(
            get_text("choose_language", await user_service.get_language(user_id)),
            reply_markup=build_language_keyboard()
        )
        await callback.answer()
