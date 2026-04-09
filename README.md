# Matrix Bot

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/aiogram-3.x-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" alt="aiogram 3.x">
  <img src="https://img.shields.io/badge/Docker-ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker ready">
  <img src="https://img.shields.io/badge/License-MIT-success?style=for-the-badge" alt="MIT License">
</p>

<p align="center">
  <b>Telegram bot for the MATRIX cafeteria menu</b><br>
  Browse today's dishes, weekly menus, lenten meals, and favorites in Russian or English.
</p>

<p align="center">
  <a href="#features">Features</a> ·
  <a href="#usage">Usage</a> ·
  <a href="#deployment">Deployment</a> ·
  <a href="#project-structure">Project Structure</a>
</p>

## Overview

Matrix Bot is a Telegram assistant for the university cafeteria. It helps users quickly find menu items, view dish details, save favorites, and switch between Russian and English.

## Demo

<p align="center">
  <img src="docs/screenshots/main_menu.png" alt="Main menu" width="31%">
  <img src="docs/screenshots/day_menu.png" alt="Day menu" width="31%">
  <img src="docs/screenshots/categories.png" alt="Dish categories" width="31%">
</p>

## Product Context

### End Users
- **Students and university staff** - the main audience who wants to quickly check what is served today
- **MATRIX cafeteria visitors** - people who want to view dishes, prices, ingredients, and calories before visiting

### Problem
- There is no convenient way to check the cafeteria menu without visiting in person
- Students do not always know the current prices and ingredients
- It is hard to find lenten dishes quickly
- Staff need a simple way to update the menu

### Solution
A Telegram bot with inline navigation:
- Automatic "today" menu based on the current weekday
- Weekly menu browsing by day
- Dish categories such as salads, soups, main dishes, side dishes, beverages, bread, and set lunch
- Detailed dish information: price, weight, calories, and ingredients
- Favorites for saving dishes you like
- Separate lenten menu section
- Bilingual interface: Russian and English
- Admin panel for managing dishes and administrators

## Features

- [x] Russian and English language support
- [x] Today menu with automatic weekday detection
- [x] Weekly menu browsing
- [x] Lenten menu
- [x] Favorites
- [x] Dish details: price, weight, calories, ingredients
- [x] Admin panel with authorization
- [x] Dish categorization
- [x] Set lunch support
- [x] Inline navigation with back button
- [x] Multi-level menu navigation
- [x] Dish visibility toggle
- [x] Dual-language dish names
- [x] Persistent user storage in JSON
- [x] Docker-based deployment
- [x] Flexible admin list stored in JSON

### Planned
- [ ] Notifications for new menu updates
- [ ] Search by dish name
- [ ] Ratings and reviews
- [ ] Web version

## Architecture

```
┌─────────────────┐
│   Telegram Bot   │  ← End-user client
│    (aiogram)     │
└────────┬────────┘
         │
┌────────▼────────┐
│    Application   │
│     (bot.py)     │
│   handlers/      │
│   keyboards/     │
│   utils/         │
└────────┬────────┘
         │
┌────────▼────────┐
│ Persistent data  │
│ menu.json        │
│ users.json       │
│ admins.json      │
└──────────────────┘
```

## Usage

### Main Buttons

| Button | Description |
|--------|-------------|
| `/start` | Start the bot and choose a language |
| 🍽 Today's menu | Show the current day's menu |
| 📅 Weekly menu | Choose a weekday |
| 🌿 Lenten menu | Show lenten dishes |
| ⭐ Favorites | Open saved dishes |
| ℹ️ Information | Show cafeteria information |
| 🌐 Change language | Switch between Russian and English |
| ⚙️ Admin panel | Open admin tools for authorized users |

### Admin Actions

| Action | Description |
|--------|-------------|
| ➕ Add dish | Add a new dish to the menu |
| ✏️ Edit dish | Edit an existing dish |
| 🗑 Delete dish | Remove a dish from the menu |
| 🙈 Hide dish | Toggle a dish's visibility |
| 👥 Administrators | Add or remove admin users |
| 🏠 Main | Return to the main menu |

## Deployment

### Requirements
- **OS**: Ubuntu 24.04 or any modern Linux / macOS
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### Quick Start with Docker

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/se-toolkit-hackathon.git
cd se-toolkit-hackathon

# 2. Create the .env file
cp .env.example .env

# 3. Edit .env and add your credentials
nano .env
# BOT_TOKEN=your_telegram_bot_token
# ADMIN_ID=your_telegram_id

# 4. Start the bot
docker compose up -d --build

# 5. Check status
docker compose ps
docker compose logs -f
```

### Manual Deployment Without Docker

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/se-toolkit-hackathon.git
cd se-toolkit-hackathon

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create the .env file
cp .env.example .env
# Add BOT_TOKEN and ADMIN_ID

# 5. Run the bot
python bot.py
```

### Adding Additional Administrators

Create `admins.json` in the project root:

```json
["123456789", "987654321"]
```

The primary administrator can also be configured through `ADMIN_ID` in `.env`.

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | Yes | Telegram bot token from @BotFather |
| `ADMIN_ID` | Yes | Primary administrator Telegram ID |

## Project Structure

```
matrix_bot/
├── bot.py              # Main entry point
├── config.py           # Configuration and admin checks
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker image build
├── docker-compose.yml  # Docker Compose configuration
├── .env.example        # Environment template
├── LICENSE             # MIT License
├── README.md           # Project documentation
│
├── handlers/           # Modular handlers
│   ├── start.py        # Start and language flow
│   ├── menu.py         # Menu navigation
│   └── admin.py        # Admin panel logic
│
├── keyboards/          # Keyboard builders
│   ├── reply.py        # Main menu keyboard
│   └── inline.py       # Inline keyboards
│
├── utils/              # Utilities
│   └── i18n.py         # Translation strings
│
├── docs/               # Documentation assets
├── menu.json           # Menu data
├── users.json          # User data
└── admins.json         # Additional admins
```

## Development

### Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env
cp .env.example .env

# Run the bot
python bot.py
```

### Tech Stack

- **Python 3.11+**
- **aiogram 3.x** - Telegram bot framework
- **JSON files** - Lightweight persistent storage
- **Docker** - Containerization

## License

MIT License - see the [LICENSE](LICENSE) file.

## Author

- **Name:** Samoylova Diana
- **Email:** d.samoilova@innopolis.university
- **Group:** DSAI-05
- **GitHub:** dianasamojlova5947-cmyk

> Note: Telegram bot token and admin ID should be kept in your local `.env` file and should not be committed to GitHub.

---

Made with love for MATRIX cafeteria ❤️
