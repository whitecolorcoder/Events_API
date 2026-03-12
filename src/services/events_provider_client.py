from typing import Any, Dict, List, Optional

import requests

from src.config.db_conf import settings


class EventsProviderClient:
    BASE_URL = "https://events-provider.dev-2.python-labs.ru/api"

    def __init__(self):
        self.headers = {"x-api-key": settings.EVENTS_API_KEY, "Content-Type": "application/json"}

    def get_events_page(self, changed_at: str, cursor: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/events/?changed_at={changed_at}"
        if cursor:
            url += f"&cursor={cursor}"

        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_all_events(self, changed_at: str) -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []
        cursor = None

        while True:
            page = self.get_events_page(changed_at, cursor)
            events.extend(page["results"])

            next_url = page["next"]
            if not next_url:
                break

            if "cursor=" in next_url:
                cursor = next_url.split("cursor=")[-1]
            else:
                cursor = None

        return events

    def register(self, event_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/events/{event_id}/register/"
        response = requests.post(url, json=payload, headers=self.headers, timeout=10)
        response.raise_for_status()
        return response.json()

    def unregister(self, event_id: str, ticket_id: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/events/{event_id}/unregister/"
        response = requests.delete(url, json={"ticket_id": ticket_id}, headers=self.headers, timeout=10)
        response.raise_for_status()
        return response.json()
