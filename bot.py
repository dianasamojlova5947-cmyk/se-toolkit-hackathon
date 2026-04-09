#!/usr/bin/env python3
import asyncio
import json
import os
from datetime import datetime

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from config import is_admin, ADMINS_FILE

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = str(os.getenv("ADMIN_ID", "")).strip()

MENU_FILE = "menu.json"
USERS_FILE = "users.json"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")

DAY_ORDER = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]

DAY_NAMES = {
    "ru": {
        "monday": "Понедельник",
        "tuesday": "Вторник",
        "wednesday": "Среда",
        "thursday": "Четверг",
        "friday": "Пятница",
        "saturday": "Суббота",
        "sunday": "Воскресенье",
    },
    "en": {
        "monday": "Monday",
        "tuesday": "Tuesday",
        "wednesday": "Wednesday",
        "thursday": "Thursday",
        "friday": "Friday",
        "saturday": "Saturday",
        "sunday": "Sunday",
    },
}

CATEGORY_NAMES = {
    "ru": {
        "salads": "Салаты",
        "soups": "Супы",
        "main_dishes": "Горячее",
        "side_dishes": "Гарниры",
        "beverages": "Напитки",
        "bread": "Хлеб",
        "set_lunch": "Комплексный обед",
    },
    "en": {
        "salads": "Salads",
        "soups": "Soups",
        "main_dishes": "Main dishes",
        "side_dishes": "Side dishes",
        "beverages": "Beverages",
        "bread": "Bread",
        "set_lunch": "Set lunch",
    },
}

CATEGORY_EMOJI = {
    "salads": "🥗",
    "soups": "🍲",
    "main_dishes": "🍗",
    "side_dishes": "🥔",
    "beverages": "🥤",
    "bread": "🍞",
    "set_lunch": "🍱",
}

TEXTS = {
    "ru": {
        "choose_language": "Выбери язык / Choose language",
        "language_saved_ru": "Язык сохранён: Русский",
        "language_saved_en": "Language saved: English",
        "welcome": (
            "👋 Привет! Я бот столовой *MATRIX*, твой главный помощник в навигации! 🧭\n\n"
            "🍽 Помогу быстро посмотреть меню на сегодня\n"
            "📅 Покажу меню на неделю\n"
            "🌿 Найду постные блюда\n\n"
            "✨ Если нужно что-то найти, я всегда рядом!"
        ),
        "today_menu": "Сегодняшнее меню",
        "week_menu": "Меню на неделю",
        "fasting_menu": "Постное меню",
        "contacts": "Информация",
        "admin_panel": "Админ-панель",
        "change_language": "Сменить язык",
        "back": "Назад",
        "ingredients": "Ингредиенты",
        "choose_day": "Выбери день недели:",
        "choose_category": "Выбери категорию:",
        "no_menu_day": "На {day} меню пока не добавлено.",
        "menu_for_day": "🍽 Меню на {day}:\n\n",
        "fasting_title": "🌿 Постное меню:\n\n",
        "dish_not_found": "Блюдо не найдено.",
        "price": "💵 Цена",
        "weight": "⚖️ Вес",
        "calories": "🔥 КБЖУ",
        "ingredients_label": "🧾 Ингредиенты",
        "contacts_text": (
            "⏰ Режим работы: с 8:00 до 20:00, без выходных\n\n"
            "📍 Университетская, 1 (1-й этаж)\n\n"
            "Есть предложение? Пиши Шеф-повару @KborisoVa"
        ),
        "no_access": "У тебя нет доступа к админ-панели.",
        "admin_welcome": "Добро пожаловать в админ-панель.",
        "add_dish": "Добавить блюдо",
        "edit_dish": "Редактировать блюдо",
        "delete_dish": "Удалить блюдо",
        "hide_dish": "Скрыть блюдо",
        "admins": "Администраторы",
        "admin_home": "Главная",
        "add_admin": "Добавить администратора",
        "remove_admin": "Удалить администратора",
        "choose_admin_action": "Выбери действие с администраторами:",
        "current_admins": "Текущие администраторы:",
        "enter_admin_id": "Отправь Telegram ID пользователя.",
        "admin_id_invalid": "Неверный Telegram ID. Попробуй ещё раз.",
        "admin_added": "✅ Администратор добавлен.",
        "admin_removed": "✅ Администратор удалён.",
        "no_admins": "Список администраторов пока пуст.",
        "choose_day_admin": "Выбери день, с которым хочешь работать:",
        "choose_category_admin": "Выбери категорию:",
        "choose_dish_admin": "Выбери блюдо:",
        "choose_field_admin": "Что именно редактируем?",
        "edit_name_ru": "Название RU",
        "edit_name_en": "Название EN",
        "edit_price": "Цена",
        "edit_weight": "Вес",
        "edit_calories": "КБЖУ",
        "edit_ingredients_ru": "Ингредиенты RU",
        "edit_ingredients_en": "Ингредиенты EN",
        "enter_new_value": "Отправь новое значение.",
        "dish_hidden": "✅ Блюдо скрыто.",
        "dish_visible": "✅ Блюдо снова видно.",
        "dish_deleted": "✅ Блюдо удалено.",
        "dish_updated": "✅ Блюдо обновлено.",
        "unknown": "Я не понял сообщение. Выбери кнопку из меню.",
        "enter_day": "Напиши день недели на английском: monday, tuesday, wednesday, thursday, friday, saturday, sunday",
        "wrong_day": "Неверный день. Попробуй ещё раз.",
        "enter_category": "Напиши категорию: salads, soups, main_dishes, side_dishes, beverages, bread",
        "wrong_category": "Неверная категория. Попробуй ещё раз.",
        "enter_name_ru": "Введи название блюда на русском.",
        "enter_name_en": "Введи название блюда на английском.",
        "enter_price": "Введи цену. Например: 140 ₽",
        "enter_weight": "Введи вес. Например: 120 г",
        "enter_calories": "Введи калории/КБЖУ. Например: 104/4/9/2",
        "enter_ingredients_ru": "Введи ингредиенты на русском.",
        "enter_ingredients_en": "Введи ингредиенты на английском.",
        "dish_added": "✅ Блюдо добавлено в меню на {day} в категорию {category}.",
        "set_lunch_price": "Цена",
        "set_lunch_items": "Состав",
        "menu_file_info": "Сейчас используется файл menu.json. У всех дней меню категорийное.",
        "empty_category": "В этой категории пока нет блюд.",
    },
    "en": {
        "choose_language": "Choose language / Выбери язык",
        "language_saved_ru": "Language saved: Russian",
        "language_saved_en": "Language saved: English",
        "welcome": (
            "👋 Hello! I am the *MATRIX* cafeteria bot, your main navigation assistant! 🧭\n\n"
            "🍽 I can quickly show today's menu\n"
            "📅 I can show the weekly menu\n"
            "🌿 I can find the lenten dishes\n\n"
            "✨ If you need anything, I'm always here!"
        ),
        "today_menu": "Today's menu",
        "week_menu": "Weekly menu",
        "fasting_menu": "Lenten menu",
        "contacts": "Information",
        "admin_panel": "Admin panel",
        "change_language": "Change language",
        "back": "Back",
        "ingredients": "Ingredients",
        "choose_day": "Choose a day:",
        "choose_category": "Choose a category:",
        "no_menu_day": "No menu has been added for {day} yet.",
        "menu_for_day": "🍽 Menu for {day}:\n\n",
        "fasting_title": "🌿 Lenten menu:\n\n",
        "dish_not_found": "Dish not found.",
        "price": "💵 Price",
        "weight": "⚖️ Weight",
        "calories": "🔥 Calories",
        "ingredients_label": "🧾 Ingredients",
        "contacts_text": (
            "⏰ Opening hours: 8:00 to 20:00, every day\n\n"
            "📍 Universitetskaya, 1 (1st floor)\n\n"
            "Have a suggestion? Message the Chef: @KborisoVa"
        ),
        "no_access": "You do not have access to the admin panel.",
        "admin_welcome": "Welcome to the admin panel.",
        "add_dish": "Add dish",
        "edit_dish": "Edit dish",
        "delete_dish": "Delete dish",
        "hide_dish": "Hide dish",
        "admins": "Administrators",
        "admin_home": "Home",
        "add_admin": "Add administrator",
        "remove_admin": "Remove administrator",
        "choose_admin_action": "Choose an administrator action:",
        "current_admins": "Current administrators:",
        "enter_admin_id": "Send the Telegram ID.",
        "admin_id_invalid": "Invalid Telegram ID. Try again.",
        "admin_added": "✅ Administrator added.",
        "admin_removed": "✅ Administrator removed.",
        "no_admins": "No administrators yet.",
        "choose_day_admin": "Choose a day to work with:",
        "choose_category_admin": "Choose a category:",
        "choose_dish_admin": "Choose a dish:",
        "choose_field_admin": "What do you want to edit?",
        "edit_name_ru": "Name RU",
        "edit_name_en": "Name EN",
        "edit_price": "Price",
        "edit_weight": "Weight",
        "edit_calories": "Calories",
        "edit_ingredients_ru": "Ingredients RU",
        "edit_ingredients_en": "Ingredients EN",
        "enter_new_value": "Send the new value.",
        "dish_hidden": "✅ Dish hidden.",
        "dish_visible": "✅ Dish is visible again.",
        "dish_deleted": "✅ Dish deleted.",
        "dish_updated": "✅ Dish updated.",
        "unknown": "I did not understand the message. Please choose a button from the menu.",
        "enter_day": "Enter weekday in English: monday, tuesday, wednesday, thursday, friday, saturday, sunday",
        "wrong_day": "Wrong day. Try again.",
        "enter_category": "Enter category: salads, soups, main_dishes, side_dishes, beverages, bread",
        "wrong_category": "Wrong category. Try again.",
        "enter_name_ru": "Enter the dish name in Russian.",
        "enter_name_en": "Enter the dish name in English.",
        "enter_price": "Enter the price. Example: 140 ₽",
        "enter_weight": "Enter the weight. Example: 120 g",
        "enter_calories": "Enter calories/macros. Example: 104/4/9/2",
        "enter_ingredients_ru": "Enter ingredients in Russian.",
        "enter_ingredients_en": "Enter ingredients in English.",
        "dish_added": "✅ Dish added to {day}, category {category}.",
        "set_lunch_price": "Price",
        "set_lunch_items": "Items",
        "menu_file_info": "The bot uses menu.json. All days support category-based menus.",
        "empty_category": "This category has no dishes yet.",
    },
}

EDITABLE_CATEGORIES = [
    "salads",
    "soups",
    "main_dishes",
    "side_dishes",
    "beverages",
    "bread",
]

user_states = {}
nav_history = {}


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def create_users_file():
    if not os.path.exists(USERS_FILE):
        save_json(USERS_FILE, {})


