"""Dashboard auto-registration for Charge Cheapest integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall

from .const import (
    DASHBOARD_TITLE,
    DASHBOARD_URL_PATH,
    DOMAIN,
    SERVICE_RECREATE_DASHBOARD,
)

_LOGGER = logging.getLogger(__name__)


# Dashboard configuration converted from dashboards/charge_cheapest.yaml
DASHBOARD_CONFIG: dict[str, Any] = {
    "title": DASHBOARD_TITLE,
    "views": [
        # Overview Tab
        {
            "title": "Overview",
            "path": "overview",
            "icon": "mdi:battery-charging",
            "cards": [
                # Status Card
                {
                    "type": "entities",
                    "title": "Charging Status",
                    "show_header_toggle": False,
                    "entities": [
                        {
                            "entity": "sensor.charge_cheapest_status",
                            "name": "Status",
                        },
                        {
                            "entity": "sensor.charge_cheapest_current_price",
                            "name": "Current Price",
                        },
                        {
                            "entity": "sensor.charge_cheapest_next_window",
                            "name": "Next Window",
                        },
                        {
                            "entity": "binary_sensor.charge_cheapest_is_cheap_hour",
                            "name": "Cheap Hour",
                        },
                    ],
                },
                # Battery SOC Gauge (conditional)
                {
                    "type": "conditional",
                    "conditions": [
                        {
                            "condition": "state",
                            "entity": "binary_sensor.charge_cheapest_system_ready",
                            "state": "on",
                        }
                    ],
                    "card": {
                        "type": "gauge",
                        "name": "Target SOC",
                        "needle": True,
                        "min": 0,
                        "max": 100,
                        "severity": {"green": 60, "yellow": 30, "red": 0},
                        "entity": "sensor.charge_cheapest_target_soc",
                    },
                },
                # Price Chart - ApexCharts (conditional)
                {
                    "type": "conditional",
                    "conditions": [
                        {
                            "condition": "state",
                            "entity": "binary_sensor.charge_cheapest_system_ready",
                            "state": "on",
                        }
                    ],
                    "card": {
                        "type": "custom:apexcharts-card",
                        "header": {
                            "show": True,
                            "title": "Electricity Prices",
                            "show_states": True,
                            "colorize_states": True,
                        },
                        "graph_span": "48h",
                        "span": {"start": "day"},
                        "apex_config": {
                            "chart": {"height": "300px"},
                            "xaxis": {
                                "labels": {"datetimeFormatter": {"hour": "HH:mm"}}
                            },
                            "yaxis": {"decimalsInFloat": 3},
                            "tooltip": {"x": {"format": "dd MMM HH:mm"}},
                        },
                        "series": [
                            {
                                "entity": "sensor.charge_cheapest_current_price",
                                "name": "Price",
                                "type": "area",
                                "color": "#4CAF50",
                                "stroke_width": 2,
                                "opacity": 0.3,
                            }
                        ],
                    },
                },
                # Price Chart Fallback - History Graph
                {
                    "type": "history-graph",
                    "title": "Price History",
                    "hours_to_show": 24,
                    "entities": [
                        {
                            "entity": "sensor.charge_cheapest_current_price",
                            "name": "Price",
                        }
                    ],
                },
                # Cheapest Hours Info
                {
                    "type": "markdown",
                    "title": "Price Information",
                    "content": "**Today's Range:** {{ states('sensor.charge_cheapest_price_range') }}\n\n"
                    "**Current Price:** {{ states('sensor.charge_cheapest_current_price') }} EUR/kWh\n\n"
                    "**Tomorrow Available:** {{ 'Yes' if is_state('binary_sensor.charge_cheapest_prices_available_tomorrow', 'on') else 'No' }}\n\n"
                    "**Recommended SOC:** {{ states('sensor.charge_cheapest_recommended_soc') }}%",
                },
            ],
        },
        # Statistics Tab
        {
            "title": "Statistics",
            "path": "statistics",
            "icon": "mdi:chart-line",
            "cards": [
                # Savings Summary
                {
                    "type": "entities",
                    "title": "Savings Summary",
                    "show_header_toggle": False,
                    "entities": [
                        {
                            "entity": "sensor.charge_cheapest_estimated_savings",
                            "name": "Estimated Savings Today",
                        },
                    ],
                },
                # Charging Statistics
                {
                    "type": "entities",
                    "title": "Charging Information",
                    "show_header_toggle": False,
                    "entities": [
                        {
                            "entity": "sensor.charge_cheapest_charging_duration",
                            "name": "Charging Duration",
                        },
                        {
                            "entity": "sensor.charge_cheapest_target_soc",
                            "name": "Target SOC",
                        },
                    ],
                },
                # Charging Status History
                {
                    "type": "history-graph",
                    "title": "Charging Activity",
                    "hours_to_show": 48,
                    "entities": [
                        {
                            "entity": "binary_sensor.charge_cheapest_is_charging",
                            "name": "Charging",
                        }
                    ],
                },
                # Price History
                {
                    "type": "history-graph",
                    "title": "Price Trends",
                    "hours_to_show": 48,
                    "entities": [
                        {
                            "entity": "sensor.charge_cheapest_current_price",
                            "name": "Price",
                        }
                    ],
                },
                # Cost Comparison Card
                {
                    "type": "markdown",
                    "title": "Cost Analysis",
                    "content": "**Charging Strategy Performance**\n\n"
                    "*Daily Savings:* {{ states('sensor.charge_cheapest_estimated_savings') }} EUR\n\n"
                    "---\n\n"
                    "*Tip: Charging during cheap hours can save 20-50% compared to average grid prices.*",
                },
            ],
        },
        # Configuration Tab
        {
            "title": "Configuration",
            "path": "configuration",
            "icon": "mdi:cog",
            "cards": [
                # Validation Status
                {
                    "type": "entities",
                    "title": "System Status",
                    "show_header_toggle": False,
                    "entities": [
                        {
                            "entity": "binary_sensor.charge_cheapest_system_ready",
                            "name": "All Dependencies OK",
                            "icon": "mdi:check-circle",
                        },
                        {
                            "entity": "binary_sensor.charge_cheapest_prices_available_tomorrow",
                            "name": "Tomorrow Prices Available",
                            "icon": "mdi:calendar-check",
                        },
                    ],
                },
                # Configuration Status OK
                {
                    "type": "conditional",
                    "conditions": [
                        {
                            "condition": "state",
                            "entity": "binary_sensor.charge_cheapest_system_ready",
                            "state": "on",
                        }
                    ],
                    "card": {
                        "type": "markdown",
                        "content": "**Configuration Status: OK**\n\n"
                        "All required entities are configured and responding correctly.",
                    },
                },
                # Configuration Status Incomplete
                {
                    "type": "conditional",
                    "conditions": [
                        {
                            "condition": "state",
                            "entity": "binary_sensor.charge_cheapest_system_ready",
                            "state": "off",
                        }
                    ],
                    "card": {
                        "type": "markdown",
                        "content": "**Configuration Status: Incomplete**\n\n"
                        "Please check the integration configuration:\n"
                        "1. Verify your price sensor entity ID\n"
                        "2. Verify your battery SOC sensor entity ID\n"
                        "3. Verify your battery charging switch entity ID\n\n"
                        "Go to Settings > Devices & Services > Charge Cheapest to reconfigure.",
                    },
                },
                # System Information
                {
                    "type": "markdown",
                    "title": "System Information",
                    "content": "**Charge Cheapest**\n\n"
                    "*Version:* 1.0.0\n\n"
                    "*Status:* {{ 'Connected' if is_state('binary_sensor.charge_cheapest_system_ready', 'on') else 'Configuration Required' }}\n\n"
                    "*Charging Status:* {{ states('sensor.charge_cheapest_status') }}\n\n"
                    "---\n\n"
                    "**Documentation**\n\n"
                    "For setup instructions and troubleshooting, visit the GitHub repository.\n\n"
                    "**Note:** To install ApexCharts for price visualization, add the custom:apexcharts-card via HACS.",
                },
            ],
        },
    ],
}


async def async_setup_dashboard(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up the dashboard on first integration setup."""
    # Check if dashboard already exists
    if await _dashboard_exists(hass):
        _LOGGER.debug("Dashboard already exists, skipping creation")
        return

    # Create dashboard
    await _create_dashboard(hass)


