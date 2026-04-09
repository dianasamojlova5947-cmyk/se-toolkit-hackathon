"""
Admin panel handlers for Matrix Bot.
Handles all admin operations including add, edit, delete dishes.
"""

import logging
from typing import Dict, Any
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import is_admin, DAY_ORDER, DAY_NAMES
from keyboards.reply import build_admin_keyboard, build_main_keyboard, build_admin_fasting_keyboard
from keyboards.inline import (
    build_dish_select_keyboard,
    build_fasting_dish_select_keyboard,
    build_confirm_keyboard,
    build_edit_fields_keyboard,
    build_back_keyboard
)
from services.user_service import UserService
from services.menu_service import MenuService
from utils.i18n import get_text

logger = logging.getLogger("matrix_bot")
router = Router()


class AdminStates(StatesGroup):
    """States for admin multi-step workflows."""
    waiting_day = State()
    waiting_name = State()
    waiting_price = State()
    waiting_weight = State()
    waiting_ingredients = State()
    waiting_edit_name = State()
    waiting_edit_price = State()
    waiting_edit_weight = State()
    waiting_edit_ingredients = State()
    waiting_fasting_name = State()
    waiting_fasting_price = State()
    waiting_fasting_weight = State()
    waiting_fasting_ingredients = State()


# Store temporary data for admin workflows
admin_data: Dict[int, Dict[str, Any]] = {}


