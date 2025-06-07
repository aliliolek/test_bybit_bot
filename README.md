# Bybit P2P Trading Bot

This project provides a small Telegram controlled bot to automate basic P2P trading tasks on Bybit.
The bot reads a `config.yaml` file on startup and periodically updates P2P ads and processes orders.

## Features
- Periodic update loop for SELL and BUY ads.
- One‑time greeting in new order chats.
- One‑time automatic mark as paid for BUY orders.
- Placeholder functions for pricing strategies.

## Usage
1. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
2. Run the bot
   ```bash
   python -m bybit_bot.bot
   ```
Edit `config.yaml` to configure Bybit and Telegram credentials, ad settings and pricing rules before running the bot.
