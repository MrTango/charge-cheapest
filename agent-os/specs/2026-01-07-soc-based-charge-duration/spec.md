# Specification: SOC-Based Charge Duration

## Goal

Add dynamic charging duration calculation based on current battery SOC, target SOC, battery capacity, and charge rate, replacing the fixed `charging_duration_hours` input with an intelligent calculation that automatically determines required charging time.

## User Stories

- As a homeowner with a battery system, I want the automation to automatically calculate how long to charge based on my current SOC so that I only charge for the exact time needed to reach my target SOC.
- As an energy-conscious user, I want charging efficiency losses accounted for in the duration calculation so that my battery actually reaches the target SOC.

## Specific Requirements

**Dynamic Charging Duration Calculation**
- Calculate required charging hours using formula: `hours = ((target_soc - current_soc) / 100) * capacity_kwh / (charge_power_kw * 0.95)`
- Read current SOC from existing `battery_soc_sensor` entity
- Read target SOC from existing `target_soc` input
- Read charging power from existing `battery_charging_power` input_number entity
- Read battery capacity from new `battery_capacity_sensor` input
- Apply 95% efficiency factor to account for charging losses
- Round up calculated duration to nearest 15-minute slot (0.25 hours)

**Battery Capacity Sensor Unit Detection**
- Read `unit_of_measurement` attribute from battery capacity sensor at runtime
- Convert Wh to kWh by dividing by 1000 when unit contains "wh" but not "kwh" (case-insensitive)
- Use value directly when unit is "kWh" or "kwh"
- Default to kWh interpretation if unit attribute is missing or unrecognized
- Handle variations like "Wh", "wh", "WH", "kWh", "kwh", "KWH"

**Minimum Duration Enforcement**
- Enforce minimum charging duration of 15 minutes (0.25 hours)
- If calculated duration is less than 15 minutes but greater than zero, use 15 minutes
- If calculated duration is zero or negative (SOC already at or above target), return 0 to skip charging

**New Blueprint Input for Battery Capacity**
- Add `battery_capacity_sensor` input with entity selector (domain: sensor)
- Description: "Sensor entity for battery maximum capacity (auto-detects Wh or kWh)"
- Example entity: `sensor.byd_battery_box_premium_hv_maximum_capacity`
- No default value (required input)

**Fallback Behavior on Calculation Failure**
- Fall back to existing `charging_duration_hours` input if dynamic calculation fails
- Failure conditions: sensor unavailable, invalid/non-numeric values, zero capacity, zero charge power
- Log warning message when fallback is used for debugging purposes
- Continue automation execution with fallback rather than failing entirely

**Integration with Existing Cheapest Hours Logic**
- Replace static `charging_duration_hours` with dynamically calculated value
- Pass calculated duration to `find_cheapest_slots()` function via `duration_hours` parameter
- Maintain compatibility with existing 15-minute slot granularity in `slot_calculator.py`
- Calculation runs at automation trigger time before cheapest window calculation

**Expose Calculated Duration for User Visibility**
- Store calculated duration in a template variable for use in notifications
- Include calculated duration in scheduled notification messages
- Allow users to see why a particular charging window length was chosen

**Input Validation and Error Handling**
- Validate all sensor values are numeric and positive before calculation
- Handle unavailable/unknown sensor states gracefully with fallback
- Validate target_soc and current_soc are within 0-100 range
- Return 0 duration (skip charging) if current_soc >= target_soc

## Existing Code to Leverage

**`/workspace/blueprints/automation/charge_cheapest.yaml`**
- Reuse existing `battery_soc_sensor` entity selector and reference pattern
- Reuse existing `target_soc` number input configuration
- Reuse existing `battery_charging_power` input_number entity reference
- Use `charging_duration_hours` as the fallback value when dynamic calculation fails
- Follow existing input selector patterns for the new battery capacity sensor input

**`/workspace/tibber_prices/slot_calculator.py`**
- Use `convert_duration_to_slots()` function to convert calculated hours to 15-minute slots
- `find_cheapest_slots()` already accepts `duration_hours` parameter for dynamic durations
- `SLOTS_PER_HOUR = 4` constant confirms 15-minute granularity
- Reuse `math.ceil()` pattern for rounding up to nearest slot

**`/workspace/tibber_prices/night_charging.py`**
- `execute_night_charging_automation()` receives `charging_duration_hours` parameter to replace with dynamic value
- `check_soc_skip_condition()` already handles SOC threshold logic (reuse pattern for validation)
- Existing notification context structure can be extended to include calculated duration
- Fallback schedule pattern in `get_fallback_schedule()` shows how to handle failures gracefully

**`/workspace/tibber_prices/price_normalizer.py`**
- Reference `parse_timestamp()` for any timestamp handling if needed
- Follow existing validation and error handling patterns

## Out of Scope

- Solar forecast integration for adjusting target SOC based on expected generation
- Support for multiple battery capacity sensors
- Manual override option to choose between fixed and dynamic duration modes
- Historical data analysis for optimizing charge rate estimates
- Temperature-based charging adjustments or derating
- Dynamic efficiency factor based on battery temperature or state of health
- Real-time adjustment of charging duration during the charging window
- Battery degradation tracking or health-based adjustments
- Grid export optimization or vehicle-to-grid features
- Multi-battery system coordination
