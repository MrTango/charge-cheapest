"""Tibber price service wrapper for Home Assistant integration.

This module provides functions to:
- Call the tibber.get_prices Home Assistant service
- Parse the service response from the prices.null key structure
- Extract and validate price entries with start_time and price fields
"""

import logging
from datetime import datetime
from typing import Any, Callable

logger = logging.getLogger(__name__)


def parse_service_response(response: dict | None) -> list[dict]:
    """Parse price array from nested prices.null key structure.

    The tibber.get_prices service returns data in format:
    {
        "prices": {
            "null": [
                {"start_time": "...", "price": 0.26},
                ...
            ]
        }
    }

    Args:
        response: Raw service response dictionary.

    Returns:
        List of price entries from the nested structure.
        Returns empty list if response is malformed or missing required keys.
    """
    if response is None:
        logger.warning("Received None response from tibber service")
        return []

    if not isinstance(response, dict):
        logger.warning("Response is not a dictionary: %s", type(response))
        return []

    prices_container = response.get("prices")
    if prices_container is None:
        logger.warning("Response missing 'prices' key")
        return []

    if not isinstance(prices_container, dict):
        logger.warning("'prices' is not a dictionary: %s", type(prices_container))
        return []

    # The key is literally "null" as a string in the YAML response
    price_array = prices_container.get("null")
    if price_array is None:
        logger.warning("Response missing 'prices.null' key")
        return []

    if not isinstance(price_array, list):
        logger.warning("'prices.null' is not a list: %s", type(price_array))
        return []

    return price_array


def extract_price_entries(entries: list[dict]) -> list[dict]:
    """Extract and validate price entries from raw data.

    Each entry must have:
    - start_time: ISO 8601 timestamp with timezone (preserved as string)
    - price: Numeric value

    Args:
        entries: List of raw price entry dictionaries.

    Returns:
        List of validated entries with start_time and price fields.
        Entries missing required fields are skipped with a warning.
    """
    if not entries:
        return []

    validated_entries = []
    for entry in entries:
        if not isinstance(entry, dict):
            logger.warning("Skipping non-dict entry: %s", entry)
            continue

        start_time = entry.get("start_time")
        price = entry.get("price")

        if start_time is None:
            logger.warning("Entry missing 'start_time': %s", entry)
            continue

        if price is None:
            logger.warning("Entry missing 'price': %s", entry)
            continue

        # Validate price is numeric
        if not isinstance(price, (int, float)):
            logger.warning("Entry has non-numeric price: %s", entry)
            continue

        validated_entries.append(
            {
                "start_time": start_time,
                "price": float(price),
            }
        )

    return validated_entries


def get_prices(
    start_datetime: datetime,
    end_datetime: datetime,
    service_caller: Callable[..., dict] | None = None,
) -> list[dict]:
    """Get normalized price data from Tibber service.

    Calls the tibber.get_prices Home Assistant service with the specified
    time range and returns a normalized list of price entries.

    Args:
        start_datetime: Start of the price range (datetime with timezone).
        end_datetime: End of the price range (datetime with timezone).
        service_caller: Optional callable to invoke the service.
            Signature: service_caller(start=str, end=str) -> dict
            If not provided, attempts to use Home Assistant service call.

    Returns:
        List of normalized price entries with start_time (ISO 8601 string)
        and price (float) keys. Returns empty list on error.
    """
    # Format datetimes as ISO 8601 strings for the service call
    start_str = start_datetime.isoformat()
    end_str = end_datetime.isoformat()

    try:
        if service_caller is not None:
            response = service_caller(start=start_str, end=end_str)
        else:
            # Default behavior: attempt Home Assistant service call
            # This would be replaced with actual HA service integration
            response = _call_ha_service(start_str, end_str)

        raw_entries = parse_service_response(response)
        return extract_price_entries(raw_entries)

    except Exception as e:
        logger.error("Failed to get prices from Tibber service: %s", e)
        return []


def _call_ha_service(start: str, end: str) -> dict[str, Any]:
    """Call the Home Assistant tibber.get_prices service.

    This is a placeholder for the actual Home Assistant service call.
    In production, this would integrate with HA's service call mechanism.

    Args:
        start: Start datetime as ISO 8601 string.
        end: End datetime as ISO 8601 string.

    Returns:
        Service response dictionary.

    Raises:
        NotImplementedError: When called without Home Assistant context.
    """
    # In a real HA integration, this would call:
    # hass.services.call("tibber", "get_prices", {"start": start, "end": end})
    raise NotImplementedError(
        "Home Assistant service call not available. "
        "Provide a service_caller function for testing."
    )
