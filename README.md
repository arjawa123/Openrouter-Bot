# Telegram OpenRouter Bot - AI Personal Assistant Agent

A production-ready, highly modular Telegram AI Assistant powered by multiple LLM providers (OpenRouter & Groq). Built with **Python 3.11+**, **FastAPI**, **Aiogram 3.x**, and **SQLAlchemy**.

This bot is designed to be more than just a chatbot; it is a **Personal Assistant Agent** capable of reasoning, proactive memory management, and productivity automation.

## 🚀 Key Features

- **🧠 Agentic Orchestration:** Uses an intent-detection layer to automatically route user requests to specialized services (Chat, Tasks, Notes, Research, Memory).
- **🛡️ Multi-Provider LLM with Fallback:** Uses **OpenRouter** as the primary engine with automatic failover to **Groq** (using Mixtral/Llama3) for high availability and speed.
- **⏰ Smart Reminders:** Automatically extracts due dates from natural language (e.g., "Remind me to call Mom tomorrow at 10am") and sends proactive notifications via a background worker.
- **📈 Intelligence Memory (Fact Extraction):** Automatically learns and remembers facts about the user from conversations to provide a deeply personalized experience.
- **🌐 Web Research:** Intelligent URL scraping and summarization that integrates directly into the assistant's reasoning context.
- **📓 Productivity Suite:** Integrated Todo list, Notes, and Code Snippet management with natural language interaction.
- **🌅 Narrative Daily Digest:** Generates a warm, AI-written morning summary of your pending tasks, recent notes, and personalized reminders.

## 🛠️ Tech Stack

- **Framework:** FastAPI (Web API) & Aiogram (Telegram Bot)
- **Database:** PostgreSQL with SQLAlchemy (Async) & Alembic (Migrations)
- **LLM Gateway:** OpenRouter (Primary) & Groq (Fallback)
- **Logging:** Loguru for structured, beautiful logs
- **Deployment:** Optimized for Render (Blueprint support)
- **Local Dev:** Fully compatible with Termux (Android)

## 📁 Project Structure

```
app/
├── api/              # Webhook and Health endpoints
├── bot/              # Telegram handlers, commands, and formatters
├── db/               # Models, CRUD, and session management
├── services/         # Core Logic
│   ├── llm/          # Multi-provider LLM abstraction & fallback logic
│   ├── assistant/    # Agent reasoning and context assembly
│   ├── memory/       # Fact extraction and long-term memory
│   └── productivity/ # Todos, Notes, Reminders, and Scraper
├── prompts/          # Dynamic system prompt templates
├── config.py         # Pydantic-based settings
└── main.py           # Application entry point & background workers
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.11+
- PostgreSQL
- Telegram Bot Token ([@BotFather](https://t.me/BotFather))
- API Keys: [OpenRouter](https://openrouter.ai/) and [Groq](https://console.groq.com/)

### 2. Local Setup (Termux / Desktop)
```bash
# Clone and enter directory
git clone <repo-url>
cd telegram-openrouter-bot

# Setup virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure Environment
cp .env.example .env
# Edit .env with your keys and DATABASE_URL
```

### 3. Database Migrations
Always run migrations after updating the code:
```bash
alembic revision --autogenerate -m "update_to_agent_v2"
alembic upgrade head
```

### 4. Running the Bot
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🤖 Available Commands

- `/start` - Initialize your personalized profile.
- `/help` - Show advanced command guide.
- `/profile` - See what the assistant has learned about you.
- `/settings` - Interactively update your name, language, or style.
- `/mode <mode>` - Manually switch between Assistant, Coder, Researcher, or Planner.
- `/todo add <text>` - Add tasks with natural language dates.
- `/digest` - Get your personalized AI-written daily summary.
- `/memory` - View your long-term memories.

**Pro-tip:** You don't always need commands! Just talk to the bot. 
*Example: "I need to buy milk tomorrow morning" will automatically create a todo with a reminder.*

---

## ☁️ Deployment

Deploying to **Render** is easy:
1. Push your code to GitHub.
2. Use the `render.yaml` blueprint.
3. Set your `TELEGRAM_WEBHOOK_URL` to your Render app URL.
4. Ensure `APP_ENV=production` to enable the webhook.

---
Built with ❤️ for a more productive AI-human collaboration.
