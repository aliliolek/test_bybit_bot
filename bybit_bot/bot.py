import asyncio
import logging
from pathlib import Path
from typing import Dict, Set

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from .config_loader import load_config, Config
from .bybit_client import BybitClient
from .price_strategy import (
    calculate_sell_price,
    calculate_buy_price,
    calculate_order_quantity,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_PATH = Path("config.yaml")

class TradingBot:
    def __init__(self, config: Config):
        self.config = config
        self.application = (
            ApplicationBuilder()
            .token(config.telegram.token)
            .post_init(self._post_init)
            .build()
        )
        self.bybit = BybitClient(
            api_key=config.bybit.api_key,
            api_secret=config.bybit.api_secret,
            testnet=config.bybit.testnet,
        )
        self.seen_orders: Set[str] = set()
        self.paid_orders: Set[str] = set()
        self._tasks: Set[asyncio.Task] = set()

        self.application.add_handler(CommandHandler("start", self.start))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Bot is running")

    async def _post_init(self, app):
        app.create_task(self._loop())

    async def _loop(self):
        interval = 60
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
            price = calculate_sell_price(self.config.pricing.SELL, 0)
            available = self.bybit.get_balance().get("availableBalance", 0)
            quantity = calculate_order_quantity(ad_conf.balance, available)
            self.bybit.update_ad(
                id=ad.get("itemId") or ad.get("id"),
                priceType=0,
                price=price,
                minAmount=ad_conf.min_limit,
                maxAmount=ad_conf.max_limit,
                paymentIds=ad_conf.payment_methods,
                quantity=quantity,
                remark=ad.get("remark"),
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
            price = calculate_buy_price(self.config.pricing.BUY, 0)
            available = self.bybit.get_balance().get("availableBalance", 0)
            quantity = calculate_order_quantity(ad_conf.balance, available)
            self.bybit.update_ad(
                id=ad.get("itemId") or ad.get("id"),
                priceType=0,
                price=price,
                minAmount=ad_conf.min_limit,
                maxAmount=ad_conf.max_limit,
                paymentIds=ad_conf.payment_methods,
                quantity=quantity,
                remark=ad.get("remark"),
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
    config = load_config(CONFIG_PATH)
    bot = TradingBot(config)
    bot.run()

if __name__ == "__main__":
    main()