def create_sample_menu():
    if os.path.exists(MENU_FILE):
        return

    sample_menu = {
        "monday": {
            "salads": [
                {
                    "name_ru": "Салат Наслаждение",
                    "name_en": "Salad Delight",
                    "price": "100 ₽",
                    "weight": "120 г",
                    "calories": "151/5/12/6",
                    "ingredients_ru": "Крабовое мясо, яйцо, помидоры, специи, майонез, чеснок",
                    "ingredients_en": "Crab meat, egg, tomatoes, spices, mayonnaise, garlic",
                },
                {
                    "name_ru": "Салат Сельдь под шубой",
                    "name_en": "Herring and Beet Salad",
                    "price": "70 ₽",
                    "weight": "120 г",
                    "calories": "198/7/15/7",
                    "ingredients_ru": "Картофель, морковь, сельдь, яйцо, майонез, свекла",
                    "ingredients_en": "Potatoes, carrots, herring, egg, mayonnaise, beetroot",
                },
                {
                    "name_ru": "Салат из свежих овощей и пастрами из индейки",
                    "name_en": "Fresh Vegetable Salad with Turkey Pastrami",
                    "price": "160 ₽",
                    "weight": "120 г",
                    "calories": "240/14/10/20",
                    "ingredients_ru": "Пастрами из индейки, помидоры черри, огурцы, салат айсберг, кукуруза, болгарский перец, мёд, растительное масло, лимонный сок",
                    "ingredients_en": "Turkey pastrami, cherry tomatoes, cucumbers, iceberg lettuce, corn, bell pepper, honey, vegetable oil, lemon juice",
                },
            ],
            "soups": [
                {
                    "name_ru": "Суп картофельный с куриными фрикадельками",
                    "name_en": "Potato Soup with Chicken Meatballs",
                    "price": "90 ₽",
                    "weight": "250 г",
                    "calories": "119/2/9/14",
                    "ingredients_ru": "Куриный бульон, курица, лук, морковь, специи, картофель",
                    "ingredients_en": "Chicken broth, chicken, onion, carrot, spices, potatoes",
                },
                {
                    "name_ru": "Борщ с курицей",
                    "name_en": "Borscht with Chicken",
                    "price": "105 ₽",
                    "weight": "250 г",
                    "calories": "210/10/12/14",
                    "ingredients_ru": "Куриный бульон, картофель, морковь, лук, свекла, томатная паста, специи",
                    "ingredients_en": "Chicken broth, potatoes, carrots, onion, beetroot, tomato paste, spices",
                },
            ],
            "main_dishes": [
                {
                    "name_ru": "Тефтели из курицы с рисом и соусом",
                    "name_en": "Chicken Meatballs with Rice and Sauce",
                    "price": "120 ₽",
                    "weight": "100/20 г",
                    "calories": "245/24/17/28",
                    "ingredients_ru": "Куриный фарш, рис, специи, растительное масло",
                    "ingredients_en": "Ground chicken, rice, spices, vegetable oil",
                },
                {
                    "name_ru": "Голень куриная гриль",
                    "name_en": "Grilled Chicken Drumstick",
                    "price": "100 ₽",
                    "weight": "100 г",
                    "calories": "245/24/17/28",
                    "ingredients_ru": "Куриные окорочка, специи, растительное масло, майонез, аджика, чеснок, уксус",
                    "ingredients_en": "Chicken legs, spices, vegetable oil, mayonnaise, adjika, garlic, vinegar",
                },
                {
                    "name_ru": "Куриная грудка с сыром и помидором",
                    "name_en": "Chicken Fillet with Cheese and Tomato",
                    "price": "140 ₽",
                    "weight": "100 г",
                    "calories": "228/30/8/6",
                    "ingredients_ru": "Куриное филе, сыр, помидор, яйцо, майонез, специи",
                    "ingredients_en": "Chicken fillet, cheese, tomato, egg, mayonnaise, spices",
                },
                {
                    "name_ru": "Наггетсы из свинины в имбирной панировке",
                    "name_en": "Pork Nuggets in Ginger Breading",
                    "price": "150 ₽",
                    "weight": "100 г",
                    "calories": "385/35/19/9",
                    "ingredients_ru": "Свинина, специи, панировочные сухари, имбирь, растительное масло",
                    "ingredients_en": "Pork, spices, breadcrumbs, ginger, vegetable oil",
                },
            ],
            "set_lunch": {
                "price": "330 ₽",
                "items": [
                    {"name_ru": "Салат Коктейль из овощей", "name_en": "Salad Cocktail of Vegetables", "calories": "95/2/5/9"},
                    {"name_ru": "Салат Сельдь под шубой", "name_en": "Herring and Beet Salad", "calories": "175/6/13/10"},
                    {"name_ru": "Суп картофельный с куриными фрикадельками", "name_en": "Potato Soup with Chicken Meatballs", "calories": "120/7/4/13"},
                    {"name_ru": "Суп-пюре из зелёного горошка", "name_en": "Green Pea Puree Soup", "calories": "110/5/4/14"},
                    {"name_ru": "Голень куриная гриль", "name_en": "Grilled Chicken Drumstick", "calories": "210/20/14/1"},
                    {"name_ru": "Тефтели из курицы с рисом и соусом", "name_en": "Chicken Meatballs with Rice and Sauce", "calories": "260/16/16/14"},
                    {"name_ru": "Булгур отварной", "name_en": "Boiled Bulgur", "calories": "120/3/2/22"},
                    {"name_ru": "Макароны отварные", "name_en": "Pasta", "calories": "150/5/3/28"},
                    {"name_ru": "Напиток на выбор / Хлеб", "name_en": "Drink of Choice / Bread", "calories": "60/2/1/10"},
                ],
            },
        },
        "tuesday": {
            "salads": [
                {
                    "name_ru": "Салат из редиса с огурцом и сметаной",
                    "name_en": "Radish Salad with Cucumber and Sour Cream",
                    "price": "90 ₽",
                    "weight": "120 г",
                    "calories": "143/2/10/11",
                    "ingredients_ru": "Зелёный лук, огурцы, редис, яйцо, сметана",
                    "ingredients_en": "Green onions, cucumbers, radishes, egg, sour cream",
                },
                {
                    "name_ru": "Салат Цезарь с курицей",
                    "name_en": "Caesar Salad with Chicken",
                    "price": "165 ₽",
                    "weight": "120 г",
                    "calories": "258/7/23/4",
                    "ingredients_ru": "Курица, айсберг, сыр, соус Цезарь, гренки, помидоры черри",
                    "ingredients_en": "Chicken, iceberg lettuce, cheese, Caesar sauce, croutons, cherry tomatoes",
                },
                {
                    "name_ru": "Салат Буковский",
                    "name_en": "Bukovsky Salad",
                    "price": "125 ₽",
                    "weight": "120 г",
                    "calories": "108/9/6/5",
                    "ingredients_ru": "Зелёный горошек, соус, капуста, лук, морковь, помидоры черри, яйцо, майонез",
                    "ingredients_en": "Green peas, sauce, cabbage, onion, carrot, cherry tomatoes, egg, mayonnaise",
                },
            ],
            "soups": [
                {
                    "name_ru": "Суп лапша с курицей",
                    "name_en": "Soup with Pasta and Chicken",
                    "price": "100 ₽",
                    "weight": "250 г",
                    "calories": "132/13/4/10",
                    "ingredients_ru": "Куриный бульон, курица, лук, морковь, специи, макароны",
                    "ingredients_en": "Chicken broth, chicken, onion, carrot, spices, pasta",
                },
                {
                    "name_ru": "Суп Норвежский",
                    "name_en": "Creamy Fish Soup",
                    "price": "135 ₽",
                    "weight": "250 г",
                    "calories": "164/10/6/16",
                    "ingredients_ru": "Рыба, сливки, картофель, лук, морковь, специи",
                    "ingredients_en": "Fish, cream, potatoes, onion, carrot, spices",
                },
            ],
            "main_dishes": [
                {
                    "name_ru": "Оладьи из печени",
                    "name_en": "Liver Pancakes",
                    "price": "105 ₽",
                    "weight": "100 г",
                    "calories": "260/12/11/14",
                    "ingredients_ru": "Печень, чеснок, мука, яйцо, масло, специи",
                    "ingredients_en": "Liver, garlic, flour, egg, butter, spices",
                },
                {
                    "name_ru": "Котлета куриная с ветчиной",
                    "name_en": "Chicken Cutlet with Ham",
                    "price": "100 ₽",
                    "weight": "100 г",
                    "calories": "262/17/19/3",
                    "ingredients_ru": "Курица, ветчина, молоко, хлеб, растительное масло",
                    "ingredients_en": "Chicken, ham, milk, bread, vegetable oil",
                },
                {
                    "name_ru": "Бефстроганов из индейки",
                    "name_en": "Turkey Stroganoff",
                    "price": "200 ₽",
                    "weight": "50/50 г",
                    "calories": "228/16/16/4",
                    "ingredients_ru": "Индейка, лук, шампиньоны, сливки, мука, специи, растительное масло",
                    "ingredients_en": "Turkey, onion, champignons, cream, flour, spices, vegetable oil",
                },
                {
                    "name_ru": "Рыба запечённая по-олимпийски с брокколи, цветной капустой и томатами",
                    "name_en": "Olympic-Style Baked Fish with Broccoli, Cauliflower and Tomatoes",
                    "price": "275 ₽",
                    "weight": "100 г",
                    "calories": "170/19/7/7",
                    "ingredients_ru": "Рыба, брокколи, цветная капуста, помидоры, сыр, майонез, растительное масло",
                    "ingredients_en": "Fish, broccoli, cauliflower, tomatoes, cheese, mayonnaise, vegetable oil",
                },
                {
                    "name_ru": "Жаркое по-домашнему со свининой",
                    "name_en": "Homemade Roast with Pork",
                    "price": "200 ₽",
                    "weight": "250 г",
                    "calories": "327/14/26/9",
                    "ingredients_ru": "Свинина, картофель, лук, морковь, специи, масло",
                    "ingredients_en": "Pork, potatoes, onion, carrot, spices, oil",
                },
            ],
            "set_lunch": {
                "price": "330 ₽",
                "items": [
                    {"name_ru": "Салат из моркови с грушей", "name_en": "Carrot and Pear Salad", "calories": "85/1/4/11"},
                    {"name_ru": "Салат из редиса с огурцом и сметаной", "name_en": "Radish Salad with Cucumber and Sour Cream", "calories": "80/2/5/7"},
                    {"name_ru": "Суп лапша с курицей", "name_en": "Soup with Pasta and Chicken", "calories": "125/7/4/15"},
                    {"name_ru": "Крем-суп овощной с гренками", "name_en": "Vegetable Cream Soup with Croutons", "calories": "100/3/4/13"},
                    {"name_ru": "Котлета куриная с ветчиной", "name_en": "Chicken Cutlet with Ham", "calories": "220/18/14/4"},
                    {"name_ru": "Оладьи из печени", "name_en": "Liver Pancakes", "calories": "190/12/11/8"},
                    {"name_ru": "Капуста тушеная", "name_en": "Stewed Cabbage", "calories": "95/2/4/12"},
                    {"name_ru": "Гречка", "name_en": "Buckwheat Porridge", "calories": "130/4/3/24"},
                    {"name_ru": "Напиток на выбор / Хлеб", "name_en": "Drink of Choice / Bread", "calories": "60/2/1/10"},
                ],
            },
        },
        "wednesday": {
            "salads": [
                {
                    "name_ru": "Салат из красной капусты с имбирными яблоками",
                    "name_en": "Red Cabbage Salad with Ginger Apples",
                    "price": "70 ₽",
                    "weight": "120 г",
                    "calories": "71/2/4/8",
                    "ingredients_ru": "Краснокочанная капуста, имбирь, яблоки, уксус, растительное масло, соль, сахар",
                    "ingredients_en": "Red cabbage, ginger, apples, vinegar, vegetable oil, salt, sugar",
                },
                {
                    "name_ru": "Салат Фунчоза с овощами",
                    "name_en": "Funchosa with Vegetables",
                    "price": "100 ₽",
                    "weight": "120 г",
                    "calories": "97/1/2/34",
                    "ingredients_ru": "Фунчоза, огурцы, морковь, помидор, масло",
                    "ingredients_en": "Funchosa, cucumbers, carrot, tomato, oil",
                },
            ],
            "soups": [
                {
                    "name_ru": "Рассольник с куриными фрикадельками",
                    "name_en": "Pickle Soup with Chicken Meatballs",
                    "price": "95 ₽",
                    "weight": "250 г",
                    "calories": "158/7/5/21",
                    "ingredients_ru": "Куриный бульон, солёные огурцы, перловка, морковь, лук, растительное масло, куриное филе, специи",
                    "ingredients_en": "Chicken broth, pickled cucumbers, pearl barley, carrot, onion, vegetable oil, chicken fillet, spices",
                },
                {
                    "name_ru": "Щи из свежей капусты с курицей",
                    "name_en": "Cabbage Soup with Chicken",
                    "price": "115 ₽",
                    "weight": "250 г",
                    "calories": "127/3/7/12",
                    "ingredients_ru": "Куриный бульон, капуста, курица, картофель, лук, морковь, растительное масло, специи",
                    "ingredients_en": "Chicken broth, cabbage, chicken, potatoes, onion, carrot, vegetable oil, spices",
                },
            ],
            "main_dishes": [
                {
                    "name_ru": "Гуляш из сердца",
                    "name_en": "Braised Beef Heart with Vegetables",
                    "price": "140 ₽",
                    "weight": "50/50 г",
                    "calories": "200/15/12/9",
                    "ingredients_ru": "Сердце говяжье, морковь, лук, специи, томатная паста, мука",
                    "ingredients_en": "Beef heart, carrot, onion, spices, tomato paste, flour",
                },
                {
                    "name_ru": "Голень куриная запечённая",
                    "name_en": "Baked Chicken Drumstick",
                    "price": "100 ₽",
                    "weight": "100 г",
                    "calories": "245/24/17/28",
                    "ingredients_ru": "Куриная голень, специи, растительное масло, майонез, аджика, чеснок, уксус",
                    "ingredients_en": "Chicken drumstick, spices, vegetable oil, mayonnaise, adjika, garlic, vinegar",
                },
            ],
            "side_dishes": [
                {
                    "name_ru": "Рис отварной с мексиканскими овощами",
                    "name_en": "Boiled Rice with Mexican Vegetables",
                    "price": "55 ₽",
                    "weight": "150 г",
                    "calories": "229/4/7/27",
                    "ingredients_ru": "Рис, мексиканская смесь, специи, растительное масло",
                    "ingredients_en": "Rice, Mexican mix, spices, vegetable oil",
                },
                {
                    "name_ru": "Гречка",
                    "name_en": "Buckwheat Porridge",
                    "price": "30 ₽",
                    "weight": "150 г",
                    "calories": "300/8/6/52",
                    "ingredients_ru": "Крупа гречневая, соль, растительное масло",
                    "ingredients_en": "Buckwheat, salt, vegetable oil",
                },
                {
                    "name_ru": "Кускус жемчужный",
                    "name_en": "Pearl Couscous",
                    "price": "75 ₽",
                    "weight": "150 г",
                    "calories": "350/19/15/60",
                    "ingredients_ru": "Кускус, соль, вода, растительное масло",
                    "ingredients_en": "Couscous, salt, water, vegetable oil",
                },
                {
                    "name_ru": "Овощи на пару",
                    "name_en": "Steamed Vegetables",
                    "price": "120 ₽",
                    "weight": "150 г",
                    "calories": "152",
                    "ingredients_ru": "Овощи, специи",
                    "ingredients_en": "Vegetables, spices",
                },
            ],
            "beverages": [
                {
                    "name_ru": "Чай в ассортименте",
                    "name_en": "Tea in Assortment",
                    "price": "30 ₽",
                    "weight": "200 г",
                    "calories": "40",
                },
                {
                    "name_ru": "Кофе растворимый",
                    "name_en": "Instant Coffee",
                    "price": "35 ₽",
                    "weight": "200 г",
                    "calories": "16,3",
                },
                {
                    "name_ru": "Компот из свежих фруктов",
                    "name_en": "Fresh Fruit Compote",
                    "price": "45 ₽",
                    "weight": "200 г",
                    "calories": "32,3",
                },
            ],
            "bread": [
                {
                    "name_ru": "Пшеничный",
                    "name_en": "Wheat Bread",
                    "weight": "30 г",
                    "calories": "242",
                },
                {
                    "name_ru": "Хлеб Сельский",
                    "name_en": "Rye Bread",
                    "weight": "30 г",
                    "calories": "240",
                },
            ],
            "set_lunch": {
                "price": "330 ₽",
                "items": [
                    {"name_ru": "Салат Фунчоза с овощами", "name_en": "Funchosa with Vegetables", "calories": "130/3/4/20"},
                    {"name_ru": "Салат из красной капусты с имбирными яблоками", "name_en": "Red Cabbage Salad with Ginger Apples", "calories": "70/1/3/9"},
                    {"name_ru": "Рассольник с куриными фрикадельками", "name_en": "Pickle Soup with Chicken Meatballs", "calories": "130/7/5/15"},
                    {"name_ru": "Щи из свежей капусты с курицей", "name_en": "Cabbage Soup with Chicken", "calories": "115/8/4/12"},
                    {"name_ru": "Гуляш из сердца", "name_en": "Braised Beef Heart with Vegetables", "calories": "200/19/13/4"},
                    {"name_ru": "Голень куриная запечённая", "name_en": "Baked Chicken Drumstick", "calories": "210/20/14/1"},
                    {"name_ru": "Рис отварной с мексиканскими овощами", "name_en": "Boiled Rice with Mexican Vegetables", "calories": "140/3/4/25"},
                    {"name_ru": "Гречка", "name_en": "Buckwheat Porridge", "calories": "130/4/3/24"},
                    {"name_ru": "Напиток на выбор / Хлеб", "name_en": "Drink of Choice / Bread", "calories": "60/2/1/10"},
                ],
            },
        },
        "thursday": {
            "salads": [
                {
                    "name_ru": "Салат Крабовый",
                    "name_en": "Crab Salad",
                    "price": "90 ₽",
                    "weight": "120 г",
                    "calories": "151/5/12/6",
                    "ingredients_ru": "Крабовое мясо, рис, яйцо, огурец, специи, майонез, кукуруза консервированная",
                    "ingredients_en": "Crab meat, rice, egg, cucumber, spices, mayonnaise, canned corn",
                },
                {
                    "name_ru": "Салат Греческий",
                    "name_en": "Greek Salad",
                    "price": "155 ₽",
                    "weight": "120 г",
                    "calories": "173/4/16/5",
                    "ingredients_ru": "Помидоры, огурцы, перец болгарский, сыр фета, лук, растительное масло",
                    "ingredients_en": "Tomatoes, cucumbers, bell pepper, feta cheese, onion, vegetable oil",
                },
                {
                    "name_ru": "Салат куриный BBQ",
                    "name_en": "BBQ Chicken Salad",
                    "price": "140 ₽",
                    "weight": "120 г",
                    "calories": "95/8/2/10",
                    "ingredients_ru": "Айсберг, пекинская капуста, мёд, растительное масло, черри, соус барбекю, куриное филе, специи",
                    "ingredients_en": "Iceberg lettuce, Chinese cabbage, honey, vegetable oil, cherry tomatoes, barbecue sauce, chicken fillet, spices",
                },
            ],
            "soups": [
                {
                    "name_ru": "Суп лапша грибная",
                    "name_en": "Mushroom Noodle Soup",
                    "price": "115 ₽",
                    "weight": "250 г",
                    "calories": "132/13/4/10",
                    "ingredients_ru": "Грибной бульон, грибы, макароны, специи, лук",
                    "ingredients_en": "Mushroom broth, mushrooms, pasta, spices, onions",
                },
                {
                    "name_ru": "Свекольник с куриными фрикадельками",
                    "name_en": "Beetroot Soup with Chicken Meatballs",
                    "price": "100 ₽",
                    "weight": "250 г",
                    "calories": "172/10/6/19",
                    "ingredients_ru": "Свекла, картофель, лук, морковь, томатная паста, растительное масло, специи, курица",
                    "ingredients_en": "Beets, potatoes, onions, carrots, tomato paste, vegetable oil, spices, chicken",
                },
            ],
            "main_dishes": [
                {
                    "name_ru": "Котлета куриная",
                    "name_en": "Chicken Cutlet",
                    "price": "120 ₽",
                    "weight": "100 г",
                    "calories": "185/20/7/11",
                    "ingredients_ru": "Куриное филе, хлеб, специи, лук, сухари панировочные, растительное масло",
                    "ingredients_en": "Chicken fillet, bread, spices, onion, breadcrumbs, vegetable oil",
                },
                {
                    "name_ru": "Куриные желудочки и сердечки тушёные в сметанном соусе",
                    "name_en": "Chicken Ventricles and Hearts Stewed in Sour Cream Sauce",
                    "price": "110 ₽",
                    "weight": "50/50 г",
                    "calories": "260/19/16/8",
                    "ingredients_ru": "Куриные сердечки, желудки, сметана, специи, мука, лук",
                    "ingredients_en": "Chicken hearts, ventricles, sour cream, spices, flour, onions",
                },
                {
                    "name_ru": "Зразы мясные с грибами",
                    "name_en": "Zrazy Meat with Mushrooms",
                    "price": "210 ₽",
                    "weight": "100 г",
                    "calories": "230",
                    "ingredients_ru": "Говядина, свинина, шампиньоны, лук, сухари панировочные, растительное масло",
                    "ingredients_en": "Beef, pork, champignons, onion, breadcrumbs, vegetable oil",
                },
                {
                    "name_ru": "Рулетик куриный с беконом",
                    "name_en": "Chicken Roll with Bacon",
                    "price": "200 ₽",
                    "weight": "100 г",
                    "calories": "240",
                    "ingredients_ru": "Куриное филе, бекон, сыр творожный, зелень, растительное масло",
                    "ingredients_en": "Chicken fillet, bacon, cream cheese, herbs, vegetable oil",
                },
                {
                    "name_ru": "Рыба запечённая по-олимпийски",
                    "name_en": "Olympic-Style Baked Fish",
                    "price": "275 ₽",
                    "weight": "100 г",
                    "calories": "300/21/23/2",
                    "ingredients_ru": "Рыба, брокколи, цветная капуста, помидор, сыр, майонез, растительное масло",
                    "ingredients_en": "Fish, broccoli, cauliflower, tomato, cheese, mayonnaise, vegetable oil",
                },
            ],
            "side_dishes": [
                {
                    "name_ru": "Картофельное пюре",
                    "name_en": "Mashed Potatoes",
                    "price": "60 ₽",
                    "weight": "150 г",
                    "calories": "157/4/6/23",
                    "ingredients_ru": "Картофель, молоко, соль, масло сливочное",
                    "ingredients_en": "Potatoes, milk, salt, butter",
                },
                {
                    "name_ru": "Фриттата из овощей",
                    "name_en": "Vegetable Frittata",
                    "price": "140 ₽",
                    "weight": "150 г",
                    "calories": "157/4/6/23",
                    "ingredients_ru": "Брокколи, яйца, молоко, соль, перец",
                    "ingredients_en": "Broccoli, eggs, milk, salt, pepper",
                },
            ],
            "set_lunch": {
                "price": "330 ₽",
                "items": [
                    {"name_ru": "Салат Крабовый", "name_en": "Crab Salad", "calories": "160/7/10/11"},
                    {"name_ru": "Салат Раджа", "name_en": "Raja Salad", "calories": "150/6/9/10"},
                    {"name_ru": "Суп лапша грибная", "name_en": "Mushroom Noodle Soup", "calories": "110/4/4/15"},
                    {"name_ru": "Свекольник с куриными фрикадельками", "name_en": "Beetroot Soup with Chicken Meatballs", "calories": "120/7/5/12"},
                    {"name_ru": "Котлета куриная", "name_en": "Chicken Cutlet", "calories": "220/18/14/5"},
                    {"name_ru": "Куриные желудочки и сердечки тушёные в сметанном соусе", "name_en": "Chicken Ventricles and Hearts Stewed in Sour Cream Sauce", "calories": "190/17/12/3"},
                    {"name_ru": "Картофельное пюре", "name_en": "Mashed Potatoes", "calories": "130/3/5/20"},
                    {"name_ru": "Макароны отварные", "name_en": "Pasta", "calories": "150/5/3/28"},
                    {"name_ru": "Напиток на выбор / Хлеб", "name_en": "Drink of Choice / Bread", "calories": "60/2/1/10"},
                ],
            },
        },
        "friday": {
            "salads": [
                {
                    "name_ru": "Салат Столичный",
                    "name_en": "Capital Salad",
                    "price": "95 ₽",
                    "weight": "120 г",
                    "calories": "104/4/9/2",
                    "ingredients_ru": "Картофель, морковь, зелёный горошек, курица, огурец, майонез",
                    "ingredients_en": "Potatoes, carrot, green peas, chicken, cucumber, mayonnaise",
                },
                {
                    "name_ru": "Салат Мимоза",
                    "name_en": "Mimosa Salad",
                    "price": "100 ₽",
                    "weight": "120 г",
                    "calories": "228/11/17/6",
                    "ingredients_ru": "Картофель, морковь, яйца, сыр, майонез",
                    "ingredients_en": "Potatoes, carrot, eggs, cheese, mayonnaise",
                },
                {
                    "name_ru": "Салат куриный BBQ",
                    "name_en": "BBQ Chicken Salad",
                    "price": "140 ₽",
                    "weight": "120 г",
                    "calories": "158/9/8/12",
                    "ingredients_ru": "Курица, салат, соус BBQ, овощи",
                    "ingredients_en": "Chicken, lettuce, BBQ sauce, vegetables",
                },
            ],
            "soups": [
                {
                    "name_ru": "Суп чесночный со свининой",
                    "name_en": "Czech Garlic Soup with Pork",
                    "price": "95 ₽",
                    "weight": "250 г",
                    "calories": "117/3/7/12",
                    "ingredients_ru": "Свинина, чеснок, картофель, специи",
                    "ingredients_en": "Pork, garlic, potatoes, spices",
                },
                {
                    "name_ru": "Щи из свежей капусты с говядиной",
                    "name_en": "Cabbage Soup with Beef",
                    "price": "140 ₽",
                    "weight": "250 г",
                    "calories": "244/10/17/12",
                    "ingredients_ru": "Капуста, говядина, картофель, морковь, лук",
                    "ingredients_en": "Cabbage, beef, potatoes, carrot, onion",
                },
            ],
            "main_dishes": [
                {
                    "name_ru": "Голень куриная гриль",
                    "name_en": "Grilled Chicken Drumstick",
                    "price": "100 ₽",
                    "weight": "100 г",
                    "calories": "245/24/17/28",
                    "ingredients_ru": "Курица, специи, масло",
                    "ingredients_en": "Chicken, spices, oil",
                },
                {
                    "name_ru": "Котлета куриная с картофелем",
                    "name_en": "Chicken Cutlet with Potatoes",
                    "price": "135 ₽",
                    "weight": "100 г",
                    "calories": "230/14/17/6",
                    "ingredients_ru": "Куриный фарш, картофель, специи",
                    "ingredients_en": "Chicken mince, potatoes, spices",
                },
                {
                    "name_ru": "Котлета из горбуши",
                    "name_en": "Pink Salmon Cutlet",
                    "price": "200 ₽",
                    "weight": "100 г",
                    "calories": "285/19/17/14",
                    "ingredients_ru": "Горбуша, хлеб, специи",
                    "ingredients_en": "Pink salmon, bread, spices",
                },
                {
                    "name_ru": "Гуляш из говядины",
                    "name_en": "Beef Goulash",
                    "price": "180 ₽",
                    "weight": "100 г",
                    "calories": "196/11/13/8",
                    "ingredients_ru": "Говядина, лук, томат, специи",
                    "ingredients_en": "Beef, onion, tomato, spices",
                },
                {
                    "name_ru": "Бефстроганов из индейки",
                    "name_en": "Turkey Stroganoff",
                    "price": "200 ₽",
                    "weight": "50/50 г",
                    "calories": "228/16/16/4",
                    "ingredients_ru": "Индейка, грибы, сливки, лук",
                    "ingredients_en": "Turkey, mushrooms, cream, onion",
                },
            ],
            "set_lunch": {
                "price": "330 ₽",
                "items": [
                    {"name_ru": "Салат Светофор", "name_en": "Traffic Light Salad", "calories": "80/1/4/10"},
                    {"name_ru": "Салат Столичный", "name_en": "Capital Salad", "calories": "65/1/3/8"},
                    {"name_ru": "Суп чесночный", "name_en": "Garlic Soup", "calories": "110/4/4/14"},
                    {"name_ru": "Суп Боб чорба", "name_en": "Bean Chorba Soup", "calories": "95/5/3/12"},
                    {"name_ru": "Котлета куриная", "name_en": "Chicken Cutlet", "calories": "180/17/10/5"},
                    {"name_ru": "Голень куриная", "name_en": "Chicken Drumstick", "calories": "210/20/14/1"},
                    {"name_ru": "Картофель по-деревенски", "name_en": "Rustic Potatoes", "calories": "130/3/5/20"},
                    {"name_ru": "Гороховое пюре", "name_en": "Pea Mash", "calories": "90/4/3/12"},
                    {"name_ru": "Хлеб / Напиток", "name_en": "Bread / Drink", "calories": "60/2/1/10"},
                ],
            },
        },
        "saturday": {
            "salads": [
                {
                    "name_ru": "Салат с курицей и ананасом",
                    "name_en": "Salad with Chicken and Pineapple",
                    "price": "150 ₽",
                    "weight": "120 г",
                    "calories": "240/14/10/20",
                    "ingredients_ru": "Куриное филе, салат айсберг, гренки, чесночный соус, ананас, сыр",
                    "ingredients_en": "Chicken fillet, iceberg lettuce, croutons, garlic sauce, pineapple, cheese",
                },
                {
                    "name_ru": "Салат Мимоза",
                    "name_en": "Mimosa Salad",
                    "price": "100 ₽",
                    "weight": "120 г",
                    "calories": "228/11/17/6",
                    "ingredients_ru": "Картофель, морковь, сыр, яйца, майонез, крабовое мясо, специи",
                    "ingredients_en": "Potatoes, carrots, cheese, eggs, mayonnaise, crab meat, spices",
                },
            ],
            "soups": [
                {
                    "name_ru": "Тайский овощной суп с омлетом",
                    "name_en": "Thai Vegetable Soup with Omelet",
                    "price": "80 ₽",
                    "weight": "250 г",
                    "calories": "158/16/28/12",
                    "ingredients_ru": "Пекинская капуста, лук, морковь, омлет, кинза, соевый соус, растительное масло",
                    "ingredients_en": "Chinese cabbage, onion, carrot, omelet, coriander, soy sauce, vegetable oil",
                },
                {
                    "name_ru": "Суп фасолевый с курицей",
                    "name_en": "Bean Soup with Chicken",
                    "price": "120 ₽",
                    "weight": "250 г",
                    "calories": "158/7/5/21",
                    "ingredients_ru": "Курица, картофель, морковь, лук, перловка, томатная паста, растительное масло, специи",
                    "ingredients_en": "Chicken, potatoes, carrots, onion, pearl barley, tomato paste, vegetable oil, spices",
                },
                {
                    "name_ru": "Суп куриный с чесночными галушками",
                    "name_en": "Chicken Soup with Garlic Dumplings",
                    "price": "110 ₽",
                    "weight": "250 г",
                    "calories": "201/10/7/25",
                    "ingredients_ru": "Куриный бульон, курица, картофель, морковь, лук, мука, яйцо, специи, растительное масло",
                    "ingredients_en": "Chicken broth, chicken, potatoes, carrots, onions, flour, egg, spices, vegetable oil",
                },
            ],
            "main_dishes": [
                {
                    "name_ru": "Оладьи из говяжьей печени",
                    "name_en": "Beef Liver Fritters",
                    "price": "150 ₽",
                    "weight": "100 г",
                    "calories": "260/12/11/14",
                    "ingredients_ru": "Печень говяжья, чеснок, мука, яйцо, масло, специи",
                    "ingredients_en": "Beef liver, garlic, flour, egg, butter, spices",
                },
                {
                    "name_ru": "Стожки с грибами",
                    "name_en": "Mushroom Racks",
                    "price": "120 ₽",
                    "weight": "100 г",
                    "calories": "131/17/2/12",
                    "ingredients_ru": "Куриное филе, грибы, лук, сыр, специи, растительное масло",
                    "ingredients_en": "Chicken fillet, mushrooms, onion, cheese, spices, vegetable oil",
                },
                {
                    "name_ru": "Гуляш из говядины",
                    "name_en": "Beef Goulash",
                    "price": "180 ₽",
                    "weight": "50/50 г",
                    "calories": "327/14/26/9",
                    "ingredients_ru": "Говядина, лук, морковь, томатная паста, растительное масло, специи, соль, мука",
                    "ingredients_en": "Beef, onion, carrot, tomato paste, vegetable oil, spices, salt, flour",
                },
                {
                    "name_ru": "Зразы куриные со шпинатом и яйцом",
                    "name_en": "Chicken Zrazy with Spinach and Egg",
                    "price": "140 ₽",
                    "weight": "100 г",
                    "calories": "300/16/19/15",
                    "ingredients_ru": "Куриное филе, лук, шпинат, молоко, специи, яйцо, сухари панировочные, масло сливочное",
                    "ingredients_en": "Chicken fillet, onion, spinach, milk, spices, egg, breadcrumbs, butter",
                },
                {
                    "name_ru": "Мойва в кляре",
                    "name_en": "Capelin in Batter",
                    "price": "150 ₽",
                    "weight": "150 г",
                    "calories": "292/21/22/3",
                    "ingredients_ru": "Мойва, мука, яйца, соль, растительное масло",
                    "ingredients_en": "Capelin, flour, eggs, salt, vegetable oil",
                },
            ],
            "side_dishes": [
                {
                    "name_ru": "Капуста тушёная со сметаной и кетчупом",
                    "name_en": "Stewed Cabbage with Sour Cream and Ketchup",
                    "price": "55 ₽",
                    "weight": "150 г",
                    "calories": "148/6/1/30",
                    "ingredients_ru": "Капуста, морковь, лук, масло, кетчуп, сметана, соль, мука, сахар",
                    "ingredients_en": "Cabbage, carrots, onions, oil, ketchup, sour cream, salt, flour, sugar",
                },
                {
                    "name_ru": "Фасоль стручковая с яйцом",
                    "name_en": "String Beans with Egg",
                    "price": "110 ₽",
                    "weight": "150 г",
                    "calories": "110",
                    "ingredients_ru": "Фасоль стручковая, соевый соус, яйцо, чеснок, растительное масло",
                    "ingredients_en": "Green beans, soy sauce, egg, garlic, vegetable oil",
                },
            ],
            "set_lunch": {
                "price": "330 ₽",
                "items": [
                    {"name_ru": "Салат из свеклы с имбирем", "name_en": "Beetroot and Ginger Salad", "calories": "80/1/4/9"},
                    {"name_ru": "Салат Ачичук", "name_en": "Achichuk Salad", "calories": "105/2/5/12"},
                    {"name_ru": "Суп фасолевый с курицей", "name_en": "Bean Soup with Chicken", "calories": "160/8/6/16"},
                    {"name_ru": "Тайский овощной суп с омлетом", "name_en": "Thai Vegetable Soup with Omelet", "calories": "180/8/10/12"},
                    {"name_ru": "Оладьи из говяжьей печени", "name_en": "Beef Liver Fritters", "calories": "120/10/6/6"},
                    {"name_ru": "Стожки с грибами", "name_en": "Mushroom Racks", "calories": "90/7/4/5"},
                    {"name_ru": "Гречка", "name_en": "Buckwheat Porridge", "calories": "140/4/3/26"},
                    {"name_ru": "Капуста тушёная со сметаной и кетчупом", "name_en": "Stewed Cabbage with Sour Cream and Ketchup", "calories": "130/3/6/14"},
                    {"name_ru": "Напиток на выбор / Хлеб", "name_en": "Drink of Choice / Bread", "calories": "60/2/1/10"},
                ],
            },
        },
        "sunday": {
            "salads": [
                {
                    "name_ru": "Салат Оливье",
                    "name_en": "Salad Olivier",
                    "price": "85 ₽",
                    "weight": "120 г",
                    "calories": "190/11/11/12",
                    "ingredients_ru": "Картофель, морковь, зелёный горошек, ветчина, огурец солёный, майонез",
                    "ingredients_en": "Potatoes, carrots, green peas, ham, pickled cucumber, mayonnaise",
                },
                {
                    "name_ru": "Салат Красное море",
                    "name_en": "Red Sea Salad",
                    "price": "105 ₽",
                    "weight": "120 г",
                    "calories": "151/5/12/6",
                    "ingredients_ru": "Помидор, крабовые палочки, болгарский перец, сыр, специи, зелень, майонез",
                    "ingredients_en": "Tomato, crab sticks, bell pepper, cheese, spices, herbs, mayonnaise",
                },
                {
                    "name_ru": "Салат Зелёный с ветчиной",
                    "name_en": "Green Salad with Ham",
                    "price": "75 ₽",
                    "weight": "120 г",
                    "calories": "121/3/8/9",
                    "ingredients_ru": "Картофель, ветчина, морковь, пекинская капуста, майонез, специи",
                    "ingredients_en": "Potatoes, ham, carrots, Chinese cabbage, mayonnaise, spices",
                },
            ],
            "soups": [
                {
                    "name_ru": "Суп картофельный с вермишелью и куриными фрикадельками",
                    "name_en": "Potato Soup with Noodles and Chicken Meatballs",
                    "price": "95 ₽",
                    "weight": "250 г",
                    "calories": "132/13/4/10",
                    "ingredients_ru": "Картофель, вермишель, морковь, лук, растительное масло, специи, курица",
                    "ingredients_en": "Potatoes, noodles, carrots, onions, vegetable oil, spices, chicken",
                },
                {
                    "name_ru": "Суп фасолевый с курицей",
                    "name_en": "Bean Soup with Chicken",
                    "price": "120 ₽",
                    "weight": "250 г",
                    "calories": "172/10/6/19",
                    "ingredients_ru": "Курица, картофель, лук, сельдерей, томат, морковь, фасоль, специи, масло",
                    "ingredients_en": "Chicken, potatoes, onion, celery, tomato, carrots, beans, spices, oil",
                },
                {
                    "name_ru": "Уха Ростовская",
                    "name_en": "Fish Soup “Rostovsky”",
                    "price": "130 ₽",
                    "weight": "250 г",
                    "calories": "164/10/6/16",
                    "ingredients_ru": "Рыба, картофель, лук, морковь, специи, растительное масло",
                    "ingredients_en": "Fish, potatoes, onion, carrots, spices, vegetable oil",
                },
            ],
            "main_dishes": [
                {
                    "name_ru": "Котлета куриная с грибами",
                    "name_en": "Chicken Cutlet with Mushrooms",
                    "price": "110 ₽",
                    "weight": "100 г",
                    "calories": "185/20/7/11",
                    "ingredients_ru": "Куриное филе, специи, хлеб, грибы, сушёные томаты, масло",
                    "ingredients_en": "Chicken fillet, spices, bread, mushrooms, sun-dried tomatoes, oil",
                },
                {
                    "name_ru": "Гуляш из курицы",
                    "name_en": "Chicken Goulash",
                    "price": "100 ₽",
                    "weight": "50/50 г",
                    "calories": "100/18/2/2",
                    "ingredients_ru": "Курица, лук, морковь, томатная паста, масло растительное, специи, соль, мука",
                    "ingredients_en": "Chicken, onion, carrots, tomato paste, vegetable oil, spices, salt, flour",
                },
                {
                    "name_ru": "Свинина по-восточному",
                    "name_en": "Pork in the Oriental Style",
                    "price": "195 ₽",
                    "weight": "50/50 г",
                    "calories": "400/21/31/12",
                    "ingredients_ru": "Свинина, лук, морковь, томатная паста, имбирь, растительное масло, специи",
                    "ingredients_en": "Pork, onion, carrot, tomato paste, ginger, vegetable oil, spices",
                },
                {
                    "name_ru": "Бедро куриное в сливочно-горчичном соусе",
                    "name_en": "Chicken Thighs in Creamy Mustard Sauce",
                    "price": "180 ₽",
                    "weight": "100 г",
                    "calories": "245/24/17/28",
                    "ingredients_ru": "Куриные бёдра, специи, горчица, сливки, растительное масло",
                    "ingredients_en": "Chicken thighs, spices, mustard, cream, vegetable oil",
                },
            ],
            "side_dishes": [
                {
                    "name_ru": "Картофельное пюре",
                    "name_en": "Mashed Potatoes",
                    "price": "60 ₽",
                    "weight": "150 г",
                    "calories": "157/4/6/23",
                    "ingredients_ru": "Картофель, молоко, соль, масло сливочное",
                    "ingredients_en": "Potatoes, milk, salt, butter",
                }
            ],
            "set_lunch": {
                "price": "330 ₽",
                "items": [
                    {"name_ru": "Салат Овощное здоровье", "name_en": "Vegetable Salad", "calories": "80/1/4/10"},
                    {"name_ru": "Салат Оливье", "name_en": "Salad Olivier", "calories": "105/2/6/10"},
                    {"name_ru": "Суп фасолевый с курицей", "name_en": "Bean Soup with Chicken", "calories": "160/8/6/16"},
                    {"name_ru": "Суп картофельный с вермишелью и куриными фрикадельками", "name_en": "Potato Soup with Noodles and Chicken Meatballs", "calories": "180/8/7/18"},
                    {"name_ru": "Котлета куриная с грибами", "name_en": "Chicken Cutlet with Mushrooms", "calories": "120/10/6/4"},
                    {"name_ru": "Гуляш из курицы", "name_en": "Chicken Goulash", "calories": "90/7/4/6"},
                    {"name_ru": "Гороховое пюре", "name_en": "Pea Mash", "calories": "140/5/4/22"},
                    {"name_ru": "Гречка", "name_en": "Buckwheat Porridge", "calories": "130/4/3/24"},
                    {"name_ru": "Напиток на выбор / Хлеб", "name_en": "Drink of Choice / Bread", "calories": "60/2/1/10"},
                ],
            },
        },
        "fasting_menu": [
            {
                "name_ru": "Салат Светофор",
                "name_en": "Traffic Light Salad",
                "price": "95 ₽",
                "weight": "120 г",
                "calories": "135/3/5/12",
                "ingredients_ru": "Огурец, болгарский перец, морковь, листья салата, растительное масло",
                "ingredients_en": "Cucumber, bell pepper, carrot, lettuce, vegetable oil",
            },
            {
                "name_ru": "Суп Боб чорба овощной",
                "name_en": "Bean Chorba Vegetable Soup",
                "price": "95 ₽",
                "weight": "250 г",
                "calories": "194/9/6/26",
                "ingredients_ru": "Фасоль, сельдерей, морковь, томат, специи",
                "ingredients_en": "Beans, celery, carrot, tomato, spices",
            },
            {
                "name_ru": "Хайгеты из соевого фарша",
                "name_en": "Soy Mince Nuggets",
                "price": "260 ₽",
                "weight": "100 г",
                "calories": "339/10/18/32",
                "ingredients_ru": "Соевый фарш, панировка, специи, растительное масло",
                "ingredients_en": "Soy mince, breading, spices, vegetable oil",
            },
            {
                "name_ru": "Картофель по-деревенски",
                "name_en": "Rustic Potatoes",
                "price": "50 ₽",
                "weight": "150 г",
                "calories": "282/5/15/32",
                "ingredients_ru": "Картофель, растительное масло, специи",
                "ingredients_en": "Potatoes, vegetable oil, spices",
            },
            {
                "name_ru": "Горошек на пару",
                "name_en": "Pea Mash",
                "price": "30 ₽",
                "weight": "150 г",
                "calories": "271/15/10/31",
                "ingredients_ru": "Горох, масло, специи",
                "ingredients_en": "Peas, oil, spices",
            },
            {
                "name_ru": "Рагу из овощей",
                "name_en": "Vegetable Ragout",
                "price": "70 ₽",
                "weight": "150 г",
                "calories": "282/5/15/32",
                "ingredients_ru": "Кабачки, морковь, картофель, лук, масло, специи",
                "ingredients_en": "Zucchini, carrot, potatoes, onion, oil, spices",
            },
            {
                "name_ru": "Рис с мексиканскими овощами",
                "name_en": "Rice with Mexican Vegetables",
                "price": "55 ₽",
                "weight": "150 г",
                "calories": "229/4/7/27",
                "ingredients_ru": "Рис, овощная смесь, масло, специи",
                "ingredients_en": "Rice, vegetable mix, oil, spices",
            },
        ],
    }

    save_json(MENU_FILE, sample_menu)
    print(f"Created {MENU_FILE}")


