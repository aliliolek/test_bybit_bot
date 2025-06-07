import asyncio
import logging
from pathlib import Path
from typing import Dict, Set

from telegram import Update, Document
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from .config_loader import load_config, Config, AdConfig
from .bybit_client import BybitClient
from .price_strategy import (
    calculate_sell_price,
    calculate_buy_price,
    calculate_buy_quantity,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_PATH = Path("config.yaml")

class TradingBot:
    def __init__(self, telegram_token: str):
        self.application = ApplicationBuilder().token(telegram_token).build()
        self.config: Config | None = None
        self.bybit: BybitClient | None = None
        self.seen_orders: Set[str] = set()
        self.paid_orders: Set[str] = set()
        self._tasks: Set[asyncio.Task] = set()

        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(MessageHandler(filters.Document.ALL, self.load_config_file))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Send config.yaml as a document to load configuration")

    async def load_config_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        document: Document = update.message.document
        if not document.file_name.endswith(".yaml"):
            await update.message.reply_text("Please send a .yaml configuration file")
            return
        file_path = CONFIG_PATH
        await document.get_file().download_to_drive(custom_path=str(file_path))
        self.config = load_config(file_path)
        self.bybit = BybitClient(
            api_key=self.config.api_key,
            api_secret=self.config.api_secret,
            testnet=self.config.testnet,
        )
        await update.message.reply_text("Configuration loaded. Starting loops...")
        self.start_loops()

    def start_loops(self):
        if not self.config or not self.bybit:
            return
        task = self.application.create_task(self.loop())
        self._tasks.add(task)

    async def loop(self):
        assert self.config and self.bybit
        interval = self.config.update_interval
        while True:
            try:
                await self.update_sell_ads()
                await self.update_buy_ads()
                await self.process_orders()
            except Exception as e:
                logger.exception("Error in main loop: %s", e)
            await asyncio.sleep(interval)

    async def update_sell_ads(self):
        assert self.bybit and self.config
        for ad_conf in self.config.ads:
            if ad_conf.type.upper() != "SELL":
                continue
            ad = self.bybit.find_ad_by_tag(1, ad_conf.tag)
            if not ad:
                continue
            price = ad_conf.fixed_price
            if price is None:
                price = calculate_sell_price(ad_conf, 0)
            quantity = ad_conf.balance
            if isinstance(quantity, str) and quantity == "max":
                balance = self.bybit.get_balance()
                quantity = balance.get("availableBalance")
            self.bybit.update_ad(
                id=ad.get("itemId") or ad.get("id"),
                priceType=0,
                price=price,
                minAmount=ad_conf.min_amount,
                maxAmount=ad_conf.max_amount,
                paymentIds=ad_conf.payment_ids,
                quantity=quantity,
                remark=ad_conf.remark or ad.get("remark"),
                actionType="MODIFY",
            )

    async def update_buy_ads(self):
        assert self.bybit and self.config
        for ad_conf in self.config.ads:
            if ad_conf.type.upper() != "BUY":
                continue
            ad = self.bybit.find_ad_by_tag(0, ad_conf.tag)
            if not ad:
                continue
            price = ad_conf.fixed_price
            if price is None:
                price = calculate_buy_price(ad_conf, 0)
            quantity = ad_conf.quantity
            if quantity is None:
                quantity = calculate_buy_quantity(ad_conf, 0)
            self.bybit.update_ad(
                id=ad.get("itemId") or ad.get("id"),
                priceType=0,
                price=price,
                minAmount=ad_conf.min_amount,
                maxAmount=ad_conf.max_amount,
                paymentIds=ad_conf.payment_ids,
                quantity=quantity,
                remark=ad_conf.remark or ad.get("remark"),
                actionType="MODIFY",
            )

    async def process_orders(self):
        assert self.bybit
        for order in self.bybit.get_pending_orders():
            order_id = str(order.get("orderId") or order.get("id"))
            side = order.get("side")
            if order_id not in self.seen_orders:
                self.bybit.send_chat_message(order_id, "\U0001F44B\U0001F440")
                self.seen_orders.add(order_id)
            if side == 0 and order_id not in self.paid_orders:
                details = self.bybit.get_order_details(order_id)
                terms = details.get("paymentTermList", [{}])[0]
                payment_type = terms.get("paymentType")
                payment_id = terms.get("id")
                if payment_type and payment_id:
                    self.bybit.mark_as_paid(order_id, payment_type, payment_id)
                    self.bybit.send_chat_message(order_id, "pls wait, I'm paying")
                self.paid_orders.add(order_id)

    def run(self):
        self.application.run_polling()


def main():
    import os
    token = os.getenv("TELEGRAM_TOKEN", "")
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN env var not set")
    bot = TradingBot(token)
    bot.run()

if __name__ == "__main__":
    main()
