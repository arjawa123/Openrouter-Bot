# Telegram OpenRouter Bot

A production-ready Telegram bot powered by OpenRouter AI, built with Python, FastAPI, aiogram, and SQLAlchemy. Designed for local development on Termux and seamless deployment to Render.

## Features

- **AI Chat:** General chat, coding assistance, research, and planning modes using various models via OpenRouter.
- **Web Scraping:** Send a URL and the bot will fetch, extract, and summarize its content.
- **Persistent Memory:** The bot remembers facts about you (`/remember`, `/forget`, `/memory`).
- **Productivity Tools:** Notes (`/note`, `/notes`), Todos (`/todo`), and Snippets (`/snippet`).
- **Daily Digest:** A quick summary of your profile, todos, and notes (`/digest`).

## Project Structure

```
telegram-openrouter-bot/
├── app/                  # Main application code
│   ├── api/              # FastAPI endpoints (webhook, health)
│   ├── bot/              # Telegram bot handlers and commands
│   ├── db/               # SQLAlchemy models and CRUD operations
│   ├── prompts/          # System prompts for different AI modes
│   ├── schemas/          # Pydantic models for data validation
│   ├── services/         # Core business logic (AI, scraping, memory)
│   ├── utils/            # Helper functions
│   ├── config.py         # Environment variables configuration
│   ├── logging_config.py # Loguru setup
│   └── main.py           # FastAPI application entry point
├── migrations/           # Alembic database migrations
├── .env.example          # Example environment variables
├── alembic.ini           # Alembic configuration
├── render.yaml           # Render deployment configuration
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

---

## Termux Local Development Setup

If you are developing this on an Android device using Termux, follow these steps:

### 1. Install Basic Dependencies
Open Termux and run:
```bash
pkg update && pkg upgrade
pkg install python python-pip postgresql rust libffi openssl
```

### 2. Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Requirements
```bash
pip install -r requirements.txt
```
*Troubleshooting:* If `asyncpg` or `cryptography` fails to build, ensure `rust` and `libffi` are installed via `pkg install`. Sometimes `pip install wheel` helps before installing requirements.

### 4. Setup Local PostgreSQL Database
In Termux, start the PostgreSQL server:
```bash
initdb ~/pgdata
pg_ctl -D ~/pgdata start
```
Create a user and database:
```bash
createuser user
createdb botdb
```

### 5. Configure Environment Variables
Copy the example env file:
```bash
cp .env.example .env
```
Edit `.env` and fill in your details:
- Get a Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Get an OpenRouter API Key from [OpenRouter](https://openrouter.ai/keys)
- Set `DATABASE_URL=postgresql+asyncpg://user@localhost/botdb` (adjust if you set a password)

### 6. Run Migrations
Generate and apply database migrations:
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 7. Run Local Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 8. Expose Local Webhook (ngrok / cloudflared)
Since Telegram needs a public URL for webhooks, use `cloudflared` (recommended for Termux):
```bash
pkg install cloudflared
cloudflared tunnel --url http://localhost:8000
```
Copy the generated `https://...trycloudflare.com` URL. Update your `.env` file:
```
TELEGRAM_WEBHOOK_URL=https://your-tunnel-url.trycloudflare.com
APP_ENV=production # Required to enable webhook setting in main.py
```
Restart the Uvicorn server.

---

## Render Deployment

This project includes a `render.yaml` file for easy deployment using Render's Blueprint feature.

### Prerequisites
1. Push this code to a GitHub/GitLab repository.
2. Create an account on [Render](https://render.com).

### Deployment Steps
1. In Render dashboard, go to **Blueprints** -> **New Blueprint Instance**.
2. Connect your Git repository.
3. Render will parse `render.yaml` and create a Web Service and optionally a PostgreSQL database (if defined, otherwise create a managed Postgres DB manually and link it).
4. **Environment Variables:** Go to the Environment settings of your new Web Service in Render and fill in all the required variables (Token, API Key, Webhook URL, Webhook Secret, Database URL).
5. Ensure your `TELEGRAM_WEBHOOK_URL` is set to `https://your-render-app-name.onrender.com`.

### Testing Deployment
Visit `https://your-render-app-name.onrender.com/health` in your browser. It should return `{"status": "ok", "version": "1.0.0"}`.

---

## Available Commands

Interact with your bot on Telegram:

- `/start` - Initialize your profile
- `/help` - View command list
- `/mode <mode>` - Change AI mode (assistant, coder, researcher, planner)
- `/remember <fact>` - Save information
- `/forget <keyword>` - Remove saved info
- `/memory` - See what the bot remembers
- `/note <text>` - Save a quick note
- `/todo add <task>` - Add task
- `/todo list` - View tasks
- `/digest` - Get a summary of your day
- `/code <prompt>` - Quick code generation

Just paste a URL, and the bot will automatically try to read and summarize it!