def load_menu():
    return load_json(MENU_FILE, {})


def save_menu(data):
    save_json(MENU_FILE, data)


def load_users():
    return load_json(USERS_FILE, {})


def save_users(data):
    save_json(USERS_FILE, data)


def set_user_language(user_id, lang):
    users = load_users()
    users[str(user_id)] = {"language": lang}
    save_users(users)


def get_user_language(user_id):
    users = load_users()
    return users.get(str(user_id), {}).get("language", "ru")


def t(user_id, key):
    lang = get_user_language(user_id)
    return TEXTS[lang][key]


def get_day_name(day_key, user_id):
    lang = get_user_language(user_id)
    return DAY_NAMES[lang][day_key]


def get_category_name(category, user_id):
    lang = get_user_language(user_id)
    return CATEGORY_NAMES[lang].get(category, category)


def get_dish_name(dish, user_id):
    lang = get_user_language(user_id)
    return dish.get(f"name_{lang}", dish.get("name_ru", dish.get("name", "Без названия")))


def get_dish_ingredients(dish, user_id):
    lang = get_user_language(user_id)
    return dish.get(f"ingredients_{lang}", dish.get("ingredients_ru", dish.get("ingredients", "—")))


def load_admin_ids():
    data = load_json(ADMINS_FILE, [])
    if not isinstance(data, list):
        return []
    return [str(item).strip() for item in data if str(item).strip()]


