from __future__ import annotations

from typing import Any, Dict, List, Optional

from bybit_p2p import P2P


class BybitP2PClient:
    """Simple wrapper around :class:`bybit_p2p.P2P`."""

    def __init__(self, api_key: str, api_secret: str, testnet: bool = False) -> None:
        self._client = P2P(testnet=testnet, api_key=api_key, api_secret=api_secret)

    def list_ads(self, *, status: int = 2, side: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return a list of the user's ads."""
        params: Dict[str, Any] = {"status": status, "page": 1, "size": 50}
        if side is not None:
            params["side"] = side
        resp = self._client.get_ads_list(**params)
        return resp.get("result", {}).get("items", [])
