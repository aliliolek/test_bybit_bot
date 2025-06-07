from __future__ import annotations
from typing import List, Optional, Dict, Any
from bybit_p2p import P2P

class BybitClient:
    """Wrapper around bybit_p2p.P2P to simplify common operations."""

    def __init__(self, *, api_key: str, api_secret: str, testnet: bool = False):
        self.client = P2P(testnet=testnet, api_key=api_key, api_secret=api_secret)

    def get_active_ads(self, side: int) -> List[Dict[str, Any]]:
        """Return list of online ads for the account."""
        resp = self.client.get_ads_list(side=side, status=2, page=1, size=50)
        return resp.get("result", {}).get("items", [])

    def find_ad_by_tag(self, side: int, tag: str) -> Optional[Dict[str, Any]]:
        for ad in self.get_active_ads(side):
            remark = ad.get("remark", "") or ""
            if remark.startswith(tag):
                return ad
        return None

    def update_ad(self, **params):
        return self.client.update_ad(**params)

    def get_pending_orders(self) -> List[Dict[str, Any]]:
        resp = self.client.get_pending_orders(page=1, size=50)
        return resp.get("result", {}).get("items", [])

    def get_order_details(self, order_id: str) -> Dict[str, Any]:
        resp = self.client.get_order_details(orderId=order_id)
        return resp.get("result", {})

    def send_chat_message(self, order_id: str, message: str):
        from uuid import uuid4
        self.client.send_chat_message(
            orderId=order_id,
            message=message,
            contentType="str",
            msgUuid=str(uuid4()),
        )

    def mark_as_paid(self, order_id: str, payment_type: str, payment_id: str):
        self.client.mark_as_paid(
            orderId=order_id,
            paymentType=payment_type,
            paymentId=payment_id,
        )

    def get_balance(self, account_type: str = "UNIFIED") -> Dict[str, Any]:
        resp = self.client.get_current_balance(accountType=account_type)
        return resp.get("result", {})
