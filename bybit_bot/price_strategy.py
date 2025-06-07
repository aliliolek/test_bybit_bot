"""Placeholders for pricing and quantity strategies."""

from .config_loader import PricingSideConfig


def calculate_sell_price(cfg: PricingSideConfig, market_price: float) -> float:
    """Return price for SELL ad. Placeholder for custom logic."""
    if cfg.fixed_price is not None:
        return cfg.fixed_price
    return market_price


def calculate_buy_price(cfg: PricingSideConfig, market_price: float) -> float:
    """Return price for BUY ad. Placeholder for custom logic."""
    if cfg.fixed_price is not None:
        return cfg.fixed_price
    return market_price


def calculate_order_quantity(balance: float, available: float) -> float:
    """Return quantity for an ad based on balance settings."""
    if isinstance(balance, str) and balance == "max":
        return available
    return float(balance)