def save_admin_ids(admin_ids):
    unique_ids = []
    for admin_id in admin_ids:
        admin_id_str = str(admin_id).strip()
        if admin_id_str and admin_id_str not in unique_ids:
            unique_ids.append(admin_id_str)
    save_json(ADMINS_FILE, unique_ids)


def get_all_admin_ids():
    admin_ids = load_admin_ids()
    if ADMIN_ID:
        admin_ids.append(ADMIN_ID.strip())
    unique_ids = []
    for admin_id in admin_ids:
        if admin_id not in unique_ids:
            unique_ids.append(admin_id)
    return unique_ids


def _normalize_day_data(day_data):
    if isinstance(day_data, dict):
        return day_data
    return {}


def _get_admin_category_items(menu_data, day_key, category):
    day_data = _normalize_day_data(menu_data.get(day_key))
    if category == "set_lunch":
        set_lunch = day_data.get("set_lunch", {})
        if not isinstance(set_lunch, dict):
            return []
        return set_lunch.get("items", [])
    return day_data.get(category, [])


def _set_admin_category_items(menu_data, day_key, category, items):
    if day_key not in menu_data or not isinstance(menu_data.get(day_key), dict):
        menu_data[day_key] = {}
    if category == "set_lunch":
        if "set_lunch" not in menu_data[day_key] or not isinstance(menu_data[day_key].get("set_lunch"), dict):
            menu_data[day_key]["set_lunch"] = {"price": "330 ₽", "items": []}
        menu_data[day_key]["set_lunch"]["items"] = items
    else:
        menu_data[day_key][category] = items


