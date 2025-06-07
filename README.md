# Simple Bybit P2P Project

This project demonstrates basic usage of the `bybit-p2p` library. It provides a
small command line helper that lists your active P2P advertisements.

## Setup

1. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `config.yaml` and fill in your API credentials.
3. Run the tool
   ```bash
   python -m p2p_bot.main config.yaml
   ```

Use the `--side` option to filter BUY (0) or SELL (1) ads.
