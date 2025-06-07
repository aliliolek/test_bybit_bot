from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any
import os
import yaml


@dataclass
class GlobalConfig:
    token: str = "USDT"
    currency: str = "USD"
    total_balance: float = 0.0


@dataclass
class BybitConfig:
    api_key: str = ""
    api_secret: str = ""
    testnet: bool = False


@dataclass
class TelegramConfig:
    token: str = ""
    chat_id: str = ""


@dataclass
class AdConfig:
    tag: str
    type: str
    balance: Union[str, float]
    min_limit: float
    max_limit: float
    payment_methods: List[int] = field(default_factory=list)


@dataclass
class PricingSideConfig:
    fixed_price: Optional[float] = None
    fallback_price: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

    check_payment_methods: bool = False
    allowed_payment_types: List[int] = field(default_factory=list)

    check_min_balance: bool = False
    min_amount_threshold: float = 0.0

    check_limit: bool = False
    min_limit_threshold: float = 0.0
    max_limit_threshold: float = 0.0

    check_register_days: bool = False
    min_register_days: int = 0

    check_min_orders: bool = False
    min_order_count: int = 0

    check_target_nicknames: bool = False
    target_nicknames: List[str] = field(default_factory=list)


@dataclass
class PricingConfig:
    SELL: PricingSideConfig = field(default_factory=PricingSideConfig)
    BUY: PricingSideConfig = field(default_factory=PricingSideConfig)


@dataclass
class Config:
    global_cfg: GlobalConfig
    bybit: BybitConfig
    telegram: TelegramConfig
    ads: List[AdConfig] = field(default_factory=list)
    pricing: PricingConfig = field(default_factory=PricingConfig)


def _expand_env(content: str) -> str:
    """Expand environment variables like ${VAR} in a YAML file."""
    return os.path.expandvars(content)


def load_config(path: str) -> Config:
    with open(path, "r") as f:
        text = _expand_env(f.read())
        data: Dict[str, Any] = yaml.safe_load(text) or {}

    global_cfg = GlobalConfig(**data.get("global", {}))
    bybit_cfg = BybitConfig(**data.get("bybit", {}))
    telegram_cfg = TelegramConfig(**data.get("telegram", {}))

    ads = [AdConfig(**ad) for ad in data.get("ads", [])]

    pricing_data = data.get("pricing", {})
    sell_cfg = PricingSideConfig(**pricing_data.get("SELL", {}))
    buy_cfg = PricingSideConfig(**pricing_data.get("BUY", {}))
    pricing_cfg = PricingConfig(SELL=sell_cfg, BUY=buy_cfg)

    return Config(
        global_cfg=global_cfg,
        bybit=bybit_cfg,
        telegram=telegram_cfg,
        ads=ads,
        pricing=pricing_cfg,
    )
