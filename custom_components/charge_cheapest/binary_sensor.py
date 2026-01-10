"""Binary sensor platform for Charge Cheapest integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_CURRENT_SOC,
    ATTR_TOMORROW_PRICES_AVAILABLE,
    DOMAIN,
)
from .coordinator import TibberCheapestChargingCoordinator


@dataclass(frozen=True)
class TibberCheapestChargingBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes Charge Cheapest binary sensor entity."""

    value_fn: str | None = None


BINARY_SENSOR_DESCRIPTIONS: tuple[
    TibberCheapestChargingBinarySensorEntityDescription, ...
] = (
    TibberCheapestChargingBinarySensorEntityDescription(
        key="is_charging",
        translation_key="is_charging",
        name="Is Charging",
        icon="mdi:battery-charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        value_fn="is_charging",
    ),
    TibberCheapestChargingBinarySensorEntityDescription(
        key="is_cheap_hour",
        translation_key="is_cheap_hour",
        name="Is Cheap Hour",
        icon="mdi:cash-check",
        value_fn=None,  # Custom handling
    ),
    TibberCheapestChargingBinarySensorEntityDescription(
        key="prices_available_tomorrow",
        translation_key="prices_available_tomorrow",
        name="Prices Available Tomorrow",
        icon="mdi:calendar-arrow-right",
        value_fn=ATTR_TOMORROW_PRICES_AVAILABLE,
    ),
    TibberCheapestChargingBinarySensorEntityDescription(
        key="system_ready",
        translation_key="system_ready",
        name="System Ready",
        icon="mdi:check-circle",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn="system_ready",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Charge Cheapest binary sensor entities."""
    coordinator: TibberCheapestChargingCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    entities = [
        TibberCheapestChargingBinarySensor(coordinator, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    ]

    async_add_entities(entities)


class TibberCheapestChargingBinarySensor(
    CoordinatorEntity[TibberCheapestChargingCoordinator], BinarySensorEntity
):
    """Representation of a Charge Cheapest binary sensor."""

    entity_description: TibberCheapestChargingBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: TibberCheapestChargingCoordinator,
        description: TibberCheapestChargingBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description

        # Set entity IDs with charge_cheapest_ prefix
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{description.key}"
        self.entity_id = f"binary_sensor.charge_cheapest_{description.key}"

        # Device info
        self._attr_device_info = coordinator.device_info

        # Name
        self._attr_has_entity_name = True

    @property
    def is_on(self) -> bool | None:
        """Return True if the binary sensor is on."""
        if self.coordinator.data is None:
            return None

        # Special handling for is_cheap_hour
        if self.entity_description.key == "is_cheap_hour":
            return self._is_cheap_hour()

        # Use value_fn to get the value
        value_fn = self.entity_description.value_fn
        if value_fn:
            value = self.coordinator.data.get(value_fn)
            return bool(value) if value is not None else None

        return None

    def _is_cheap_hour(self) -> bool:
        """Check if current price is below daily average."""
        if self.coordinator.data is None:
            return False

        current_price = self.coordinator.data.get("current_price")
        if current_price is None:
            return False

        # Get price range and calculate average
        price_range = self.coordinator.data.get("price_range", "")
        if not price_range or price_range == "unavailable":
            return False

        try:
            # Parse price range "min - max"
            parts = price_range.split(" - ")
            if len(parts) == 2:
                min_price = float(parts[0])
                max_price = float(parts[1])
                avg_price = (min_price + max_price) / 2
                return current_price < avg_price
        except (ValueError, TypeError):
            pass

        return False

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if self.coordinator.data is None:
            return {}

        attrs = {}

        if self.entity_description.key == "is_charging":
            attrs[ATTR_CURRENT_SOC] = self.coordinator.data.get(ATTR_CURRENT_SOC)

        elif self.entity_description.key == "is_cheap_hour":
            attrs["current_price"] = self.coordinator.data.get("current_price")
            attrs["price_range"] = self.coordinator.data.get("price_range")

        elif self.entity_description.key == "prices_available_tomorrow":
            attrs[ATTR_TOMORROW_PRICES_AVAILABLE] = self.coordinator.data.get(
                ATTR_TOMORROW_PRICES_AVAILABLE
            )

        elif self.entity_description.key == "system_ready":
            attrs["status"] = self.coordinator.data.get("status")

        return attrs

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data is not None
