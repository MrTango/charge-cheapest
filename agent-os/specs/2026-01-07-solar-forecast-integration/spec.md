# Specification: Solar Forecast Integration

## Goal

Integrate solar production forecasts from the Forecast.Solar API into the battery charging optimization system to calculate optimal morning SOC targets based on expected solar production, morning consumption patterns, and battery headroom requirements.

## User Stories

- As a home battery owner, I want my charging system to automatically lower my morning SOC target based on expected solar production so that my battery has headroom to capture incoming solar energy during the day.
- As a user, I want to see a Home Assistant sensor showing the calculated optimal SOC target with configurable logging detail so that I can understand and verify the system's recommendations.

## Specific Requirements

**Forecast.Solar API Integration**
- Integrate with Forecast.Solar free API endpoint for solar production forecasts
- Use existing Home Assistant solar system sensor values (latitude, longitude, panel azimuth, panel tilt, peak power) rather than requiring duplicate blueprint inputs
- API endpoint format: `https://api.forecast.solar/estimate/{lat}/{lon}/{dec}/{az}/{kwp}`
- Parse API response to extract expected daily kWh production for the forecast period
- Handle API rate limits appropriately (free tier allows 12 requests per hour)

**Hourly Polling Schedule**
- Poll the Forecast.Solar API every hour to capture updated forecasts
- Use Home Assistant time-based trigger pattern consistent with existing blueprint triggers
- Store the latest forecast result in a template sensor for use in SOC calculations
- Continue polling during daylight hours; optionally reduce frequency at night

**SOC Calculation Logic**
- Calculate optimal morning SOC using formula: `target_soc = default_night_target - (expected_solar_kwh - morning_consumption_kwh - headroom_offset_kwh) / battery_capacity_kwh * 100`
- Clamp result between configurable minimum SOC floor (e.g., 20%) and the default night target SOC
- Morning consumption is a manual kWh input representing expected usage between wake time and solar production start
- Headroom offset is a user-configurable +/- kWh adjustment for tuning

**Blueprint Input Configuration**
- Add input for morning consumption estimate in kWh (manual value)
- Add input for SOC offset adjustment (+/- kWh for calculation tuning)
- Add input for minimum SOC floor percentage (lower bound for calculated target)
- Add toggle for detailed vs basic logging mode
- Rely on existing Home Assistant sensors for solar system parameters (no duplicate inputs)

**Sensor Output**
- Expose calculated optimal morning SOC as a Home Assistant template sensor
- Sensor should update whenever a new forecast is received
- Include sensor attributes: expected solar kWh, morning consumption kWh, offset applied, calculation timestamp, forecast source

**Logging and Diagnostics**
- Basic logging mode: "Target SOC: 45% (expected solar: 12 kWh, morning consumption: 5 kWh)"
- Detailed logging mode: Include battery headroom calculation breakdown, forecast API response timestamp, raw forecast values, and calculation formula steps
- Use Home Assistant persistent notification for logging output, consistent with existing blueprint patterns

**Fallback Behavior**
- When Forecast.Solar API is unavailable or returns an error, fall back to the user's configured default night target SOC
- Log a warning notification when fallback is activated
- Implement retry with exponential backoff for transient API failures (max 3 retries)

**Integration with Existing Night Charging**
- The calculated optimal SOC should be used as the target for the night charging schedule
- Replace or override the static `night_target_soc` input when solar forecast is available
- Maintain backward compatibility: if solar forecast feature is disabled, use existing static target

## Visual Design

No visual assets provided.

## Existing Code to Leverage

**Blueprint input pattern (`/workspace/blueprints/automation/charge_cheapest.yaml`)**
- Follow existing input selector patterns for time, number, boolean, and entity inputs
- Use consistent naming conventions (snake_case with descriptive names)
- Replicate input grouping with section comments for organization
- Leverage existing SOC target inputs as reference (night_target_soc, day_target_soc)

**Duration calculator module (`/workspace/tibber_prices/duration_calculator.py`)**
- Reuse `convert_capacity_to_kwh()` function for battery capacity unit conversion
- Follow `validate_calculation_inputs()` pattern for input validation
- Apply similar logging patterns with debug, info, and warning levels
- Use the same 0-100 SOC range validation approach

**Tibber price service pattern (`/workspace/tibber_prices/tibber_price_service.py`)**
- Follow `parse_service_response()` pattern for parsing external API responses
- Implement similar `extract_*_entries()` pattern for validating API data
- Use callable service_caller pattern for testability
- Apply same error handling with logging for API failures

**Notification system (`/workspace/tibber_prices/notifications.py`)**
- Extend `NotificationType` enum with new solar forecast notification types if needed
- Follow `build_notification_message()` pattern for constructing log messages
- Use `create_notification_payload()` for Home Assistant notification service calls
- Maintain consistent notification_id naming scheme

**Night charging orchestration (`/workspace/tibber_prices/night_charging.py`)**
- Follow `execute_night_charging_automation()` workflow pattern for integration
- Apply similar SOC check and skip condition logic
- Use same fallback behavior pattern (skip, default, immediate) where applicable
- Leverage `_parse_numeric_sensor_value()` for extracting sensor states

## Out of Scope

- Automatic adjustment based on weather uncertainty or cloud cover probability
- Multiple solar array support (east/west facing panels with different forecasts)
- Integration with alternative forecast providers (Solcast, Open-Meteo, Tibber solar)
- Historical accuracy tracking comparing forecasts vs actual production
- Machine learning or adaptive adjustment based on past forecast accuracy
- Intraday re-optimization (recalculating during the day based on actual production)
- Integration with EV charging schedules
- Cost optimization considering solar self-consumption vs grid export rates
- Weather alert integration for storm or snow cover warnings
- Graphical dashboard or visualization components
