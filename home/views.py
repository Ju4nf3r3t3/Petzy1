from __future__ import annotations

import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.shortcuts import render
from django.utils.translation import gettext as _

from .services import get_featured_provider


def _fetch_json(url: str, *, timeout: int = 5) -> dict | list | None:
    """Try to fetch JSON data from an external endpoint."""

    if not url:
        return None

    request = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:  # nosec: B310 - trusted endpoints configurable
            payload = response.read().decode("utf-8")
        return json.loads(payload)
    except (URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return None


def _normalise_ally_products(data: dict | list | None, limit: int = 5):
    """Normalise data coming from the allied service."""

    if not data:
        return []

    items = data if isinstance(data, list) else data.get("results", [])
    normalised = []
    for item in items[:limit]:
        if isinstance(item, dict):
            normalised.append(
                {
                    "name": item.get("name") or item.get("title"),
                    "price": item.get("price"),
                    "description": item.get("description"),
                    "url": item.get("detail_url") or item.get("url"),
                }
            )
    return normalised


def _extract_weather(data: dict | list | None):
    if not isinstance(data, dict):
        return None
    current = data.get("current_weather")
    if not isinstance(current, dict):
        return None
    return {
        "temperature": current.get("temperature"),
        "windspeed": current.get("windspeed"),
    }


def index(request):
    featured_provider = get_featured_provider()
    featured_products = featured_provider.get_featured()

    ally_raw = _fetch_json(getattr(settings, "ALLY_SERVICE_URL", ""))
    ally_products = _normalise_ally_products(ally_raw)

    weather_raw = _fetch_json(getattr(settings, "THIRD_PARTY_WEATHER_URL", ""))
    weather_data = _extract_weather(weather_raw)

    context = {
        "featured_products": featured_products,
        "ally_products": ally_products,
        "weather_data": weather_data,
        "ally_service_url": getattr(settings, "ALLY_SERVICE_URL", ""),
        "breadcrumbs": [
            {"label": _("Inicio"), "url": ""},
        ],
    }
    return render(request, "home/index.html", context)