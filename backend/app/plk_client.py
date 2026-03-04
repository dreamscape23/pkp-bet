from typing import Any

import httpx

from .config import settings


class PLKClient:
    def __init__(self) -> None:
        self.base_url = settings.plk_api_base_url
        self.api_key = settings.plk_api_key

    async def fetch_ic_operations(self) -> list[dict[str, Any]]:
        if not self.api_key:
            return []

        url = f'{self.base_url}/api/v1/operations'
        headers = {'X-API-Key': self.api_key}
        params = {'carriersInclude': 'IC', 'withPlanned': 'true'}

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

        if isinstance(data, list):
            return data
        if isinstance(data, dict) and 'items' in data and isinstance(data['items'], list):
            return data['items']
        return []
