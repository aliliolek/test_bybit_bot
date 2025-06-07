from dataclasses import dataclass, field
from typing import List, Optional, Union
import yaml

@dataclass
class AdConfig:
    tag: str
    type: str  # SELL or BUY
    fixed_price: Optional[float] = None
    balance: Optional[Union[str, float]] = None
    quantity: Optional[float] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    payment_ids: List[str] = field(default_factory=list)
    remark: str = ""

@dataclass
class Config:
    api_key: str
    api_secret: str
    testnet: bool = False
    update_interval: int = 60
    ads: List[AdConfig] = field(default_factory=list)

def load_config(path: str) -> Config:
    with open(path, "r") as f:
        data = yaml.safe_load(f) or {}
    ads = [AdConfig(**ad) for ad in data.get("ads", [])]
    return Config(
        api_key=data.get("api_key", ""),
        api_secret=data.get("api_secret", ""),
        testnet=data.get("testnet", False),
        update_interval=data.get("update_interval", 60),
        ads=ads,
    )