def register_admin_handlers(dp, user_service: UserService, menu_service: MenuService) -> None:
    """
    Register admin handlers.

    Args:
        dp: Dispatcher instance
        user_service: User service instance
        menu_service: Menu service instance
    """

    @dp.callback_query(F.data == "admin_panel")
    async def admin_panel_callback(callback: CallbackQuery):
        """Open admin panel from inline main menu."""
        user_id = callback.from_user.id
        lang = await user_service.get_language(user_id)

        if not is_admin(user_id):
            logger.warning(f"Non-admin user {user_id} tried to access admin panel")
            await callback.message.edit_text(get_text("no_access", lang))
            await callback.answer()
            return

        keyboard = await build_admin_keyboard(user_id, user_service)
        await callback.message.edit_text(
            get_text("admin_welcome", lang),
            reply_markup=keyboard
        )
        await callback.answer()

    @dp.callback_query(F.data == "admin:back")
    async def admin_back_callback(callback: CallbackQuery, state: FSMContext):
        """Return to main menu."""
        user_id = callback.from_user.id
        lang = await user_service.get_language(user_id)

        await state.clear()
        if user_id in admin_data:
            del admin_data[user_id]

        keyboard = await build_main_keyboard(user_id, user_service)
        await callback.message.edit_text(
            get_text("welcome", lang),
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        await callback.answer()

    @dp.callback_query(F.data == "admin:add_dish")
    async def add_dish_callback(callback: CallbackQuery, state: FSMContext):
        """Start add dish flow from inline button."""
        user_id = callback.from_user.id
        lang = await user_service.get_language(user_id)

        if not is_admin(user_id):
            await callback.message.edit_text(get_text("no_access", lang))
            await callback.answer()
            return

        admin_data[user_id] = {"is_fasting": False}
        await state.set_state(AdminStates.waiting_day)

        back_keyboard = await build_back_keyboard(user_id, user_service, "admin:back")
        await callback.message.edit_text(get_text("write_day", lang), reply_markup=back_keyboard)
        await callback.answer()

    @dp.callback_query(F.data == "admin:view_menu")
    async def view_menu_callback(callback: CallbackQuery):
        """Show full menu to admin."""
        user_id = callback.from_user.id
        lang = await user_service.get_language(user_id)

        if not is_admin(user_id):
            await callback.message.edit_text(get_text("no_access", lang))
            await callback.answer()
            return

        menu = await menu_service.get_full_menu()
        day_names = DAY_NAMES.get(lang, DAY_NAMES["ru"])

        response = get_text("menu_title_admin", lang)

        for day_key in DAY_ORDER:
            response += f"*{day_names[day_key]}:*\n"
            dishes = menu.get(day_key, [])

            if not dishes:
                response += f"{get_text('no_dishes', lang)}\n\n"
                continue

            for dish in dishes:
                response += f"  • {dish['name']} — {dish['price']}\n"
            response += "\n"

        response += f"\n*🌿 {get_text('fasting_menu', lang).replace('🌿 ', '')}:*\n"
        fasting_dishes = menu.get("fasting_menu", [])

        if not fasting_dishes:
            response += f"{get_text('no_dishes', lang)}\n"
        else:
            for dish in fasting_dishes:
                response += f"  • {dish['name']} — {dish['price']}\n"

        await callback.message.edit_text(response, parse_mode="Markdown", reply_markup=await build_admin_keyboard(user_id, user_service))
        await callback.answer()

    @dp.callback_query(F.data == "admin:edit_dish")
    async def edit_dish_callback(callback: CallbackQuery):
        """Start edit dish flow from inline button."""
        user_id = callback.from_user.id
        lang = await user_service.get_language(user_id)

        if not is_admin(user_id):
            await callback.message.edit_text(get_text("no_access", lang))
            await callback.answer()
            return

        day_names = DAY_NAMES.get(lang, DAY_NAMES["ru"])
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        rows = []
        for day_key in DAY_ORDER:
            rows.append([
                InlineKeyboardButton(
                    text=day_names[day_key],
                    callback_data=f"edit_day:{day_key}"
                )
            ])

        rows.append([
            InlineKeyboardButton(
                text=get_text("back", lang),
                callback_data="admin:back"
            )
        ])

        keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
        await callback.message.edit_text(
            get_text("choose_day", lang),
            reply_markup=keyboard
        )
        await callback.answer()

    @dp.callback_query(F.data == "admin:delete_dish")
    async def delete_dish_callback(callback: CallbackQuery):
        """Start delete dish flow from inline button."""
        user_id = callback.from_user.id
        lang = await user_service.get_language(user_id)

        if not is_admin(user_id):
            await callback.message.edit_text(get_text("no_access", lang))
            await callback.answer()
            return

        day_names = DAY_NAMES.get(lang, DAY_NAMES["ru"])
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        rows = []
        for day_key in DAY_ORDER:
            rows.append([
                InlineKeyboardButton(
                    text=day_names[day_key],
                    callback_data=f"delete_day:{day_key}"
                )
            ])

        rows.append([
            InlineKeyboardButton(
                text=get_text("back", lang),
                callback_data="admin:back"
            )
        ])

        keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
        await callback.message.edit_text(
            get_text("choose_day", lang),
            reply_markup=keyboard
        )
        await callback.answer()

    @dp.callback_query(F.data == "admin:manage_fasting")
    async def manage_fasting_callback(callback: CallbackQuery):
        """Show fasting menu admin panel."""
        user_id = callback.from_user.id
        lang = await user_service.get_language(user_id)

        if not is_admin(user_id):
            await callback.message.edit_text(get_text("no_access", lang))
            await callback.answer()
            return

        keyboard = await build_admin_fasting_keyboard(user_id, user_service)
        await callback.message.edit_text(
            get_text("choose_fasting_action", lang),
            reply_markup=keyboard
        )
        await callback.answer()

    @dp.callback_query(F.data == "admin_fasting:add")
    async def add_fasting_callback(callback: CallbackQuery, state: FSMContext):
        """Start add fasting dish flow."""
        user_id = callback.from_user.id
        lang = await user_service.get_language(user_id)

        if not is_admin(user_id):
            await callback.message.edit_text(get_text("no_access", lang))
            await callback.answer()
            return

        admin_data[user_id] = {"is_fasting": True}
        await state.set_state(AdminStates.waiting_fasting_name)
        back_keyboard = await build_back_keyboard(user_id, user_service, "admin:back")
        await callback.message.edit_text(get_text("write_dish_name", lang), reply_markup=back_keyboard)
        await callback.answer()

    @dp.callback_query(F.data == "admin_fasting:edit")
    async def fasting_edit_callback(callback: CallbackQuery):
        """Stub for fasting edit."""
        lang = await user_service.get_language(callback.from_user.id)
        await callback.answer(
            "Пока не реализовано" if lang == "ru" else "Not implemented yet",
            show_alert=True
        )

    @dp.callback_query(F.data == "admin_fasting:delete")
    async def fasting_delete_callback(callback: CallbackQuery):
        """Stub for fasting delete."""
        lang = await user_service.get_language(callback.from_user.id)
        await callback.answer(
            "Пока не реализовано" if lang == "ru" else "Not implemented yet",
            show_alert=True
        )

    @dp.message(F.text.in_(["⚙️ Админ-панель", "⚙️ Admin panel", "Админ-панель", "Admin panel"]))
    async def admin_panel_handler(message: Message):
        """Handle admin panel button press."""
        user_id = message.from_user.id
        lang = await user_service.get_language(user_id)

        if not is_admin(user_id):
            logger.warning(f"Non-admin user {user_id} tried to access admin panel")
            await message.answer(get_text("no_access", lang))
            return

        logger.info(f"Admin {user_id} opened admin panel")
        keyboard = await build_admin_keyboard(user_id, user_service)
        await message.answer(
            get_text("admin_welcome", lang),
            reply_markup=keyboard
        )

    @dp.message(F.text.in_(["◀️ Назад", "◀️ Back", "Назад", "Back"]))
    async def back_handler(message: Message, state: FSMContext):
        """Handle back button - return to main menu."""
        user_id = message.from_user.id
        lang = await user_service.get_language(user_id)

        # Clear any active state
        await state.clear()
        if user_id in admin_data:
            del admin_data[user_id]

        keyboard = await build_main_keyboard(user_id, user_service)
        await message.answer(
            get_text("main_menu", lang),
            reply_markup=keyboard
        )

    # ==================== ADD DISH ====================

    @dp.message(F.text.in_(["➕ Добавить блюдо", "➕ Add dish", "Добавить блюдо", "Add dish"]))
    async def add_dish_start(message: Message, state: FSMContext):
        """Start add dish flow."""
        user_id = message.from_user.id
        lang = await user_service.get_language(user_id)

        if not is_admin(user_id):
            await message.answer(get_text("no_access", lang))
            return

        admin_data[user_id] = {"is_fasting": False}
        await state.set_state(AdminStates.waiting_day)

        await message.answer(get_text("write_day", lang))

    @dp.message(AdminStates.waiting_day)
    async def process_day(message: Message, state: FSMContext):
        """Process day input for add dish."""
        user_id = message.from_user.id
        lang = await user_service.get_language(user_id)
        day_key = message.text.strip().lower()

        if day_key not in DAY_ORDER:
            await message.answer(get_text("wrong_day", lang))
            return

        admin_data[user_id]["day_key"] = day_key
        await state.set_state(AdminStates.waiting_name)
        await message.answer(get_text("write_dish_name", lang))

    @dp.message(AdminStates.waiting_name)
    async def process_name(message: Message, state: FSMContext):
        """Process dish name input."""
        user_id = message.from_user.id
        lang = await user_service.get_language(user_id)

        admin_data[user_id]["dish_name"] = message.text.strip()
        await state.set_state(AdminStates.waiting_price)
        await message.answer(get_text("write_price", lang))

    @dp.message(AdminStates.waiting_price)
    async def process_price(message: Message, state: FSMContext):
        """Process price input."""
        user_id = message.from_user.id
        lang = await user_service.get_language(user_id)

        admin_data[user_id]["dish_price"] = message.text.strip()
        await state.set_state(AdminStates.waiting_ingredients)
        await message.answer(get_text("write_ingredients", lang))

    @dp.message(AdminStates.waiting_ingredients)
    async def process_ingredients(message: Message, state: FSMContext):
        """Process ingredients and save dish."""
        user_id = message.from_user.id
        lang = await user_service.get_language(user_id)

        ingredients = message.text.strip()
        data = admin_data.get(user_id, {})

        day_key = data.get("day_key")
        dish_name = data.get("dish_name", "Unknown")
        dish_price = data.get("dish_price", "0")
        is_fasting = data.get("is_fasting", False)

        success = await menu_service.add_dish(
            day_key=day_key,
            name=dish_name,
            price=dish_price,
            ingredients=ingredients,
            is_fasting=is_fasting
        )

        if success:
            day_names = DAY_NAMES.get(lang, DAY_NAMES["ru"])
            day_name = day_names.get(day_key, day_key) if day_key else ""
            await message.answer(
                get_text("dish_added", lang).format(dish_name=dish_name, day=day_name),
                parse_mode="Markdown"
            )
            logger.info(f"Admin {user_id} added dish: {dish_name}")
        else:
            await message.answer(get_text("error_occurred", lang))

        await state.clear()
        if user_id in admin_data:
            del admin_data[user_id]

        keyboard = await build_admin_keyboard(user_id, user_service)
        await message.answer(
            get_text("admin_welcome", lang),
            reply_markup=keyboard
        )

    # ==================== EDIT DISH ====================

    @dp.message(F.text.in_(["✏️ Редактировать блюдо", "✏️ Edit dish", "Редактировать блюдо", "Edit dish"]))
    async def edit_dish_start(message: Message, state: FSMContext):
        """Start edit dish flow - show day selection."""
        user_id = message.from_user.id
        lang = await user_service.get_language(user_id)

        if not is_admin(user_id):
            await message.answer(get_text("no_access", lang))
            return

        # Show inline keyboard with day buttons
        day_names = DAY_NAMES.get(lang, DAY_NAMES["ru"])
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        rows = []
        for day_key in DAY_ORDER:
            rows.append([
                InlineKeyboardButton(
                    text=day_names[day_key],
                    callback_data=f"edit_day:{day_key}"
                )
            ])

        keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
        await message.answer(
            get_text("choose_day", lang),
            reply_markup=keyboard
        )

    @dp.callback_query(F.data.startswith("edit_day:"))
    async def edit_day_callback(callback: CallbackQuery, state: FSMContext):
        """Handle day selection for edit."""
        user_id = callback.from_user.id
        lang = await user_service.get_language(user_id)
        day_key = callback.data.split(":")[1]

        dishes = await menu_service.get_day_menu(day_key)

        if not dishes:
            await callback.message.answer(get_text("no_dishes_day", lang))
            await callback.answer()
            return

        admin_data[user_id] = {"day_key": day_key, "is_fasting": False}
        keyboard = await build_dish_select_keyboard(day_key, dishes, user_id, user_service, "edit")

        await callback.message.answer(
            get_text("choose_dish_edit", lang),
            reply_markup=keyboard
        )
        await callback.answer()

    @dp.callback_query(F.data.startswith("select_dish:edit:"))
    async def select_dish_edit_callback(callback: CallbackQuery, state: FSMContext):
        """Handle dish selection for editing."""
        user_id = callback.from_user.id
        lang = await user_service.get_language(user_id)

        parts = callback.data.split(":")
        day_key = parts[2]
        dish_index = int(parts[3])

        dishes = await menu_service.get_day_menu(day_key)

        if dish_index >= len(dishes):
            await callback.message.answer(get_text("dish_not_found", lang))
            await callback.answer()
            return

        admin_data[user_id] = {
            "day_key": day_key,
            "dish_index": dish_index,
            "is_fasting": False
        }

        keyboard = await build_edit_fields_keyboard(user_id, user_service, dish_index, day_key)
        await callback.message.answer(
            get_text("edit_what", lang),
            reply_markup=keyboard
        )
        await callback.answer()

    @dp.callback_query(F.data.startswith("edit_field:regular:"))
    async def edit_field_callback(callback: CallbackQuery, state: FSMContext):
        """Handle field selection for editing."""
        user_id = callback.from_user.id
        lang = await user_service.get_language(user_id)

        parts = callback.data.split(":")
        day_key = parts[2]
        dish_index = int(parts[3])
        field = parts[4]

        admin_data[user_id] = {
            "day_key": day_key,
            "dish_index": dish_index,
            "field": field,
            "is_fasting": False
        }

        field_states = {
            "name": AdminStates.waiting_edit_name,
            "price": AdminStates.waiting_edit_price,
            "weight": AdminStates.waiting_edit_weight,
            "ingredients": AdminStates.waiting_edit_ingredients
        }

        field_prompts = {
            "name": "write_new_name",
            "price": "write_new_price",
            "weight": "write_new_weight",
            "ingredients": "write_new_ingredients"
        }

        await state.set_state(field_states[field])
        await callback.message.answer(get_text(field_prompts[field], lang))
        await callback.answer()

    @dp.message(AdminStates.waiting_edit_name)
    async def process_edit_name(message: Message, state: FSMContext):
        """Process new name."""
        await _process_edit_field(message, state, "name", user_service, menu_service)

    @dp.message(AdminStates.waiting_edit_price)
    async def process_edit_price(message: Message, state: FSMContext):
        """Process new price."""
        await _process_edit_field(message, state, "price", user_service, menu_service)

    @dp.message(AdminStates.waiting_edit_weight)
    async def process_edit_weight(message: Message, state: FSMContext):
        """Process new weight."""
        await _process_edit_field(message, state, "weight", user_service, menu_service)

    @dp.message(AdminStates.waiting_edit_ingredients)
    async def process_edit_ingredients(message: Message, state: FSMContext):
        """Process new ingredients."""
        await _process_edit_field(message, state, "ingredients", user_service, menu_service)

    # ==================== DELETE DISH ====================

    @dp.message(F.text.in_(["🗑 Удалить блюдо", "🗑 Delete dish", "Удалить блюдо", "Delete dish"]))
    async def delete_dish_start(message: Message, state: FSMContext):
        """Start delete dish flow - show day selection."""
        user_id = message.from_user.id
        lang = await user_service.get_language(user_id)

        if not is_admin(user_id):
            await message.answer(get_text("no_access", lang))
            return

        day_names = DAY_NAMES.get(lang, DAY_NAMES["ru"])
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        rows = []
        for day_key in DAY_ORDER:
            rows.append([
                InlineKeyboardButton(
                    text=day_names[day_key],
                    callback_data=f"delete_day:{day_key}"
                )
            ])

        keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
        await message.answer(
            get_text("choose_day", lang),
            reply_markup=keyboard
        )

    @dp.callback_query(F.data.startswith("delete_day:"))
    async def delete_day_callback(callback: CallbackQuery, state: FSMContext):
        """Handle day selection for delete."""
        user_id = callback.from_user.id
        lang = await user_service.get_language(user_id)
        day_key = callback.data.split(":")[1]

        dishes = await menu_service.get_day_menu(day_key)

        if not dishes:
            await callback.message.answer(get_text("no_dishes_day", lang))
            await callback.answer()
            return

        admin_data[user_id] = {"day_key": day_key, "is_fasting": False}
        keyboard = await build_dish_select_keyboard(day_key, dishes, user_id, user_service, "delete")

        await callback.message.answer(
            get_text("choose_dish_delete", lang),
            reply_markup=keyboard
        )
        await callback.answer()

    @dp.callback_query(F.data.startswith("select_dish:delete:"))
    async def select_dish_delete_callback(callback: CallbackQuery, state: FSMContext):
        """Handle dish selection for deletion confirmation."""
        user_id = callback.from_user.id
        lang = await user_service.get_language(user_id)

        parts = callback.data.split(":")
        day_key = parts[2]
        dish_index = int(parts[3])

        dishes = await menu_service.get_day_menu(day_key)

        if dish_index >= len(dishes):
            await callback.message.answer(get_text("dish_not_found", lang))
            await callback.answer()
            return

        dish = dishes[dish_index]
        admin_data[user_id] = {
            "day_key": day_key,
            "dish_index": dish_index,
            "dish_name": dish["name"],
            "is_fasting": False
        }

        keyboard = await build_confirm_keyboard(user_id, user_service, f"confirm_delete:{day_key}:{dish_index}")
        await callback.message.answer(
            get_text("confirm_delete", lang).format(dish_name=dish["name"]),
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        await callback.answer()

    @dp.callback_query(F.data.startswith("confirm_delete:"))
    async def confirm_delete_callback(callback: CallbackQuery, state: FSMContext):
        """Handle delete confirmation."""
        user_id = callback.from_user.id
        lang = await user_service.get_language(user_id)

        parts = callback.data.split(":")
        action = parts[3]

        if action != "yes":
            await callback.message.answer(get_text("delete_cancelled", lang))
            await callback.answer()
            return

        data = admin_data.get(user_id, {})
        day_key = data.get("day_key")
        dish_index = data.get("dish_index")
        dish_name = data.get("dish_name")

        success = await menu_service.delete_dish(dish_index, day_key)

        if success:
            day_names = DAY_NAMES.get(lang, DAY_NAMES["ru"])
            day_name = day_names.get(day_key, day_key)
            await callback.message.answer(
                get_text("dish_deleted", lang).format(dish_name=dish_name, day=day_name),
                parse_mode="Markdown"
            )
            logger.info(f"Admin {user_id} deleted dish: {dish_name}")
        else:
            await callback.message.answer(get_text("error_occurred", lang))

        if user_id in admin_data:
            del admin_data[user_id]

        await callback.answer()

    # ==================== VIEW MENU ====================

    @dp.message(F.text.in_(["📋 Смотреть меню", "📋 View menu", "Смотреть меню", "View menu"]))
    async def view_menu_handler(message: Message):
        """Show full menu to admin."""
        user_id = message.from_user.id
        lang = await user_service.get_language(user_id)

        if not is_admin(user_id):
            await message.answer(get_text("no_access", lang))
            return

        menu = await menu_service.get_full_menu()
        day_names = DAY_NAMES.get(lang, DAY_NAMES["ru"])

        response = get_text("menu_title_admin", lang)

        for day_key in DAY_ORDER:
            response += f"*{day_names[day_key]}:*\n"
            dishes = menu.get(day_key, [])

            if not dishes:
                response += f"{get_text('no_dishes', lang)}\n\n"
                continue

            for dish in dishes:
                response += f"  • {dish['name']} — {dish['price']}\n"
            response += "\n"

        # Add fasting menu
        response += f"\n*🌿 {get_text('fasting_menu', lang).replace('🌿 ', '')}:*\n"
        fasting_dishes = menu.get("fasting_menu", [])

        if not fasting_dishes:
            response += f"{get_text('no_dishes', lang)}\n"
        else:
            for dish in fasting_dishes:
                response += f"  • {dish['name']} — {dish['price']}\n"

        await message.answer(response, parse_mode="Markdown")

    # ==================== FASTING MENU MANAGEMENT ====================

    @dp.message(F.text.in_(["🌿 Управление постным меню", "🌿 Manage lenten menu", "Управление постным меню", "Manage lenten menu"]))
    async def fasting_menu_handler(message: Message):
        """Show fasting menu admin panel."""
        user_id = message.from_user.id
        lang = await user_service.get_language(user_id)

        if not is_admin(user_id):
            await message.answer(get_text("no_access", lang))
            return

        keyboard = await build_admin_fasting_keyboard(user_id, user_service)
        await message.answer(
            get_text("choose_fasting_action", lang),
            reply_markup=keyboard
        )

    @dp.message(F.text.in_(["🌿 Добавить постное блюдо", "🌿 Add lenten dish", "Добавить постное блюдо", "Add lenten dish"]))
    async def add_fasting_start(message: Message, state: FSMContext):
        """Start add fasting dish flow."""
        user_id = message.from_user.id
        lang = await user_service.get_language(user_id)

        if not is_admin(user_id):
            await message.answer(get_text("no_access", lang))
            return

        admin_data[user_id] = {"is_fasting": True}
        await state.set_state(AdminStates.waiting_fasting_name)
        await message.answer(get_text("write_dish_name", lang))

    @dp.message(AdminStates.waiting_fasting_name)
    async def process_fasting_name(message: Message, state: FSMContext):
        """Process fasting dish name."""
        user_id = message.from_user.id

        admin_data[user_id]["dish_name"] = message.text.strip()
        await state.set_state(AdminStates.waiting_fasting_price)
        lang = await user_service.get_language(user_id)
        await message.answer(get_text("write_price", lang))

    @dp.message(AdminStates.waiting_fasting_price)
    async def process_fasting_price(message: Message, state: FSMContext):
        """Process fasting dish price."""
        user_id = message.from_user.id

        admin_data[user_id]["dish_price"] = message.text.strip()
        await state.set_state(AdminStates.waiting_fasting_weight)
        lang = await user_service.get_language(user_id)
        await message.answer(get_text("write_weight", lang))

    @dp.message(AdminStates.waiting_fasting_weight)
    async def process_fasting_weight(message: Message, state: FSMContext):
        """Process fasting dish weight."""
        user_id = message.from_user.id

        admin_data[user_id]["dish_weight"] = message.text.strip()
        await state.set_state(AdminStates.waiting_fasting_ingredients)
        lang = await user_service.get_language(user_id)
        await message.answer(get_text("write_ingredients", lang))

    @dp.message(AdminStates.waiting_fasting_ingredients)
    async def process_fasting_ingredients(message: Message, state: FSMContext):
        """Process fasting dish ingredients and save."""
        user_id = message.from_user.id
        lang = await user_service.get_language(user_id)

        ingredients = message.text.strip()
        data = admin_data.get(user_id, {})

        dish_name = data.get("dish_name", "Unknown")
        dish_price = data.get("dish_price", "0")
        dish_weight = data.get("dish_weight", "")

        success = await menu_service.add_dish(
            day_key="",
            name=dish_name,
            price=dish_price,
            ingredients=ingredients,
            weight=dish_weight,
            is_fasting=True
        )

        if success:
            await message.answer(
                get_text("dish_added", lang).format(dish_name=dish_name, day="🌿"),
                parse_mode="Markdown"
            )
            logger.info(f"Admin {user_id} added fasting dish: {dish_name}")
        else:
            await message.answer(get_text("error_occurred", lang))

        await state.clear()
        if user_id in admin_data:
            del admin_data[user_id]

        keyboard = await build_admin_fasting_keyboard(user_id, user_service)
        await message.answer(
            get_text("choose_fasting_action", lang),
            reply_markup=keyboard
        )


async def _process_edit_field(
    message: Message,
    state: FSMContext,
    field: str,
    user_service: UserService,
    menu_service: MenuService
) -> None:
    """Process edit field and update dish."""
    user_id = message.from_user.id
    lang = await user_service.get_language(user_id)

    data = admin_data.get(user_id, {})
    day_key = data.get("day_key")
    dish_index = data.get("dish_index")
    is_fasting = data.get("is_fasting", False)

    new_value = message.text.strip()

    # For JSON mode, we need to use index-based update
    if is_fasting:
        dishes = await menu_service.get_fasting_menu()
    else:
        dishes = await menu_service.get_day_menu(day_key)

    if dish_index >= len(dishes):
        await message.answer(get_text("dish_not_found", lang))
        await state.clear()
        return

    # For database mode, get dish ID
    if menu_service.use_database and dishes[dish_index].get("id"):
        dish_id = dishes[dish_index]["id"]
        if field == "name":
            await menu_service.update_dish(dish_id, name=new_value)
        elif field == "price":
            await menu_service.update_dish(dish_id, price=new_value)
        elif field == "weight":
            await menu_service.update_dish(dish_id, weight=new_value)
        elif field == "ingredients":
            await menu_service.update_dish(dish_id, ingredients=new_value)
    else:
        # JSON mode
        if field == "name":
            await menu_service._update_dish_json(dish_index, name=new_value, day_key=day_key, is_fasting=is_fasting)
        elif field == "price":
            await menu_service._update_dish_json(dish_index, price=new_value, day_key=day_key, is_fasting=is_fasting)
        elif field == "weight":
            await menu_service._update_dish_json(dish_index, weight=new_value, day_key=day_key, is_fasting=is_fasting)
        elif field == "ingredients":
            await menu_service._update_dish_json(dish_index, ingredients=new_value, day_key=day_key, is_fasting=is_fasting)

    await message.answer(get_text("dish_updated", lang))
    logger.info(f"Admin {user_id} updated {field} for dish at index {dish_index}")

    await state.clear()
    if user_id in admin_data:
        del admin_data[user_id]

    keyboard = await build_admin_keyboard(user_id, user_service)
    await message.answer(
        get_text("admin_welcome", lang),
        reply_markup=keyboard
    )