async def async_register_dashboard_service(hass: HomeAssistant) -> None:
    """Register the recreate_dashboard service."""
    if hass.services.has_service(DOMAIN, SERVICE_RECREATE_DASHBOARD):
        return

    async def handle_recreate_dashboard(call: ServiceCall) -> None:
        """Handle the recreate_dashboard service call."""
        _LOGGER.info("Recreating dashboard...")

        # Delete existing dashboard if present
        await _delete_dashboard(hass)

        # Create fresh dashboard
        await _create_dashboard(hass)

        _LOGGER.info("Dashboard recreated successfully")

    hass.services.async_register(
        DOMAIN,
        SERVICE_RECREATE_DASHBOARD,
        handle_recreate_dashboard,
    )


async def _dashboard_exists(hass: HomeAssistant) -> bool:
    """Check if the dashboard already exists."""
    try:
        # Check in lovelace storage
        lovelace_config = hass.data.get("lovelace", {})

        # Check dashboards collection
        dashboards = lovelace_config.get("dashboards", {})
        if DASHBOARD_URL_PATH in dashboards:
            return True

        # Also check using the lovelace component
        from homeassistant.components.lovelace import DOMAIN as LOVELACE_DOMAIN

        if LOVELACE_DOMAIN in hass.data:
            lovelace_data = hass.data[LOVELACE_DOMAIN]
            if hasattr(lovelace_data, "dashboards"):
                return DASHBOARD_URL_PATH in lovelace_data.dashboards

    except Exception as err:
        _LOGGER.debug("Could not check dashboard existence: %s", err)

    return False


