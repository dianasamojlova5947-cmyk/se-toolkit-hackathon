# Matrix Bot — Меню столовой

Telegram-бот для просмотра меню университетской столовой с поддержкой русского и английского языков, категориями блюд и админ-панелью.

## One-line Description

Умный Telegram-бот для навигации по меню столовой с поиском блюд, ингредиентами и админ-панелью.

## Demo

![Главное меню](docs/screenshots/main_menu.png)
![Меню на день](docs/screenshots/day_menu.png)
![Категории блюд](docs/screenshots/categories.png)

## Product Context

### End Users
- **Студенты и сотрудники университета** — основной пользователь, хочет быстро узнать что сегодня в столовой
- **Посетители столовой MATRIX** — хотят просмотреть меню, цены и ингредиенты до визита

### Problem
- Нет удобного способа узнать меню столовой без личного визита
- Студенты не знают актуальные цены и ингредиенты блюд
- Нет информации о постных опциях для постящихся
- Администрации нужен простой способ обновлять меню

### Solution
Telegram-бот с inline-клавиатурой:
- Автоматическое меню на сегодня по дню недели
- Категоризация блюд (салаты, супы, горячее, гарниры, напитки)
- Детальная информация о каждом блюде (цена, вес, калории, ингредиенты)
- Постное меню в отдельном разделе
- Мультиязычность (Русский / English)
- Админ-панель для управления меню через бота

## Features

### ✅ Implemented Features

**Version 1 (Core):**
- [x] Мультиязычность (Русский / English)
- [x] Меню на сегодня (автоопределение дня)
- [x] Меню на неделю по дням
- [x] Постное меню
- [x] Информация о блюдах (цена, вес, калории, ингредиенты)
- [x] Админ-панель с авторизацией

**Version 2 (Improvements):**
- [x] Категоризация блюд по типам (салаты, супы, горячее, гарниры, напитки, хлеб)
- [x] Комплексные обеды
- [x] Inline-навигация с кнопкой "Назад"
- [x] Многоуровневая навигация по меню
- [x] Расширенная информация о блюдах (калории, вес)
- [x] Двуязычные названия блюд
- [x] SQLite база данных
- [x] Docker-контейнеризация
- [x] Гибкая система админов через JSON-файл

### 🔜 Planned Features
- [ ] Уведомления о новом меню
- [ ] Поиск по блюдам
- [ ] Рейтинги и отзывы
- [ ] Web-версия

## Architecture

```
┌─────────────────┐
│   Telegram Bot   │  ← End-user client
│    (aiogram)     │
└────────┬────────┘
         │
┌────────▼────────┐
│    Backend       │
│   (bot.py)       │
│   handlers/      │
│   services/      │
│   keyboards/     │
└────────┬────────┘
         │
┌────────▼────────┐
│    Database      │
│   (SQLite)       │
│   menu.json      │
└──────────────────┘
```

## Usage

### User Commands

| Команда | Описание |
|---------|----------|
| `/start` | Начало работы, выбор языка |
| 🍽 Сегодня | Меню на текущий день |
| 📅 Неделя | Выбор дня недели |
| 🌿 Постное | Постное меню |
| ℹ️ Информация | Контакты столовой |
| 🌐 Язык | Смена языка |
| ⚙️ Админ | Админ-панель (для админов) |

### Admin Commands

| Команда | Описание |
|---------|----------|
| ➕ Добавить блюдо | Добавить новое блюдо |
| ➕ Добавить постное | Добавить постное блюдо |
| ✏️ Редактировать | Изменить блюдо |
| 🗑 Удалить | Удалить блюдо |
| 📋 Смотреть меню | Просмотр всего меню |

## Deployment

### Requirements
- **OS**: Ubuntu 24.04 (или любой Linux/MacOS)
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### Quick Start (Docker)

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/se-toolkit-hackathon.git
cd se-toolkit-hackathon

# 2. Create .env file
cp .env.example .env

# 3. Edit .env and add your credentials
nano .env
# BOT_TOKEN=your_telegram_bot_token
# ADMIN_ID=your_telegram_id

# 4. Run deployment script
chmod +x deploy.sh
./deploy.sh

# OR manually:
docker-compose up -d
```

### Manual Deployment (without Docker)

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/se-toolkit-hackathon.git
cd se-toolkit-hackathon

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/MacOS
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env with your BOT_TOKEN and ADMIN_ID

# 5. Run the bot
python bot.py
```

### Adding Additional Admins

Create `admins.json` in the project root:

```json
["123456789", "987654321"]
```

Or set `ADMIN_ID` in `.env` for the primary admin.

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | Yes | Telegram bot token from @BotFather |
| `ADMIN_ID` | Yes | Primary admin Telegram ID |

## Project Structure

```
matrix_bot/
├── bot.py              # Entry point
├── config.py           # Configuration
├── requirements.txt    # Dependencies
├── Dockerfile          # Docker build
├── docker-compose.yml  # Docker Compose
├── deploy.sh           # Deployment script
├── .env.example        # Environment template
├── LICENSE             # MIT License
│
├── handlers/           # Message handlers
│   ├── start.py        # Start & language
│   ├── menu.py         # Menu viewing
│   └── admin.py        # Admin panel
│
├── keyboards/          # Keyboards
│   ├── reply.py        # Main menu keyboards
│   └── inline.py       # Inline keyboards
│
├── services/           # Business logic
│   ├── database.py     # SQLite operations
│   ├── user_service.py # User management
│   └── menu_service.py # Menu management
│
├── utils/              # Utilities
│   ├── logger.py       # Logging setup
│   └── i18n.py         # Internationalization
│
├── data/               # Persistent data (Docker)
├── logs/               # Log files
└── docs/               # Documentation
```

## Development

### Setup Development Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run bot
python bot.py
```

### Tech Stack

- **Python 3.11+**
- **aiogram 3.x** — Telegram Bot framework
- **SQLite** — Database
- **Docker** — Containerization

## License

MIT License - see [LICENSE](LICENSE) file.

## Author

- **Name:** [Your Name]
- **Email:** [Your University Email]
- **Group:** [Your Group]

---

Made with ❤️ for MATRIX cafeteria