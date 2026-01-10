"""Constants for the Tibber Cheapest Charging integration."""

from typing import Final

# Domain
DOMAIN: Final = "tibber_cheapest_charging"

# Platforms
PLATFORMS: Final = ["sensor", "binary_sensor"]

# Version
VERSION: Final = "1.0.0"

# Configuration keys - Entity selection
CONF_BATTERY_SOC_SENSOR: Final = "battery_soc_sensor"
CONF_BATTERY_CHARGING_SWITCH: Final = "battery_charging_switch"
CONF_PRICE_SENSOR: Final = "price_sensor"
CONF_SOLAR_FORECAST_SENSOR: Final = "solar_forecast_sensor"
CONF_BATTERY_CAPACITY_SENSOR: Final = "battery_capacity_sensor"
CONF_BATTERY_CHARGING_POWER: Final = "battery_charging_power"

# Configuration keys - Schedule times
CONF_NIGHT_START_TIME: Final = "night_start_time"
CONF_NIGHT_END_TIME: Final = "night_end_time"
CONF_DAY_SCHEDULE_ENABLED: Final = "day_schedule_enabled"
CONF_DAY_START_TIME: Final = "day_start_time"
CONF_DAY_END_TIME: Final = "day_end_time"
CONF_EVENING_PEAK_START: Final = "evening_peak_start"
CONF_EVENING_PEAK_END: Final = "evening_peak_end"

# Configuration keys - SOC targets
CONF_NIGHT_TARGET_SOC: Final = "night_target_soc"
CONF_DAY_TARGET_SOC: Final = "day_target_soc"
CONF_EVENING_PEAK_TARGET_SOC: Final = "evening_peak_target_soc"
CONF_TARGET_SOC: Final = "target_soc"

# Configuration keys - Charging behavior
CONF_CHARGING_DURATION_HOURS: Final = "charging_duration_hours"
CONF_TRIGGER_TIME: Final = "trigger_time"
CONF_FAILURE_BEHAVIOR: Final = "failure_behavior"
CONF_DEFAULT_CHARGE_START_TIME: Final = "default_charge_start_time"
CONF_DEFAULT_CHARGE_DURATION: Final = "default_charge_duration"

# Configuration keys - Notifications
CONF_NOTIFICATION_SERVICE: Final = "notification_service"
CONF_NOTIFY_CHARGING_SCHEDULED: Final = "notify_charging_scheduled"
CONF_NOTIFY_CHARGING_STARTED: Final = "notify_charging_started"
CONF_NOTIFY_CHARGING_COMPLETED: Final = "notify_charging_completed"
CONF_NOTIFY_CHARGING_SKIPPED: Final = "notify_charging_skipped"
CONF_NOTIFY_CHARGING_ERROR: Final = "notify_charging_error"
CONF_NOTIFY_EMERGENCY_CHARGING: Final = "notify_emergency_charging"

# Configuration keys - Solar forecast
CONF_SOLAR_FORECAST_ENABLED: Final = "solar_forecast_enabled"
CONF_FORECAST_MODE_AUTOMATIC: Final = "forecast_mode_automatic"
CONF_MORNING_CONSUMPTION_KWH: Final = "morning_consumption_kwh"
CONF_SOC_OFFSET_KWH: Final = "soc_offset_kwh"
CONF_MINIMUM_SOC_FLOOR: Final = "minimum_soc_floor"

# Default values - Schedule times
DEFAULT_NIGHT_START_TIME: Final = "23:00:00"
DEFAULT_NIGHT_END_TIME: Final = "06:00:00"
DEFAULT_DAY_START_TIME: Final = "09:00:00"
DEFAULT_DAY_END_TIME: Final = "16:00:00"
DEFAULT_EVENING_PEAK_START: Final = "17:00:00"
DEFAULT_EVENING_PEAK_END: Final = "21:00:00"
DEFAULT_TRIGGER_TIME: Final = "22:30:00"
DEFAULT_DEFAULT_CHARGE_START_TIME: Final = "01:00:00"

