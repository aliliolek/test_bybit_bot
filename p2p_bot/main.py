from __future__ import annotations

import argparse
from pprint import pprint

from .client import BybitP2PClient
from .config import load_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple Bybit P2P helper")
    parser.add_argument("config", help="Path to YAML config file")
    parser.add_argument(
        "--side",
        type=int,
        choices=[0, 1],
        help="0 for BUY ads, 1 for SELL ads",
    )
    args = parser.parse_args()

    cfg = load_config(args.config)
    bybit_cfg = cfg.get("bybit", {})
    api_key = bybit_cfg.get("api_key", "")
    api_secret = bybit_cfg.get("api_secret", "")
    testnet = bybit_cfg.get("testnet", False)

    client = BybitP2PClient(api_key=api_key, api_secret=api_secret, testnet=testnet)
    ads = client.list_ads(side=args.side)
    pprint(ads)


if __name__ == "__main__":
    main()
