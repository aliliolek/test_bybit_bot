"""Placeholders for pricing and quantity strategies."""

def calculate_sell_price(ad, market_price):
    """Return price for SELL ad. Placeholder for custom logic."""
    return market_price

def calculate_buy_price(ad, market_price):
    """Return price for BUY ad. Placeholder for custom logic."""
    return market_price

def calculate_buy_quantity(ad, available_balance):
    """Return quantity for BUY ad. Placeholder for custom logic."""
    return ad.quantity or 0