async def _create_dashboard(hass: HomeAssistant) -> None:
    """Create the dashboard."""
    try:
        # Use storage collection to create dashboard
        from homeassistant.components.lovelace import DOMAIN as LOVELACE_DOMAIN
        from homeassistant.components.lovelace.const import (
            CONF_URL_PATH,
            CONF_REQUIRE_ADMIN,
            CONF_SHOW_IN_SIDEBAR,
            MODE_STORAGE,
        )

        # Create dashboard configuration
        dashboard_data = {
            "id": DASHBOARD_URL_PATH,
            CONF_URL_PATH: DASHBOARD_URL_PATH,
            "title": DASHBOARD_TITLE,
            "icon": "mdi:battery-charging",
            CONF_SHOW_IN_SIDEBAR: True,
            CONF_REQUIRE_ADMIN: False,
            "mode": MODE_STORAGE,
        }

        # Store dashboard views
        lovelace_config = DASHBOARD_CONFIG.copy()

        # Try to create using lovelace storage
        if LOVELACE_DOMAIN in hass.data:
            lovelace_data = hass.data[LOVELACE_DOMAIN]

            # Try different methods to create dashboard
            if hasattr(lovelace_data, "dashboards"):
                try:
                    dashboards_collection = lovelace_data.dashboards
                    if hasattr(dashboards_collection, "async_create_item"):
                        await dashboards_collection.async_create_item(dashboard_data)
                        _LOGGER.info("Dashboard created via dashboards collection")

                        # Store the config
                        await _store_dashboard_config(hass, lovelace_config)
                        return
                except Exception as err:
                    _LOGGER.debug("Could not create via dashboards collection: %s", err)

        # Fallback: Store dashboard config directly
        await _store_dashboard_config(hass, lovelace_config)
        _LOGGER.info("Dashboard configuration stored")

    except Exception as err:
        _LOGGER.error("Failed to create dashboard: %s", err)


async def _store_dashboard_config(hass: HomeAssistant, config: dict) -> None:
    """Store dashboard configuration in Home Assistant storage."""
    try:
        from homeassistant.helpers.storage import Store

        store = Store(hass, 1, f"lovelace.{DASHBOARD_URL_PATH}")
        await store.async_save({"data": config})
        _LOGGER.debug("Dashboard config stored")
    except Exception as err:
        _LOGGER.warning("Could not store dashboard config: %s", err)


async def _delete_dashboard(hass: HomeAssistant) -> None:
    """Delete the existing dashboard."""
    try:
        from homeassistant.components.lovelace import DOMAIN as LOVELACE_DOMAIN

        if LOVELACE_DOMAIN in hass.data:
            lovelace_data = hass.data[LOVELACE_DOMAIN]

            if hasattr(lovelace_data, "dashboards"):
                try:
                    dashboards_collection = lovelace_data.dashboards
                    if DASHBOARD_URL_PATH in dashboards_collection:
                        if hasattr(dashboards_collection, "async_delete_item"):
                            await dashboards_collection.async_delete_item(
                                DASHBOARD_URL_PATH
                            )
                            _LOGGER.info("Existing dashboard deleted")
                            return
                except Exception as err:
                    _LOGGER.debug("Could not delete via dashboards collection: %s", err)

        # Fallback: Try to remove storage file
        try:
            from homeassistant.helpers.storage import Store

            store = Store(hass, 1, f"lovelace.{DASHBOARD_URL_PATH}")
            await store.async_remove()
            _LOGGER.debug("Dashboard storage removed")
        except Exception:
            pass

    except Exception as err:
        _LOGGER.debug("Could not delete dashboard: %s", err)