def _dish_label(dish, user_id):
    label = get_dish_name(dish, user_id)
    if dish.get("hidden"):
        label += " [скрыто]"
    return label


def _visible_items(items):
    if not isinstance(items, list):
        return []
    return [item for item in items if not item.get("hidden")]


def set_nav_root(user_id, screen_token):
    nav_history[user_id] = [screen_token]


def push_nav(user_id, screen_token):
    stack = nav_history.setdefault(user_id, [])
    if not stack:
        stack.append(screen_token)
    elif stack[-1] != screen_token:
        stack.append(screen_token)


def pop_nav(user_id):
    stack = nav_history.setdefault(user_id, ["main"])
    if len(stack) > 1:
        stack.pop()
    return stack[-1]


def main_keyboard(user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(user_id, "today_menu"), callback_data="today_menu")],
            [InlineKeyboardButton(text=t(user_id, "week_menu"), callback_data="week_menu")],
            [InlineKeyboardButton(text=t(user_id, "fasting_menu"), callback_data="fasting_menu")],
            [InlineKeyboardButton(text=t(user_id, "contacts"), callback_data="contacts")],
            [InlineKeyboardButton(text=t(user_id, "change_language"), callback_data="change_language")],
            [InlineKeyboardButton(text=t(user_id, "admin_panel"), callback_data="admin_panel")],
        ],
    )


def admin_keyboard(user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(user_id, "add_dish"), callback_data="admin:add_dish")],
            [InlineKeyboardButton(text=t(user_id, "edit_dish"), callback_data="admin:edit_dish")],
            [InlineKeyboardButton(text=t(user_id, "delete_dish"), callback_data="admin:delete_dish")],
            [InlineKeyboardButton(text=t(user_id, "hide_dish"), callback_data="admin:hide_dish")],
            [InlineKeyboardButton(text=t(user_id, "admins"), callback_data="admin:admins")],
            [InlineKeyboardButton(text=t(user_id, "admin_home"), callback_data="admin:home")],
        ],
    )