# Default values - SOC targets
DEFAULT_NIGHT_TARGET_SOC: Final = 60
DEFAULT_DAY_TARGET_SOC: Final = 50
DEFAULT_EVENING_PEAK_TARGET_SOC: Final = 50
DEFAULT_TARGET_SOC: Final = 80
DEFAULT_MINIMUM_SOC_FLOOR: Final = 20

# Default values - Charging behavior
DEFAULT_CHARGING_DURATION_HOURS: Final = 3.0
DEFAULT_DEFAULT_CHARGE_DURATION: Final = 3.0
DEFAULT_DAY_SCHEDULE_ENABLED: Final = False
DEFAULT_FAILURE_BEHAVIOR: Final = "skip_charging"

# Default values - Notifications
DEFAULT_NOTIFICATION_SERVICE: Final = "persistent_notification.create"
DEFAULT_NOTIFY_CHARGING_SCHEDULED: Final = True
DEFAULT_NOTIFY_CHARGING_STARTED: Final = True
DEFAULT_NOTIFY_CHARGING_COMPLETED: Final = True
DEFAULT_NOTIFY_CHARGING_SKIPPED: Final = True
DEFAULT_NOTIFY_CHARGING_ERROR: Final = True
DEFAULT_NOTIFY_EMERGENCY_CHARGING: Final = True

# Default values - Solar forecast
DEFAULT_SOLAR_FORECAST_ENABLED: Final = False
DEFAULT_FORECAST_MODE_AUTOMATIC: Final = False
DEFAULT_MORNING_CONSUMPTION_KWH: Final = 3.0
DEFAULT_SOC_OFFSET_KWH: Final = 0.0

# Failure behavior options
FAILURE_BEHAVIOR_SKIP: Final = "skip_charging"
FAILURE_BEHAVIOR_DEFAULT_WINDOW: Final = "use_default_window"
FAILURE_BEHAVIOR_CHARGE_IMMEDIATELY: Final = "charge_immediately"

FAILURE_BEHAVIORS: Final = [
    FAILURE_BEHAVIOR_SKIP,
    FAILURE_BEHAVIOR_DEFAULT_WINDOW,
    FAILURE_BEHAVIOR_CHARGE_IMMEDIATELY,
]

# Charging status states
STATUS_IDLE: Final = "idle"
STATUS_SCHEDULED: Final = "scheduled"
STATUS_CHARGING: Final = "charging"
STATUS_DISABLED: Final = "disabled"
STATUS_ERROR: Final = "error"

# Coordinator update interval (minutes)
COORDINATOR_UPDATE_INTERVAL: Final = 5

# Efficiency factor for charging calculations
CHARGING_EFFICIENCY: Final = 0.95

# Time slot granularity (15 minutes = 0.25 hours)
TIME_SLOT_HOURS: Final = 0.25

# Emergency check buffer (minutes before evening peak)
EMERGENCY_CHECK_BUFFER_MINUTES: Final = 60

# Service names
SERVICE_RECREATE_DASHBOARD: Final = "recreate_dashboard"

# Dashboard configuration
DASHBOARD_URL_PATH: Final = "charge-cheapest"
DASHBOARD_TITLE: Final = "Charge Cheapest"

# Device info
DEVICE_MANUFACTURER: Final = "Tibber Cheapest Charging"
DEVICE_MODEL: Final = "Smart Battery Charging"

# Attributes
ATTR_NEXT_WINDOW_START: Final = "next_window_start"
ATTR_NEXT_WINDOW_END: Final = "next_window_end"
ATTR_ESTIMATED_COST: Final = "estimated_cost"
ATTR_CHARGING_DURATION: Final = "charging_duration"
ATTR_TARGET_SOC: Final = "target_soc"
ATTR_CURRENT_SOC: Final = "current_soc"
ATTR_TOMORROW_PRICES_AVAILABLE: Final = "tomorrow_prices_available"
ATTR_CALCULATION_TIMESTAMP: Final = "calculation_timestamp"
ATTR_SOLAR_FORECAST_KWH: Final = "solar_forecast_kwh"
ATTR_OPTIMAL_SOC_TARGET: Final = "optimal_soc_target"
