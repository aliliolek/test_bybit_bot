# Bybit P2P Trading Bot

This project provides a small Telegram controlled bot to automate basic P2P trading tasks on Bybit.  
The bot loads a YAML configuration file and starts periodic loops that update P2P ads and interact with new orders.

## Features
- Load `config.yaml` via Telegram document message.
- Periodic update loop for SELL and BUY ads.
- One‑time greeting in new order chats.
- One‑time automatic mark as paid for BUY orders.
- Placeholder functions for pricing strategies.

## Usage
1. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
2. Export your Telegram bot token
   ```bash
   export TELEGRAM_TOKEN=123:ABC
   ```
3. Run the bot
   ```bash
   python -m bybit_bot.bot
   ```

Edit `config.yaml` to set Bybit API credentials and ad parameters.  
Send the file to your bot to start trading.