def build_admin_days_keyboard(user_id, callback_prefix, back_callback="admin:back"):
    rows = [
        [InlineKeyboardButton(text=DAY_NAMES[get_user_language(user_id)][day], callback_data=f"{callback_prefix}:{day}")]
        for day in DAY_ORDER
    ]
    rows.append([InlineKeyboardButton(text=t(user_id, "back"), callback_data=back_callback)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_admin_categories_keyboard(user_id, day_key, callback_prefix, back_callback="admin:back"):
    categories = ["salads", "soups", "main_dishes", "side_dishes", "beverages", "bread", "set_lunch"]
    rows = []
    for category in categories:
        rows.append([
            InlineKeyboardButton(
                text=f"{CATEGORY_EMOJI.get(category, '📌')} {get_category_name(category, user_id)}",
                callback_data=f"{callback_prefix}:{day_key}:{category}",
            )
        ])
    rows.append([InlineKeyboardButton(text=t(user_id, "back"), callback_data=back_callback)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_admin_dishes_keyboard(user_id, day_key, category, callback_prefix, back_callback="admin:back"):
    menu_data = load_menu()
    dishes = _get_admin_category_items(menu_data, day_key, category)
    rows = []
    for idx, dish in enumerate(dishes):
        rows.append([
            InlineKeyboardButton(
                text=f"{idx + 1}. {_dish_label(dish, user_id)}",
                callback_data=f"{callback_prefix}:{day_key}:{category}:{idx}",
            )
        ])
    rows.append([InlineKeyboardButton(text=t(user_id, "back"), callback_data=back_callback)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_admin_fields_keyboard(user_id, day_key, category, dish_index, back_callback="admin:back_to_dishes"):
    if category == "set_lunch":
        fields = [
            ("edit_name_ru", "name_ru"),
            ("edit_name_en", "name_en"),
            ("edit_calories", "calories"),
        ]
    else:
        fields = [
            ("edit_name_ru", "name_ru"),
            ("edit_name_en", "name_en"),
            ("edit_price", "price"),
            ("edit_weight", "weight"),
            ("edit_calories", "calories"),
            ("edit_ingredients_ru", "ingredients_ru"),
            ("edit_ingredients_en", "ingredients_en"),
        ]

    rows = [
        [
            InlineKeyboardButton(
                text=t(user_id, label_key),
                callback_data=f"admin:edit_field:{day_key}:{category}:{dish_index}:{field}",
            )
        ]
        for label_key, field in fields
    ]
    rows.append([InlineKeyboardButton(text=t(user_id, "back"), callback_data=back_callback)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_admin_confirm_keyboard(yes_callback, no_callback, user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data=yes_callback),
                InlineKeyboardButton(text="❌ Нет", callback_data=no_callback),
            ],
            [InlineKeyboardButton(text=t(user_id, "back"), callback_data=no_callback)],
        ]
    )


def language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Русский", callback_data="set_lang:ru"),
                InlineKeyboardButton(text="English", callback_data="set_lang:en"),
            ]
        ],
    )


def get_today_key():
    return DAY_ORDER[datetime.now().weekday()]


def get_day_categories(day_data):
    if not isinstance(day_data, dict):
        return []
    ordered = [
        "salads",
        "soups",
        "main_dishes",
        "side_dishes",
        "beverages",
        "bread",
        "set_lunch",
    ]
    categories = []
    for key in ordered:
        if key not in day_data:
            continue
        if key == "set_lunch":
            items = day_data.get("set_lunch", {}).get("items", [])
            if _visible_items(items):
                categories.append(key)
        else:
            if _visible_items(day_data.get(key, [])):
                categories.append(key)
    return categories


def build_day_menu_text(day_key, menu_data, user_id):
    day_name = get_day_name(day_key, user_id)
    day_data = menu_data.get(day_key)

    if not day_data:
        return t(user_id, "no_menu_day").format(day=day_name)

    if isinstance(day_data, dict):
        if not get_day_categories(day_data):
            return t(user_id, "no_menu_day").format(day=day_name)
        return f"{t(user_id, 'menu_for_day').format(day=day_name)}{t(user_id, 'choose_category')}"

    text = t(user_id, "menu_for_day").format(day=day_name)
    for i, dish in enumerate(day_data, start=1):
        text += f"{i}. {get_dish_name(dish, user_id)} — {dish.get('price', '—')}\n"
    return text


def build_back_keyboard(user_id, callback_data):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(user_id, "back"), callback_data=callback_data)]
        ]
    )


