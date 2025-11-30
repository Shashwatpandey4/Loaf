# 🍞 LOAF — Your AI-Powered Meal Planning Companion

<p align="center">
  <img src="UI/loaf.png" alt="Loaf Logo" width="150"/>
</p>

**Loaf** is an end-to-end intelligent meal planning system that takes you from "I don't know what to eat" to "groceries on the way" in one seamless workflow. It combines AI-powered recipe recommendations, health-aware personalization, smart grocery ordering, and calendar integration—all without lifting a finger.

---

## ✨ What Loaf Does

### 1. 📚 Recipe Knowledge Base
Loaf maintains a curated database of recipes spanning multiple cuisines—from Spicy Sichuan Noodles to Classic Greek Moussaka. The knowledge base includes detailed information: ingredients with precise measurements, step-by-step instructions, prep/cook times, difficulty levels, and dietary tags.

**Where it lives:** `knowledge/recipes.py` contains the recipe definitions, and `scripts/load_recipes.py` loads them into the SQLite database (`knowledge.db`).

---

### 2. 👤 Personalized Health Profiles
Loaf creates a persona for each user by asking about dietary restrictions (vegetarian/non-vegetarian) and medical conditions (diabetes, high blood pressure, or none). This ensures every meal plan is tailored to your specific health needs.

**Where it lives:** `scripts/add_persona.py` handles the interactive persona creation, storing profiles in the database via `src/models/contracts.py` (the `Persona` model).

---

### 3. 🍽️ AI-Generated Meal Plans
Using an AI agent powered by OpenAI, Loaf generates personalized weekly meal plans based on your persona and preferences. The agent queries the recipe database intelligently and crafts a 7-day meal plan that respects your dietary needs. Using the `agno` framework, the agent uses SQL tools to query the database.

**Where it lives:** `scripts/demo.py` orchestrates the conversation with the AI agent, while `knowledge/prompt.py` contains the system prompt that guides the AI's behavior. The agent uses `agno` framework with SQL tools to query the database.

---

### 4. 🌐 Smart Recipe Scraping
Don't have a recipe in the database? No problem. When the AI suggests a recipe that doesn't exist locally, Loaf automatically scrapes it from **publicdomainrecipes.com** (or uses DuckDuckGo to find alternatives) and adds it to your knowledge base.

**Where it lives:** `scripts/recipe_scraper.py` handles the web scraping logic, `src/recipe_extraction.py` extracts structured recipe data from web pages, and `src/web_search.py` powers the DuckDuckGo search integration.

---

### 5. 🛒 Grocery Ordering & Stripe Payment
Once your meal plan is set, Loaf automatically:
- Generates a consolidated grocery list from all recipes
- Schedules delivery through a mock logistics API
- Processes payment via **Stripe** (test mode with dummy cards)
- Generates a PDF receipt with itemized pricing

**Where it lives:** `run_weekly_meal_workflow.py` contains the full workflow including `generate_grocery_list()`, `schedule_logistics()`, `trigger_stripe_payment()`, and `generate_pdf_logistics_payment()`. The mock delivery API is in `logistics/mock_logistics_api.py`.

---

### 6. 📅 Google Calendar Integration
Every meal gets scheduled on your Google Calendar at 6 PM each day, complete with cooking instructions in the event description. A grocery order reminder is also added for the weekend.

**Where it lives:** `calendar_agent/google_calendar.py` provides the OAuth flow and event creation helpers. The scheduling logic in `run_weekly_meal_workflow.py` calls `schedule_meal_plan()` to populate your calendar.

---

## 🚀 Quick Start

### Run Everything with One Command

```bash
./run.sh
```

This starts:
- **API Server** on `http://localhost:8000` — FastAPI backend that processes chat requests
- **UI Server** on `http://localhost:8080` — Simple web interface for interacting with Loaf

Open your browser to `http://localhost:8080` and start planning your meals!

---

## 🏗️ Project Architecture

```
Loaf/
├── run.sh                      # 🚀 One-click launcher for both servers
├── run_weekly_meal_workflow.py # 🔄 Complete end-to-end workflow orchestration
├── api_server.py               # 🌐 FastAPI server connecting UI to backend
├── chat.py                     # 💬 Interactive CLI chat interface
│
├── knowledge/
│   ├── recipes.py              # 📖 Recipe knowledge base (20+ recipes)
│   └── prompt.py               # 🧠 AI system prompt for meal planning
│
├── scripts/
│   ├── demo.py                 # 🎬 Main demo script (setup + chat)
│   ├── add_persona.py          # 👤 Interactive persona creation
│   ├── load_recipes.py         # 📥 Load recipes into database
│   ├── recipe_scraper.py       # 🕷️ Web scraping for new recipes
│   ├── meal_plan_tools.py      # 🛠️ Meal plan validation utilities
│   └── create_database.py      # 🗄️ Database initialization
│
├── src/
│   ├── models/contracts.py     # 📋 Pydantic models (Recipe, Persona, etc.)
│   ├── recipe_extraction.py    # 🔍 Extract recipes from web pages
│   ├── web_search.py           # 🌐 DuckDuckGo recipe search
│   └── fullstack_kb_answerer.py # 🤖 Knowledge base query engine
│
├── calendar_agent/
│   └── google_calendar.py      # 📅 Google Calendar OAuth & event creation
│
├── logistics/
│   └── mock_logistics_api.py   # 🚚 Mock grocery delivery API (Flask)
│
├── UI/                         # 🎨 Simple web interface
│   ├── index.html
│   ├── style.css
│   └── script.js
│
└── output_examples/            # 📄 Sample outputs
    ├── meal_plan_*.json        # Generated meal plans
    ├── grocery_list.json       # Consolidated shopping list
    ├── grocery_receipt.pdf     # Payment receipt with delivery info
    └── grocery_delivery_status.json
```

---

## 💳 Stripe Test Mode

When testing payments, use Stripe's test cards:

| Card Number | Result |
|-------------|--------|
| `4242 4242 4242 4242` | ✅ Successful payment |
| `4000 0000 0000 0002` | ❌ Card declined |
| `4000 0027 6000 3184` | 🔐 3D Secure required |

Use any future expiry date (e.g., `12/34`), any 3-digit CVC, and any ZIP code.

---

## 🔧 Environment Setup

1. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (create a `.env` file):
   ```
   OPENAI_API_KEY=your_openai_key
   STRIPE_API_KEY=your_stripe_test_key
   EXA_API_KEY=your_exa_key  # Optional, for enhanced search
   ```

4. **Set up Google Calendar** (for calendar integration):
   - Create OAuth credentials in Google Cloud Console
   - Download as `credentials.json` in the project root
   - First run will open browser for authentication



