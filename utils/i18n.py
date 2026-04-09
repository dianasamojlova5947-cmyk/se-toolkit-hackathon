"""
Internationalization (i18n) module.
Provides translations for all bot messages.
"""

from typing import Dict

TEXTS: Dict[str, Dict[str, str]] = {
    "ru": {
        # Language selection
        "choose_language": "🌐 Выбери язык / Choose language",
        "language_saved": "✅ Язык сохранён: Русский",
        "change_language": "Сменить язык",

        # Main menu
        "welcome": (
            "👋 Привет! Я бот столовой *MATRIX*, твой главный помощник в навигации! 🧭\n\n"
            "🍽 Помогу быстро посмотреть меню на сегодня\n"
            "📅 Покажу меню на неделю\n"
            "🌿 Найду постные блюда\n\n"
            "✨ Если нужно что-то найти, я всегда рядом!"
        ),
        "today_menu": "🍽 Сегодняшнее меню",
        "week_menu": "📅 Меню на неделю",
        "fasting_menu": "🌿 Постное меню",
        "contacts": "ℹ️ Информация",
        "admin_panel": "⚙️ Админ-панель",
        "language_btn": "🌐 Сменить язык",
        "back": "◀️ Назад",

        # Admin panel
        "add_dish": "➕ Добавить блюдо",
        "edit_dish": "✏️ Редактировать блюдо",
        "delete_dish": "🗑 Удалить блюдо",
        "add_fasting_dish": "🌿 Добавить постное блюдо",
        "manage_fasting": "🌿 Управление постным меню",
        "view_menu": "📋 Смотреть меню",
        "no_access": "❌ У тебя нет доступа к админ-панели.",
        "admin_welcome": "🔐 Добро пожаловать в админ-панель!\n\nВыберите действие:",

        # Day selection
        "choose_day": "📅 Выбери день недели:",

        # Contacts
        "contacts_text": (
            "📍 *Контакты столовой Matrix*\n\n"
            "⏰ *Режим работы:* с 8:00 до 20:00, без выходных\n\n"
            "📍 *Адрес:* Университетская, 1 (1-й этаж)\n\n"
            "💬 Есть предложение? Пиши Шеф-повару: @KborisoVa"
        ),

        # Menu display
        "fasting_title": "🌿 *Постное меню:*\n\n",
        "fasting_empty": "❌ Постное меню пока не добавлено.",
        "ingredients_btn": "Ингредиенты",
        "ingredients_label": "🧾 Ингредиенты",
        "price_label": "💵 Цена",
        "weight_label": "⚖️ Выход",
        "dish_not_found": "❌ Блюдо не найдено.",
        "menu_not_added": "❌ На {day} меню пока не добавлено.",
        "menu_for_day": "🍽 *Меню на {day}:*\n\n",
        "unknown_message": "❓ Я не понял сообщение. Выбери кнопку из меню.",
        "main_menu": "🏠 Главное меню.",

        # Add dish flow
        "write_day": "📅 Напиши день недели:\n\nmonday, tuesday, wednesday, thursday, friday, saturday, sunday",
        "wrong_day": "❌ Неверный день. Попробуй ещё раз.\n\nmonday, tuesday, wednesday, thursday, friday, saturday, sunday",
        "write_dish_name": "📝 Теперь напиши название блюда:",
        "write_price": "💰 Теперь напиши цену блюда.\n\nПример: 220 ₽",
        "write_weight": "⚖️ Напиши вес блюда.\n\nПример: 150 гр",
        "write_ingredients": "🧾 Теперь напиши ингредиенты блюда:",
        "dish_added": "✅ Блюдо *{dish_name}* добавлено в меню на {day}",

        # Edit dish flow
        "choose_dish_edit": "✏️ Выбери блюдо для редактирования:",
        "choose_dish_delete": "🗑 Выбери блюдо для удаления:",
        "edit_what": "✏️ Что хочешь изменить?",
        "edit_name": "📝 Название",
        "edit_price": "💰 Цена",
        "edit_weight": "⚖️ Вес",
        "edit_ingredients": "🧾 Ингредиенты",
        "write_new_name": "📝 Напиши новое название:",
        "write_new_price": "💰 Напиши новую цену:",
        "write_new_weight": "⚖️ Напиши новый вес:",
        "write_new_ingredients": "🧾 Напиши новые ингредиенты:",
        "dish_updated": "✅ Блюдо обновлено!",

        # Delete dish flow
        "confirm_delete": "🗑 Удалить блюдо *{dish_name}*?",
        "yes": "✅ Да",
        "no": "❌ Нет",
        "dish_deleted": "✅ Блюдо *{dish_name}* удалено из меню на {day}.",
        "delete_cancelled": "❌ Удаление отменено.",

        # View menu (admin)
        "menu_title_admin": "📋 *Текущее меню:*\n\n",
        "no_dishes": "—",

        # Fasting menu admin
        "fasting_menu_admin": "🌿 *Постное меню:*\n\n",
        "choose_fasting_action": "🌿 Управление постным меню:",
        "edit_fasting": "✏️ Редактировать",
        "delete_fasting": "🗑 Удалить",

        # Errors
        "error_occurred": "❌ Произошла ошибка. Попробуй позже.",
        "menu_empty": "❌ Меню пустое.",
        "no_dishes_day": "❌ В этот день нет блюд.",

        # Language selection
        "language_button_ru": "🇷🇺 Русский",
        "language_button_en": "🇬🇧 English",
    },
    "en": {
        # Language selection
        "choose_language": "🌐 Choose language / Выбери язык",
        "language_saved": "✅ Language saved: English",
        "change_language": "Change language",

        # Main menu
        "welcome": (
            "👋 Hello! I am the *MATRIX* cafeteria bot, your main navigation assistant! 🧭\n\n"
            "🍽 I can quickly show today's menu\n"
            "📅 I can show the weekly menu\n"
            "🌿 I can find the lenten dishes\n\n"
            "✨ If you need anything, I'm always here!"
        ),
        "today_menu": "🍽 Today's menu",
        "week_menu": "📅 Weekly menu",
        "fasting_menu": "🌿 Lenten menu",
        "contacts": "ℹ️ Information",
        "admin_panel": "⚙️ Admin panel",
        "language_btn": "🌐 Change language",
        "back": "◀️ Back",

        # Admin panel
        "add_dish": "➕ Add dish",
        "edit_dish": "✏️ Edit dish",
        "delete_dish": "🗑 Delete dish",
        "add_fasting_dish": "🌿 Add lenten dish",
        "manage_fasting": "🌿 Manage lenten menu",
        "view_menu": "📋 View menu",
        "no_access": "❌ You do not have access to the admin panel.",
        "admin_welcome": "🔐 Welcome to the admin panel!\n\nSelect an action:",

        # Day selection
        "choose_day": "📅 Choose a day of the week:",

        # Contacts
        "contacts_text": (
            "📍 *Matrix Cafeteria Contacts*\n\n"
            "⏰ *Opening hours:* 8:00 to 20:00, every day\n\n"
            "📍 *Address:* Universitetskaya, 1 (1st floor)\n\n"
            "💬 Have a suggestion? Message the Chef: @KborisoVa"
        ),

        # Menu display
        "fasting_title": "🌿 *Lenten menu:*\n\n",
        "fasting_empty": "❌ The lenten menu has not been added yet.",
        "ingredients_btn": "Ingredients",
        "ingredients_label": "🧾 Ingredients",
        "price_label": "💵 Price",
        "weight_label": "⚖️ Weight",
        "dish_not_found": "❌ Dish not found.",
        "menu_not_added": "❌ No menu has been added for {day} yet.",
        "menu_for_day": "🍽 *Menu for {day}:*\n\n",
        "unknown_message": "❓ I did not understand the message. Please choose a button from the menu.",
        "main_menu": "🏠 Main menu.",

        # Add dish flow
        "write_day": "📅 Enter the weekday:\n\nmonday, tuesday, wednesday, thursday, friday, saturday, sunday",
        "wrong_day": "❌ Wrong day. Try again.\n\nmonday, tuesday, wednesday, thursday, friday, saturday, sunday",
        "write_dish_name": "📝 Now enter the dish name:",
        "write_price": "💰 Now enter the price.\n\nExample: 220 ₽",
        "write_weight": "⚖️ Enter the dish weight.\n\nExample: 150 g",
        "write_ingredients": "🧾 Now enter the dish ingredients:",
        "dish_added": "✅ Dish *{dish_name}* was added to the menu for {day}",

        # Edit dish flow
        "choose_dish_edit": "✏️ Select a dish to edit:",
        "choose_dish_delete": "🗑 Select a dish to delete:",
        "edit_what": "✏️ What would you like to edit?",
        "edit_name": "📝 Name",
        "edit_price": "💰 Price",
        "edit_weight": "⚖️ Weight",
        "edit_ingredients": "🧾 Ingredients",
        "write_new_name": "📝 Enter the new name:",
        "write_new_price": "💰 Enter the new price:",
        "write_new_weight": "⚖️ Enter the new weight:",
        "write_new_ingredients": "🧾 Enter the new ingredients:",
        "dish_updated": "✅ Dish updated!",

        # Delete dish flow
        "confirm_delete": "🗑 Delete dish *{dish_name}*?",
        "yes": "✅ Yes",
        "no": "❌ No",
        "dish_deleted": "✅ Dish *{dish_name}* deleted from {day} menu.",
        "delete_cancelled": "❌ Deletion cancelled.",

        # View menu (admin)
        "menu_title_admin": "📋 *Current menu:*\n\n",
        "no_dishes": "—",

        # Fasting menu admin
        "fasting_menu_admin": "🌿 *Lenten menu:*\n\n",
        "choose_fasting_action": "🌿 Manage lenten menu:",
        "edit_fasting": "✏️ Edit",
        "delete_fasting": "🗑 Delete",

        # Errors
        "error_occurred": "❌ An error occurred. Please try again later.",
        "menu_empty": "❌ The menu is empty.",
        "no_dishes_day": "❌ No dishes for this day.",

        # Language selection
        "language_button_ru": "🇷🇺 Русский",
        "language_button_en": "🇬🇧 English",
    }
}


def get_text(key: str, lang: str = "ru") -> str:
    """
    Get translated text by key.

    Args:
        key: Translation key
        lang: Language code (ru/en)

    Returns:
        Translated string
    """
    return TEXTS.get(lang, TEXTS["ru"]).get(key, key)