def build_week_keyboard(user_id):
    lang = get_user_language(user_id)
    rows = [
        [InlineKeyboardButton(text=DAY_NAMES[lang][day], callback_data=f"show_day:{day}")]
        for day in DAY_ORDER
    ]
    rows.append([InlineKeyboardButton(text=t(user_id, "back"), callback_data="nav:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_day_ingredients_keyboard(day_key, menu_data, user_id):
    day_data = menu_data.get(day_key, [])
    buttons = []

    if isinstance(day_data, list):
        for idx, dish in enumerate(_visible_items(day_data)):
            buttons.append([
                InlineKeyboardButton(
                    text=f"{t(user_id, 'ingredients')}: {get_dish_name(dish, user_id)}",
                    callback_data=f"ingredients:{day_key}:{idx}",
                )
            ])

    buttons.append([InlineKeyboardButton(text=t(user_id, "back"), callback_data="nav:back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None


def build_day_categories_keyboard(day_key, menu_data, user_id):
    day_data = menu_data.get(day_key, {})
    categories = get_day_categories(day_data)
    buttons = []

    for category in categories:
        emoji = CATEGORY_EMOJI.get(category, "📌")
        buttons.append([
            InlineKeyboardButton(
                text=f"{emoji} {get_category_name(category, user_id)}",
                callback_data=f"category:{day_key}:{category}",
            )
        ])

    buttons.append([InlineKeyboardButton(text=t(user_id, "back"), callback_data="nav:back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None


def build_category_items_keyboard(day_key, category, menu_data, user_id):
    day_data = menu_data.get(day_key, {})
    items = _visible_items(day_data.get(category, []))
    buttons = []

    if category == "set_lunch":
        return None

    for idx, dish in enumerate(items):
        buttons.append([
            InlineKeyboardButton(
                text=f"{t(user_id, 'ingredients')}: {get_dish_name(dish, user_id)}",
                callback_data=f"category_item:{day_key}:{category}:{idx}",
            )
        ])

    buttons.append([InlineKeyboardButton(text=t(user_id, "back"), callback_data="nav:back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None


def build_fasting_keyboard(menu_data, user_id):
    fasting_menu = menu_data.get("fasting_menu", [])
    buttons = []

    for idx, dish in enumerate(fasting_menu):
        buttons.append([
            InlineKeyboardButton(
                text=f"{t(user_id, 'ingredients')}: {get_dish_name(dish, user_id)}",
                callback_data=f"fasting_item:{idx}",
            )
        ])

    buttons.append([InlineKeyboardButton(text=t(user_id, "back"), callback_data="nav:back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None


async def render_main_menu(message, user_id, track=True):
    if track:
        push_nav(user_id, "main")
    await message.edit_text(
        t(user_id, "welcome"),
        reply_markup=main_keyboard(user_id),
    )


async def render_week_menu(message, user_id, track=True):
    if track:
        push_nav(user_id, "week")
    await message.edit_text(
        t(user_id, "choose_day"),
        reply_markup=build_week_keyboard(user_id),
    )


async def render_day_menu(message, day_key, user_id, track=True):
    if track:
        push_nav(user_id, f"day:{day_key}")
    menu_data = load_menu()
    day_data = menu_data.get(day_key)

    if isinstance(day_data, dict):
        await message.edit_text(
            build_day_menu_text(day_key, menu_data, user_id),
            reply_markup=build_day_categories_keyboard(day_key, menu_data, user_id),
        )
        return

    await message.edit_text(
        build_day_menu_text(day_key, menu_data, user_id),
        reply_markup=build_day_ingredients_keyboard(day_key, menu_data, user_id),
    )


async def render_category_menu(message, day_key, category, user_id, track=True):
    if track:
        push_nav(user_id, f"category:{day_key}:{category}")

    menu_data = load_menu()
    day_data = menu_data.get(day_key, {})
    items = _visible_items(day_data.get(category))

    if category == "set_lunch":
        set_lunch = day_data.get("set_lunch", {})
        lunch_items = _visible_items(set_lunch.get("items", []))
        response = f"{CATEGORY_EMOJI.get('set_lunch', '🍱')} {get_category_name('set_lunch', user_id)}\n"
        response += f"{t(user_id, 'set_lunch_price')}: {set_lunch.get('price', '—')}\n\n"
        response += f"{t(user_id, 'set_lunch_items')}:\n"
        lang = get_user_language(user_id)
        for item in lunch_items:
            response += (
                f"• {item.get(f'name_{lang}', item.get('name_ru', '—'))}\n"
                f"  {t(user_id, 'calories')}: {item.get('calories', '—')}\n"
            )

        await message.edit_text(
            response,
            reply_markup=build_day_categories_keyboard(day_key, menu_data, user_id),
        )
        return

    if not items:
        await message.edit_text(
            t(user_id, "empty_category"),
            reply_markup=build_day_categories_keyboard(day_key, menu_data, user_id),
        )
        return

    title = get_category_name(category, user_id)
    response = f"{CATEGORY_EMOJI.get(category, '📌')} {title}:\n\n"
    for i, dish in enumerate(items, start=1):
        response += (
            f"{i}. {get_dish_name(dish, user_id)} — {dish.get('price', '—')}\n"
            f"   {t(user_id, 'weight')}: {dish.get('weight', '—')}\n"
            f"   {t(user_id, 'calories')}: {dish.get('calories', '—')}\n\n"
        )

    await message.edit_text(
        response,
        reply_markup=build_category_items_keyboard(day_key, category, menu_data, user_id),
    )


async def render_fasting_menu(message, user_id, track=True):
    if track:
        push_nav(user_id, "fasting")
    menu_data = load_menu()
    fasting_menu = _visible_items(menu_data.get("fasting_menu", []))

    if not fasting_menu:
        await message.edit_text(
            t(user_id, "no_menu_day").format(day=t(user_id, "fasting_menu")),
            reply_markup=main_keyboard(user_id),
        )
        return

    response = t(user_id, "fasting_title")
    for i, dish in enumerate(fasting_menu, start=1):
        response += (
            f"{i}. {get_dish_name(dish, user_id)} — {dish.get('price', '—')}\n"
            f"   {t(user_id, 'weight')}: {dish.get('weight', '—')}\n"
            f"   {t(user_id, 'calories')}: {dish.get('calories', '—')}\n\n"
        )

    await message.edit_text(
        response,
        reply_markup=build_fasting_keyboard(menu_data, user_id),
    )


async def render_screen_from_token(message, user_id, token):
    if token == "main":
        await render_main_menu(message, user_id, track=False)
        return

    if token == "today":
        today = get_today_key()
        await render_day_menu(message, today, user_id, track=False)
        return

    if token == "week":
        await render_week_menu(message, user_id, track=False)
        return

    if token == "fasting":
        await render_fasting_menu(message, user_id, track=False)
        return

    if token.startswith("day:"):
        _, day_key = token.split(":", 1)
        await render_day_menu(message, day_key, user_id, track=False)
        return

    if token.startswith("category:"):
        _, day_key, category = token.split(":", 2)
        await render_category_menu(message, day_key, category, user_id, track=False)
        return

    await render_main_menu(message, user_id, track=False)


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        t(message.from_user.id, "choose_language"),
        reply_markup=language_keyboard(),
    )


@dp.message(F.text == "Русский")
async def set_russian(message: Message):
    set_user_language(message.from_user.id, "ru")
    await message.answer(
        TEXTS["ru"]["language_saved_ru"],
        reply_markup=main_keyboard(message.from_user.id),
    )
    await message.answer(TEXTS["ru"]["welcome"])


@dp.message(F.text == "English")
async def set_english(message: Message):
    set_user_language(message.from_user.id, "en")
    await message.answer(
        TEXTS["en"]["language_saved_en"],
        reply_markup=main_keyboard(message.from_user.id),
    )
    await message.answer(TEXTS["en"]["welcome"])


@dp.message(F.text.in_(["Сменить язык", "Change language"]))
async def change_language_handler(message: Message):
    await message.answer(
        t(message.from_user.id, "choose_language"),
        reply_markup=language_keyboard(),
    )


@dp.callback_query(F.data == "set_lang:ru")
async def set_language_ru_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    set_user_language(user_id, "ru")
    set_nav_root(user_id, "main")
    await callback.message.edit_text(
        f"{TEXTS['ru']['language_saved_ru']}\n\n{TEXTS['ru']['welcome']}",
        reply_markup=main_keyboard(user_id),
    )
    await callback.answer()


@dp.callback_query(F.data == "set_lang:en")
async def set_language_en_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    set_user_language(user_id, "en")
    set_nav_root(user_id, "main")
    await callback.message.edit_text(
        f"{TEXTS['en']['language_saved_en']}\n\n{TEXTS['en']['welcome']}",
        reply_markup=main_keyboard(user_id),
    )
    await callback.answer()


@dp.callback_query(F.data == "today_menu")
async def today_menu_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    today = get_today_key()
    await render_day_menu(callback.message, today, user_id)
    await callback.answer()


@dp.callback_query(F.data == "week_menu")
async def week_menu_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    await render_week_menu(callback.message, user_id)
    await callback.answer()


@dp.callback_query(F.data == "fasting_menu")
async def fasting_menu_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    await render_fasting_menu(callback.message, user_id)
    await callback.answer()


@dp.callback_query(F.data == "contacts")
async def contacts_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    push_nav(user_id, "contacts")
    await callback.message.edit_text(
        t(user_id, "contacts_text"),
        reply_markup=build_back_keyboard(user_id, "nav:back"),
    )
    await callback.answer()


@dp.callback_query(F.data == "change_language")
async def change_language_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.edit_text(
        t(user_id, "choose_language"),
        reply_markup=language_keyboard(),
    )
    await callback.answer()


@dp.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.message.edit_text(t(user_id, "no_access"), reply_markup=main_keyboard(user_id))
        await callback.answer()
        return

    user_states.pop(user_id, None)
    await callback.message.edit_text(
        t(user_id, "admin_welcome"),
        reply_markup=admin_keyboard(user_id),
    )
    await callback.answer()


@dp.callback_query(F.data == "admin:back")
async def admin_back_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_states.pop(user_id, None)
    await callback.message.edit_text(
        t(user_id, "admin_welcome"),
        reply_markup=admin_keyboard(user_id),
    )
    await callback.answer()


@dp.callback_query(F.data == "admin:home")
async def admin_home_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.message.edit_text(t(user_id, "no_access"), reply_markup=main_keyboard(user_id))
        await callback.answer()
        return

    user_states.pop(user_id, None)
    await callback.message.edit_text(t(user_id, "welcome"), reply_markup=main_keyboard(user_id))
    await callback.answer()


@dp.callback_query(F.data == "admin:add_dish")
async def admin_add_dish_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.message.edit_text(t(user_id, "no_access"), reply_markup=main_keyboard(user_id))
        await callback.answer()
        return

    user_states[user_id] = {"step": "waiting_day"}
    await callback.message.edit_text(t(user_id, "enter_day"), reply_markup=build_back_keyboard(user_id, "admin:back"))
    await callback.answer()


@dp.callback_query(F.data == "admin:admins")
async def admin_admins_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.message.edit_text(t(user_id, "no_access"), reply_markup=main_keyboard(user_id))
        await callback.answer()
        return

    user_states.pop(user_id, None)
    admin_ids = [admin_id for admin_id in get_all_admin_ids()]
    lines = [t(user_id, "choose_admin_action")]
    if admin_ids:
        lines.append("")
        lines.append(t(user_id, "current_admins"))
        for admin_id in admin_ids:
            suffix = " (главный)" if ADMIN_ID and admin_id == ADMIN_ID.strip() else ""
            lines.append(f"• `{admin_id}`{suffix}")
    else:
        lines.append("")
        lines.append(t(user_id, "no_admins"))

    rows = [
        [InlineKeyboardButton(text=t(user_id, "add_admin"), callback_data="admin:add_admin")],
        [InlineKeyboardButton(text=t(user_id, "remove_admin"), callback_data="admin:remove_admin")],
        [InlineKeyboardButton(text=t(user_id, "back"), callback_data="admin:back")],
    ]
    await callback.message.edit_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="Markdown")
    await callback.answer()


@dp.callback_query(F.data == "admin:add_admin")
async def admin_add_admin_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.message.edit_text(t(user_id, "no_access"), reply_markup=main_keyboard(user_id))
        await callback.answer()
        return

    user_states[user_id] = {"step": "admin_waiting_id"}
    await callback.message.edit_text(
        t(user_id, "enter_admin_id"),
        reply_markup=build_back_keyboard(user_id, "admin:admins"),
    )
    await callback.answer()


@dp.callback_query(F.data == "admin:remove_admin")
async def admin_remove_admin_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.message.edit_text(t(user_id, "no_access"), reply_markup=main_keyboard(user_id))
        await callback.answer()
        return

    admin_ids = [admin_id for admin_id in load_admin_ids() if admin_id != (ADMIN_ID.strip() if ADMIN_ID else "")]
    if not admin_ids:
        await callback.message.edit_text(
            t(user_id, "no_admins"),
            reply_markup=build_back_keyboard(user_id, "admin:admins"),
        )
        await callback.answer()
        return

    rows = []
    for admin_id in admin_ids:
        rows.append([
            InlineKeyboardButton(
                text=admin_id,
                callback_data=f"admin:remove_admin_pick:{admin_id}",
            )
        ])
    rows.append([InlineKeyboardButton(text=t(user_id, "back"), callback_data="admin:admins")])
    await callback.message.edit_text(
        t(user_id, "choose_admin_action"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("admin:remove_admin_pick:"))
async def admin_remove_admin_pick_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.message.edit_text(t(user_id, "no_access"), reply_markup=main_keyboard(user_id))
        await callback.answer()
        return

    admin_id = callback.data.split(":", 2)[2]
    admin_ids = load_admin_ids()
    if admin_id in admin_ids:
        admin_ids.remove(admin_id)
        save_admin_ids(admin_ids)

    await callback.message.edit_text(
        t(user_id, "admin_removed"),
        reply_markup=admin_keyboard(user_id),
    )
    await callback.answer()


@dp.callback_query(F.data == "admin:edit_dish")
async def admin_edit_dish_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.message.edit_text(t(user_id, "no_access"), reply_markup=main_keyboard(user_id))
        await callback.answer()
        return

    user_states[user_id] = {"mode": "edit", "step": "choose_day"}
    await callback.message.edit_text(
        t(user_id, "choose_day_admin"),
        reply_markup=build_admin_days_keyboard(user_id, "admin:edit_day"),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("admin:edit_day:"))
async def admin_edit_day_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    day_key = callback.data.split(":", 2)[2]
    user_states[user_id] = {"mode": "edit", "step": "choose_category", "day": day_key}
    await callback.message.edit_text(
        t(user_id, "choose_category_admin"),
        reply_markup=build_admin_categories_keyboard(user_id, day_key, "admin:edit_category", back_callback="admin:edit_dish"),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("admin:edit_category:"))
async def admin_edit_category_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    _, _, day_key, category = callback.data.split(":", 3)
    user_states[user_id] = {"mode": "edit", "step": "choose_dish", "day": day_key, "category": category}
    await callback.message.edit_text(
        t(user_id, "choose_dish_admin"),
        reply_markup=build_admin_dishes_keyboard(
            user_id,
            day_key,
            category,
            "admin:edit_dish_pick",
            back_callback=f"admin:edit_day:{day_key}",
        ),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("admin:edit_dish_pick:"))
async def admin_edit_dish_pick_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    day_key = parts[2]
    category = parts[3]
    dish_index = int(parts[4])
    user_states[user_id] = {
        "mode": "edit",
        "step": "choose_field",
        "day": day_key,
        "category": category,
        "dish_index": dish_index,
    }
    await callback.message.edit_text(
        t(user_id, "choose_field_admin"),
        reply_markup=build_admin_fields_keyboard(
            user_id,
            day_key,
            category,
            dish_index,
            back_callback=f"admin:edit_category:{day_key}:{category}",
        ),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("admin:edit_field:"))
async def admin_edit_field_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    day_key = parts[2]
    category = parts[3]
    dish_index = int(parts[4])
    field = parts[5]

    menu = load_menu()
    dishes = _get_admin_category_items(menu, day_key, category)
    if not (0 <= dish_index < len(dishes)):
        await callback.message.edit_text(t(user_id, "dish_not_found"), reply_markup=admin_keyboard(user_id))
        await callback.answer()
        return

    user_states[user_id] = {
        "mode": "edit",
        "step": "waiting_value",
        "day": day_key,
        "category": category,
        "dish_index": dish_index,
        "field": field,
    }
    await callback.message.edit_text(
        t(user_id, "enter_new_value"),
        reply_markup=build_back_keyboard(user_id, f"admin:edit_dish_pick:{day_key}:{category}:{dish_index}"),
    )
    await callback.answer()


@dp.callback_query(F.data == "admin:back_to_categories")
async def admin_back_to_categories_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    state = user_states.get(user_id, {})
    day_key = state.get("day")
    mode = state.get("mode")
    if not day_key or mode not in {"edit", "delete", "hide"}:
        await callback.message.edit_text(t(user_id, "admin_welcome"), reply_markup=admin_keyboard(user_id))
        await callback.answer()
        return

    state["step"] = "choose_category"
    user_states[user_id] = state
    await callback.message.edit_text(
        t(user_id, "choose_category_admin"),
        reply_markup=build_admin_categories_keyboard(
            user_id,
            day_key,
            f"admin:{mode}_category",
            back_callback=f"admin:{mode}_dish" if mode != "edit" else "admin:edit_dish",
        ),
    )
    await callback.answer()


@dp.callback_query(F.data == "admin:back_to_dishes")
async def admin_back_to_dishes_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    state = user_states.get(user_id, {})
    day_key = state.get("day")
    category = state.get("category")
    mode = state.get("mode")
    if not day_key or not category or mode not in {"edit", "delete", "hide"}:
        await callback.message.edit_text(t(user_id, "admin_welcome"), reply_markup=admin_keyboard(user_id))
        await callback.answer()
        return

    state["step"] = "choose_dish"
    user_states[user_id] = state
    if mode == "edit":
        reply_markup = build_admin_dishes_keyboard(
            user_id,
            day_key,
            category,
            "admin:edit_dish_pick",
            back_callback=f"admin:edit_category:{day_key}:{category}",
        )
        text = t(user_id, "choose_dish_admin")
    else:
        reply_markup = build_admin_dishes_keyboard(
            user_id,
            day_key,
            category,
            f"admin:{mode}_dish_pick",
            back_callback=f"admin:{mode}_category:{day_key}:{category}",
        )
        text = t(user_id, "choose_dish_admin")

    await callback.message.edit_text(text, reply_markup=reply_markup)
    await callback.answer()


@dp.callback_query(F.data == "admin:delete_dish")
async def admin_delete_dish_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.message.edit_text(t(user_id, "no_access"), reply_markup=main_keyboard(user_id))
        await callback.answer()
        return

    user_states[user_id] = {"mode": "delete", "step": "choose_day"}
    await callback.message.edit_text(
        t(user_id, "choose_day_admin"),
        reply_markup=build_admin_days_keyboard(user_id, "admin:delete_day"),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("admin:delete_day:"))
async def admin_delete_day_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    day_key = callback.data.split(":", 2)[2]
    user_states[user_id] = {"mode": "delete", "step": "choose_category", "day": day_key}
    await callback.message.edit_text(
        t(user_id, "choose_category_admin"),
        reply_markup=build_admin_categories_keyboard(user_id, day_key, "admin:delete_category", back_callback="admin:delete_dish"),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("admin:delete_category:"))
async def admin_delete_category_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    _, _, day_key, category = callback.data.split(":", 3)
    user_states[user_id] = {"mode": "delete", "step": "choose_dish", "day": day_key, "category": category}
    await callback.message.edit_text(
        t(user_id, "choose_dish_admin"),
        reply_markup=build_admin_dishes_keyboard(
            user_id,
            day_key,
            category,
            "admin:delete_dish_pick",
            back_callback=f"admin:delete_day:{day_key}",
        ),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("admin:delete_dish_pick:"))
async def admin_delete_dish_pick_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    day_key = parts[2]
    category = parts[3]
    dish_index = int(parts[4])
    user_states[user_id] = {
        "mode": "delete",
        "step": "confirm_delete",
        "day": day_key,
        "category": category,
        "dish_index": dish_index,
    }
    await callback.message.edit_text(
        t(user_id, "choose_field_admin"),
        reply_markup=build_admin_confirm_keyboard(
            yes_callback=f"admin:confirm_delete:{day_key}:{category}:{dish_index}",
            no_callback="admin:back_to_dishes",
            user_id=user_id,
        ),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("admin:confirm_delete:"))
async def admin_confirm_delete_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    day_key = parts[2]
    category = parts[3]
    dish_index = int(parts[4])

    menu = load_menu()
    dishes = _get_admin_category_items(menu, day_key, category)
    if not (0 <= dish_index < len(dishes)):
        await callback.message.edit_text(t(user_id, "dish_not_found"), reply_markup=admin_keyboard(user_id))
        await callback.answer()
        return

    del dishes[dish_index]
    _set_admin_category_items(menu, day_key, category, dishes)
    save_menu(menu)

    user_states[user_id] = {"mode": "delete", "step": "choose_category", "day": day_key}
    await callback.message.edit_text(
        t(user_id, "dish_deleted"),
        reply_markup=build_admin_categories_keyboard(user_id, day_key, "admin:delete_category", back_callback="admin:delete_dish"),
    )
    await callback.answer()


@dp.callback_query(F.data == "admin:hide_dish")
async def admin_hide_dish_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.message.edit_text(t(user_id, "no_access"), reply_markup=main_keyboard(user_id))
        await callback.answer()
        return

    user_states[user_id] = {"mode": "hide", "step": "choose_day"}
    await callback.message.edit_text(
        t(user_id, "choose_day_admin"),
        reply_markup=build_admin_days_keyboard(user_id, "admin:hide_day"),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("admin:hide_day:"))
async def admin_hide_day_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    day_key = callback.data.split(":", 2)[2]
    user_states[user_id] = {"mode": "hide", "step": "choose_category", "day": day_key}
    await callback.message.edit_text(
        t(user_id, "choose_category_admin"),
        reply_markup=build_admin_categories_keyboard(user_id, day_key, "admin:hide_category", back_callback="admin:hide_dish"),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("admin:hide_category:"))
async def admin_hide_category_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    _, _, day_key, category = callback.data.split(":", 3)
    user_states[user_id] = {"mode": "hide", "step": "choose_dish", "day": day_key, "category": category}
    await callback.message.edit_text(
        t(user_id, "choose_dish_admin"),
        reply_markup=build_admin_dishes_keyboard(
            user_id,
            day_key,
            category,
            "admin:hide_dish_pick",
            back_callback=f"admin:hide_day:{day_key}",
        ),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("admin:hide_dish_pick:"))
async def admin_hide_dish_pick_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    day_key = parts[2]
    category = parts[3]
    dish_index = int(parts[4])

    menu = load_menu()
    dishes = _get_admin_category_items(menu, day_key, category)
    if not (0 <= dish_index < len(dishes)):
        await callback.message.edit_text(t(user_id, "dish_not_found"), reply_markup=admin_keyboard(user_id))
        await callback.answer()
        return

    dishes[dish_index]["hidden"] = not dishes[dish_index].get("hidden", False)
    _set_admin_category_items(menu, day_key, category, dishes)
    save_menu(menu)

    result_text = t(user_id, "dish_hidden") if dishes[dish_index]["hidden"] else t(user_id, "dish_visible")
    user_states[user_id] = {"mode": "hide", "step": "choose_dish", "day": day_key, "category": category}
    await callback.message.edit_text(
        result_text,
        reply_markup=build_admin_dishes_keyboard(
            user_id,
            day_key,
            category,
            "admin:hide_dish_pick",
            back_callback=f"admin:hide_category:{day_key}:{category}",
        ),
    )
    await callback.answer()


@dp.message()
async def universal_handler(message: Message):
    user_id = message.from_user.id
    text = message.text
    state = user_states.get(user_id)
    menu_data = load_menu()

    if text == t(user_id, "today_menu"):
        today = get_today_key()
        push_nav(user_id, f"day:{today}")
        day_data = menu_data.get(today)

        if isinstance(day_data, dict):
            await message.answer(
                build_day_menu_text(today, menu_data, user_id),
                reply_markup=build_day_categories_keyboard(today, menu_data, user_id),
            )
            return

        menu_text = build_day_menu_text(today, menu_data, user_id)
        keyboard = build_day_ingredients_keyboard(today, menu_data, user_id)
        await message.answer(menu_text, reply_markup=keyboard)
        return

    if text == t(user_id, "week_menu"):
        push_nav(user_id, "week")
        await message.answer(
            t(user_id, "choose_day"),
            reply_markup=build_week_keyboard(user_id),
        )
        return

    if text == t(user_id, "fasting_menu"):
        push_nav(user_id, "fasting")
        fasting_menu = menu_data.get("fasting_menu", [])
        if not fasting_menu:
            await message.answer(
                t(user_id, "no_menu_day").format(day=t(user_id, "fasting_menu"))
            )
            return

        response = t(user_id, "fasting_title")
        for i, dish in enumerate(fasting_menu, start=1):
            response += (
                f"{i}. {get_dish_name(dish, user_id)} — {dish.get('price', '—')}\n"
                f"   {t(user_id, 'weight')}: {dish.get('weight', '—')}\n"
                f"   {t(user_id, 'calories')}: {dish.get('calories', '—')}\n\n"
            )

        await message.answer(
            response,
            reply_markup=build_fasting_keyboard(menu_data, user_id),
        )
        return

    if text == t(user_id, "contacts"):
        push_nav(user_id, "contacts")
        await message.answer(t(user_id, "contacts_text"))
        return

    if text == t(user_id, "admin_panel"):
        if not is_admin(user_id):
            await message.answer(t(user_id, "no_access"))
            return

        await message.answer(
            t(user_id, "admin_welcome"),
            reply_markup=admin_keyboard(user_id),
        )
        return

    if text == t(user_id, "back"):
        user_states.pop(user_id, None)
        await message.answer(
            t(user_id, "welcome"),
            reply_markup=main_keyboard(user_id),
        )
        return

    if text == t(user_id, "view_menu"):
        if not is_admin(user_id):
            await message.answer(t(user_id, "no_access"))
            return

        await message.answer(t(user_id, "menu_file_info"))
        return

    if text == t(user_id, "add_dish"):
        if not is_admin(user_id):
            await message.answer(t(user_id, "no_access"))
            return

        user_states[user_id] = {"step": "waiting_day"}
        await message.answer(t(user_id, "enter_day"))
        return

    if state:
        step = state.get("step")

        if step == "admin_waiting_id":
            admin_id = text.strip()
            if not admin_id.isdigit():
                await message.answer(t(user_id, "admin_id_invalid"))
                return

            admin_ids = load_admin_ids()
            if admin_id not in admin_ids:
                admin_ids.append(admin_id)
                save_admin_ids(admin_ids)

            user_states.pop(user_id, None)
            await message.answer(
                t(user_id, "admin_added"),
                reply_markup=admin_keyboard(user_id),
            )
            return

        if step == "waiting_value":
            day = state.get("day")
            category = state.get("category")
            dish_index = state.get("dish_index")
            field = state.get("field")

            menu = load_menu()
            dishes = _get_admin_category_items(menu, day, category)
            if not (0 <= dish_index < len(dishes)):
                await message.answer(t(user_id, "dish_not_found"))
                user_states.pop(user_id, None)
                return

            dishes[dish_index][field] = text.strip()
            _set_admin_category_items(menu, day, category, dishes)
            save_menu(menu)

            user_states[user_id] = {
                "mode": "edit",
                "step": "choose_dish",
                "day": day,
                "category": category,
            }
            await message.answer(
                t(user_id, "dish_updated"),
                reply_markup=build_admin_dishes_keyboard(
                    user_id,
                    day,
                    category,
                    "admin:edit_dish_pick",
                    back_callback=f"admin:edit_category:{day}:{category}",
                ),
            )
            return

        if step == "waiting_day":
            day = text.strip().lower()
            if day not in DAY_ORDER:
                await message.answer(t(user_id, "wrong_day"))
                return

            state["day"] = day
            state["step"] = "waiting_category"
            await message.answer(t(user_id, "enter_category"))
            return

        if step == "waiting_category":
            category = text.strip().lower()
            if category not in EDITABLE_CATEGORIES:
                await message.answer(t(user_id, "wrong_category"))
                return

            state["category"] = category
            state["step"] = "waiting_name_ru"
            await message.answer(t(user_id, "enter_name_ru"))
            return

        if step == "waiting_name_ru":
            state["name_ru"] = text.strip()
            state["step"] = "waiting_name_en"
            await message.answer(t(user_id, "enter_name_en"))
            return

        if step == "waiting_name_en":
            state["name_en"] = text.strip()
            state["step"] = "waiting_price"
            await message.answer(t(user_id, "enter_price"))
            return

        if step == "waiting_price":
            state["price"] = text.strip()
            state["step"] = "waiting_weight"
            await message.answer(t(user_id, "enter_weight"))
            return

        if step == "waiting_weight":
            state["weight"] = text.strip()
            state["step"] = "waiting_calories"
            await message.answer(t(user_id, "enter_calories"))
            return

        if step == "waiting_calories":
            state["calories"] = text.strip()
            state["step"] = "waiting_ingredients_ru"
            await message.answer(t(user_id, "enter_ingredients_ru"))
            return

        if step == "waiting_ingredients_ru":
            state["ingredients_ru"] = text.strip()
            state["step"] = "waiting_ingredients_en"
            await message.answer(t(user_id, "enter_ingredients_en"))
            return

        if step == "waiting_ingredients_en":
            state["ingredients_en"] = text.strip()

            menu = load_menu()
            day = state["day"]
            category = state["category"]

            new_dish = {
                "name_ru": state["name_ru"],
                "name_en": state["name_en"],
                "price": state["price"],
                "weight": state["weight"],
                "calories": state["calories"],
                "ingredients_ru": state["ingredients_ru"],
                "ingredients_en": state["ingredients_en"],
            }

            if day not in menu or not isinstance(menu.get(day), dict):
                menu[day] = {
                    "salads": [],
                    "soups": [],
                    "main_dishes": [],
                    "side_dishes": [],
                    "beverages": [],
                    "bread": [],
                    "set_lunch": {"price": "330 ₽", "items": []},
                }

            if category not in menu[day] or not isinstance(menu[day][category], list):
                menu[day][category] = []

            menu[day][category].append(new_dish)
            save_menu(menu)
            user_states.pop(user_id, None)

            await message.answer(
                t(user_id, "dish_added").format(
                    day=get_day_name(day, user_id),
                    category=get_category_name(category, user_id),
                ),
                reply_markup=main_keyboard(user_id),
            )
            return

    await message.answer(t(user_id, "unknown"))


@dp.callback_query(F.data == "nav:back")
async def back_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    prev_token = pop_nav(user_id)
    await render_screen_from_token(callback.message, user_id, prev_token)

    await callback.answer()


@dp.callback_query(F.data.startswith("show_day:"))
async def show_day_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    day = callback.data.split(":")[1]
    await render_day_menu(callback.message, day, user_id)
    await callback.answer()


@dp.callback_query(F.data.startswith("ingredients:"))
async def ingredients_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    day = parts[1]
    idx = int(parts[2])

    menu_data = load_menu()
    dishes = _visible_items(menu_data.get(day, []))

    if 0 <= idx < len(dishes):
        dish = dishes[idx]
        push_nav(user_id, "detail")
        await callback.message.edit_text(
            f"{get_dish_name(dish, user_id)}\n"
            f"{t(user_id, 'price')}: {dish.get('price', '—')}\n"
            f"{t(user_id, 'weight')}: {dish.get('weight', '—')}\n"
            f"{t(user_id, 'calories')}: {dish.get('calories', '—')}\n"
            f"{t(user_id, 'ingredients_label')}: {get_dish_ingredients(dish, user_id)}",
            reply_markup=build_back_keyboard(user_id, "nav:back"),
        )
    else:
        push_nav(user_id, "detail")
        await callback.message.edit_text(
            t(user_id, "dish_not_found"),
            reply_markup=build_back_keyboard(user_id, "nav:back"),
        )

    await callback.answer()


@dp.callback_query(F.data.startswith("fasting_item:"))
async def fasting_item_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    idx = int(callback.data.split(":")[1])
    menu_data = load_menu()
    dishes = _visible_items(menu_data.get("fasting_menu", []))

    if 0 <= idx < len(dishes):
        dish = dishes[idx]
        push_nav(user_id, "detail")
        await callback.message.edit_text(
            f"{get_dish_name(dish, user_id)}\n"
            f"{t(user_id, 'price')}: {dish.get('price', '—')}\n"
            f"{t(user_id, 'weight')}: {dish.get('weight', '—')}\n"
            f"{t(user_id, 'calories')}: {dish.get('calories', '—')}\n"
            f"{t(user_id, 'ingredients_label')}: {get_dish_ingredients(dish, user_id)}",
            reply_markup=build_back_keyboard(user_id, "nav:back"),
        )
    else:
        push_nav(user_id, "detail")
        await callback.message.edit_text(
            t(user_id, "dish_not_found"),
            reply_markup=build_back_keyboard(user_id, "nav:back"),
        )

    await callback.answer()


@dp.callback_query(F.data.startswith("category:"))
async def category_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    day = parts[1]
    category = parts[2]
    await render_category_menu(callback.message, day, category, user_id)
    await callback.answer()


@dp.callback_query(F.data.startswith("category_item:"))
async def category_item_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    day = parts[1]
    category = parts[2]
    idx = int(parts[3])

    menu_data = load_menu()
    day_data = menu_data.get(day, {})
    dishes = _visible_items(day_data.get(category, []))

    if 0 <= idx < len(dishes):
        dish = dishes[idx]
        push_nav(user_id, "detail")
        await callback.message.edit_text(
            f"{get_dish_name(dish, user_id)}\n"
            f"{t(user_id, 'price')}: {dish.get('price', '—')}\n"
            f"{t(user_id, 'weight')}: {dish.get('weight', '—')}\n"
            f"{t(user_id, 'calories')}: {dish.get('calories', '—')}\n"
            f"{t(user_id, 'ingredients_label')}: {get_dish_ingredients(dish, user_id)}",
            reply_markup=build_back_keyboard(user_id, "nav:back"),
        )
    else:
        push_nav(user_id, "detail")
        await callback.message.edit_text(
            t(user_id, "dish_not_found"),
            reply_markup=build_back_keyboard(user_id, "nav:back"),
        )

    await callback.answer()


async def main():
    create_sample_menu()
    create_users_file()
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
