# CS2 Info Hub Bot (Telegram)

A comprehensive Telegram bot that acts as an all-in-one hub for CS2 players. It provides real-time skin prices, live server stats, and detailed user profile/inventory inspection using multiple official and unofficial Steam APIs.

---

## 🚀 Features

* **📈 Real-Time Price Checker:**
    * Search for any CS2 item (skins, stickers, agents, crates) by name from a local database of 27,000+ items.
    * Get detailed price info: **Lowest Price**, **Median Price**, and **24h Volume**.
* **👤 Steam Profile Inspector:**
    * Fetches any user's profile using their SteamID64 via the **Official Steam Web API**.
    * Displays avatar, status (Online/Offline/In-Game), real name, and account creation date.
* **🎒 Public Inventory Viewer:**
    * Fetches and displays a user's *public* CS2 inventory.
    * Implements a full pagination system ("Next Page", "Prev Page") to browse hundreds of items.
    * Allows checking the price of any item directly from the inventory viewer.
* **📊 Live Server Stats:**
    * Grabs the current **total players online** and **players in-game** from Valve's live JSON API.
* **🤖 Advanced Bot UX:**
    * Built using `aiogram 3.x` with a clean, modular architecture (handlers, API clients, keyboards separated).
    * Uses **Finite State Machine (FSM)** to manage complex user dialogues (search, inventory browsing).
    * Features an interactive "Hub" interface that **edits messages** (`edit_message_text`) instead of spamming the chat.

## 🛠️ Tech Stack

* **Python 3.11+**
* **Aiogram 3.x** (Modern asynchronous Telegram bot framework)
* **Aiohttp** (For all asynchronous API calls)
* **Python-dotenv** (For secure management of API keys and tokens)

## ⚙️ How to Run

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/kiri-osint/CS2-Info-Hub-Bot.git (https://github.com/kiri-osint/CS2-Info-Hub-Bot.git)
    cd CS2-Info-Hub-Bot
    ```
2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # (On Windows: .\venv\Scripts\activate)
    pip install -r requirements.txt
    ```
3.  **Create your `.env` file:**
    * Create a file named `.env` in the root directory.
    * Add your keys:
        ```ini
        BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
        STEAM_API_KEY="YOUR_STEAM_WEB_API_KEY"
        ```
4.  **Run the bot:**
    ```bash
    python server.py
    ```

---
