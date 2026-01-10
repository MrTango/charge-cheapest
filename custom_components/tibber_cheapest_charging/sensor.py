"""Sensor platform for Tibber Cheapest Charging integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_CALCULATION_TIMESTAMP,
    ATTR_CHARGING_DURATION,
    ATTR_CURRENT_SOC,
    ATTR_ESTIMATED_COST,
    ATTR_NEXT_WINDOW_END,
    ATTR_NEXT_WINDOW_START,
    ATTR_OPTIMAL_SOC_TARGET,
    ATTR_TARGET_SOC,
    ATTR_TOMORROW_PRICES_AVAILABLE,
    DOMAIN,
)
from .coordinator import TibberCheapestChargingCoordinator


@dataclass(frozen=True)
class TibberCheapestChargingSensorEntityDescription(SensorEntityDescription):
    """Describes Tibber Cheapest Charging sensor entity."""

    value_fn: str | None = None
    attr_fn: dict[str, str] | None = None


SENSOR_DESCRIPTIONS: tuple[TibberCheapestChargingSensorEntityDescription, ...] = (
    TibberCheapestChargingSensorEntityDescription(
        key="status",
        translation_key="charging_status",
        name="Charging Status",
        icon="mdi:battery-sync",
        value_fn="status",
    ),
    TibberCheapestChargingSensorEntityDescription(
        key="current_price",
        translation_key="current_price",
        name="Current Price",
        icon="mdi:currency-eur",
        native_unit_of_measurement="EUR/kWh",
        device_class=SensorDeviceClass.MONETARY,
        value_fn="current_price",
    ),
    TibberCheapestChargingSensorEntityDescription(
        key="next_window",
        translation_key="next_window",
        name="Next Charging Window",
        icon="mdi:clock-time-four",
        value_fn=None,  # Custom handling
    ),
    TibberCheapestChargingSensorEntityDescription(
        key="recommended_soc",
        translation_key="recommended_soc",
        name="Recommended SOC",
        icon="mdi:battery-charging-medium",
        native_unit_of_measurement=PERCENTAGE,
        value_fn=ATTR_OPTIMAL_SOC_TARGET,
    ),
    TibberCheapestChargingSensorEntityDescription(
        key="price_range",
        translation_key="price_range",
        name="Price Range Today",
        icon="mdi:chart-line-variant",
        value_fn="price_range",
    ),
    TibberCheapestChargingSensorEntityDescription(
        key="estimated_savings",
        translation_key="estimated_savings",
        name="Estimated Savings Today",
        icon="mdi:piggy-bank",
        native_unit_of_measurement="EUR",
        device_class=SensorDeviceClass.MONETARY,
        value_fn="estimated_savings",
    ),
    TibberCheapestChargingSensorEntityDescription(
        key="charging_duration",
        translation_key="charging_duration",
        name="Charging Duration",
        icon="mdi:timer",
        native_unit_of_measurement="h",
        value_fn=ATTR_CHARGING_DURATION,
    ),
    TibberCheapestChargingSensorEntityDescription(
        key="target_soc",
        translation_key="target_soc",
        name="Target SOC",
        icon="mdi:battery-charging-high",
        native_unit_of_measurement=PERCENTAGE,
        value_fn=ATTR_TARGET_SOC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tibber Cheapest Charging sensor entities."""
    coordinator: TibberCheapestChargingCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    entities = [
        TibberCheapestChargingSensor(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    ]

    async_add_entities(entities)


class TibberCheapestChargingSensor(
    CoordinatorEntity[TibberCheapestChargingCoordinator], SensorEntity
):
    """Representation of a Tibber Cheapest Charging sensor."""

    entity_description: TibberCheapestChargingSensorEntityDescription

    def __init__(
        self,
        coordinator: TibberCheapestChargingCoordinator,
        description: TibberCheapestChargingSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description

        # Set entity IDs with charge_cheapest_ prefix
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{description.key}"
        self.entity_id = f"sensor.charge_cheapest_{description.key}"

        # Device info
        self._attr_device_info = coordinator.device_info

        # Name
        self._attr_has_entity_name = True

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None

        # Special handling for next_window
        if self.entity_description.key == "next_window":
            return self._format_next_window()

        # Use value_fn to get the value
        value_fn = self.entity_description.value_fn
        if value_fn:
            return self.coordinator.data.get(value_fn)

        return None

    def _format_next_window(self) -> str:
        """Format the next charging window as a time range."""
        if self.coordinator.data is None:
            return "Unknown"

        start = self.coordinator.data.get(ATTR_NEXT_WINDOW_START)
        end = self.coordinator.data.get(ATTR_NEXT_WINDOW_END)

        if not start or not end:
            failure_mode = self.coordinator.data.get("failure_mode")
            if failure_mode == "skip":
                return "Skipped"
            return "Not scheduled"

        # Format as HH:MM - HH:MM
        start_formatted = start[:5] if isinstance(start, str) and len(start) >= 5 else str(start)
        end_formatted = end[:5] if isinstance(end, str) and len(end) >= 5 else str(end)

        return f"{start_formatted} - {end_formatted}"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if self.coordinator.data is None:
            return {}

        attrs = {}

        # Common attributes
        if self.entity_description.key == "status":
            attrs[ATTR_CURRENT_SOC] = self.coordinator.data.get(ATTR_CURRENT_SOC)
            attrs[ATTR_TARGET_SOC] = self.coordinator.data.get(ATTR_TARGET_SOC)
            attrs["is_charging"] = self.coordinator.data.get("is_charging", False)
            attrs["system_ready"] = self.coordinator.data.get("system_ready", False)

        elif self.entity_description.key == "next_window":
            attrs[ATTR_NEXT_WINDOW_START] = self.coordinator.data.get(ATTR_NEXT_WINDOW_START)
            attrs[ATTR_NEXT_WINDOW_END] = self.coordinator.data.get(ATTR_NEXT_WINDOW_END)
            attrs[ATTR_ESTIMATED_COST] = self.coordinator.data.get(ATTR_ESTIMATED_COST)
            attrs[ATTR_CHARGING_DURATION] = self.coordinator.data.get(ATTR_CHARGING_DURATION)
            attrs["failure_mode"] = self.coordinator.data.get("failure_mode")

        elif self.entity_description.key == "recommended_soc":
            attrs[ATTR_OPTIMAL_SOC_TARGET] = self.coordinator.data.get(ATTR_OPTIMAL_SOC_TARGET)
            attrs[ATTR_CALCULATION_TIMESTAMP] = self.coordinator.data.get(ATTR_CALCULATION_TIMESTAMP)

        elif self.entity_description.key == "current_price":
            attrs[ATTR_TOMORROW_PRICES_AVAILABLE] = self.coordinator.data.get(
                ATTR_TOMORROW_PRICES_AVAILABLE
            )

        return attrs

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data is not None
