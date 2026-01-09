# Spec Requirements: SOC-Based Charge Duration

## Initial Description

SOC-Based Charge Duration - Add logic to calculate required charging hours based on current battery SOC, target SOC, and battery capacity/charge rate. Dynamically adjust the hours parameter passed to the cheapest hours calculation.

This is Roadmap Item #6, building on the completed foundation:
- #1 Blueprint Configuration Schema (complete)
- #2 Tibber Get Prices Service Integration (complete)
- #3 Cross-Midnight Price Fetching (complete)
- #4 Cheapest Hours Calculation Logic (complete)
- #5 Night Charging Automation (complete)

## Requirements Discussion

### First Round Questions

**Q1:** For battery capacity, I assume we need an input for the total battery capacity in kWh. Should this be a manual number input, or should we read it from a sensor entity (e.g., from the battery integration)?
**Answer:** Use a sensor entity for battery capacity. The sensor `sensor.byd_battery_box_premium_hv_maximum_capacity` provides this value.

**Q2:** For charge rate, I assume we need the maximum charging power. Should this use the existing `battery_charging_power` input_number entity already defined in the blueprint, or do you need a separate configuration?
**Answer:** Use the existing `battery_charging_power` input_number entity from the blueprint configuration.

**Q3:** For the calculation formula, I'm planning to use: `charging_hours = ((target_soc - current_soc) / 100) * capacity_kwh / charge_power_kw`. Is this the correct approach, or do you have a specific formula preference?
**Answer:** Yes, that formula is correct.

**Q4:** For efficiency losses, should we add a configurable efficiency factor (e.g., 90%) to account for charging losses, or assume 100% efficiency for simplicity?
**Answer:** Use 95% efficiency factor to account for charging losses.

**Q5:** For minimum charging duration, should we enforce a minimum (e.g., 15 minutes) to avoid scheduling very short charging windows that might not be practical?
**Answer:** Yes, enforce a minimum charging duration of 15 minutes.

**Q6:** For the output, should the calculated duration replace the fixed `charging_duration_hours` input entirely, or should users be able to choose between fixed and dynamic duration modes?
**Answer:** Replace the fixed duration with dynamic calculation. The fixed input can remain as a fallback/default if calculation fails.

**Q7:** Is there anything specific you want to exclude from this feature that might seem like an obvious inclusion?
**Answer:** No additional exclusions mentioned.

### Follow-up Questions

**Follow-up 1:** For the battery capacity sensor, does it report in Wh or kWh? This affects whether we need a conversion factor in the calculation.
**Answer:** The sensor has a `unit_of_measurement` attribute that can be read to determine if the value is in Wh or kWh. The sensor also has a `friendly_name` attribute. The blueprint can dynamically detect the unit at runtime and apply the appropriate conversion factor (divide by 1000 if Wh, use directly if kWh).

**Battery capacity sensor attributes:**
- `sensor.byd_battery_box_premium_hv_maximum_capacity.unit_of_measurement` - can be read to determine if Wh or kWh
- `sensor.byd_battery_box_premium_hv_maximum_capacity.friendly_name` - also available

### Existing Code to Reference

**Similar Features Identified:**
- Feature: Night Charging Automation - Path: `/workspace/blueprints/automation/charge_cheapest.yaml`
- Components to potentially reuse:
  - `battery_charging_power` input_number entity already exists in blueprint
  - `battery_soc_sensor` entity already exists for current SOC reading
  - `target_soc` input already exists for target SOC threshold
  - `charging_duration_hours` input will be replaced/enhanced by dynamic calculation
- Backend logic to reference: Cheapest hours calculation logic already handles duration parameter

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
Not applicable.

## Requirements Summary

### Functional Requirements

**Core Calculation Logic:**
- Calculate required charging duration dynamically based on:
  - Current battery SOC (from `battery_soc_sensor`)
  - Target SOC (from `target_soc` input)
  - Battery capacity (from new `battery_capacity_sensor` input)
  - Charging power (from existing `battery_charging_power` input_number)
- Formula: `charging_hours = ((target_soc - current_soc) / 100) * capacity_kwh / (charge_power_kw * 0.95)`
- Round up to nearest 15-minute slot
- Expose calculated duration as a sensor/attribute for user visibility

**Unit Detection and Conversion:**
- Read `unit_of_measurement` attribute from battery capacity sensor at runtime
- If unit is "Wh", divide value by 1000 to convert to kWh
- If unit is "kWh", use value directly
- Handle edge cases where unit might be formatted differently (e.g., "wh", "WH", "kwh", "KWH")

**Minimum Duration Enforcement:**
- Enforce minimum charging duration of 15 minutes (0.25 hours)
- If calculated duration is less than 15 minutes, use 15 minutes
- If calculated duration is zero or negative (already at/above target SOC), skip charging

**Efficiency Factor:**
- Apply 95% charging efficiency factor to account for losses
- Formula includes efficiency: `hours = energy_needed / (charge_power * 0.95)`

**Fallback Behavior:**
- If dynamic calculation fails (sensor unavailable, invalid values, etc.), fall back to existing fixed `charging_duration_hours` input
- Log warning when fallback is used

**Output Integration:**
- Replace the static `charging_duration_hours` value with dynamically calculated duration
- Pass calculated duration (in hours or 15-minute slots) to the cheapest hours calculation logic

### New Inputs Required

**Battery Capacity Sensor:**
- Name: Battery Capacity Sensor
- Description: Sensor entity for battery maximum capacity (auto-detects Wh or kWh)
- Selector: entity (domain: sensor)
- Example: `sensor.byd_battery_box_premium_hv_maximum_capacity`

### Existing Inputs Used

From current blueprint configuration:
- `battery_soc_sensor` - Current battery state of charge
- `target_soc` - Target SOC percentage threshold
- `battery_charging_power` - Charging power in watts (input_number entity)
- `charging_duration_hours` - Used as fallback if dynamic calculation fails

### Reusability Opportunities

- Extend existing blueprint at `/workspace/blueprints/automation/charge_cheapest.yaml`
- Reuse existing `battery_soc_sensor` entity reference
- Reuse existing `target_soc` input configuration
- Reuse existing `battery_charging_power` input_number reference
- Leverage existing cheapest hours calculation that accepts duration parameter

### Scope Boundaries

**In Scope:**
- Dynamic charging duration calculation based on SOC delta and capacity
- 95% efficiency factor applied to calculation
- Runtime unit detection for battery capacity (Wh vs kWh)
- Round up to nearest 15-minute slot
- Minimum 15-minute duration enforcement
- Expose calculated duration as sensor/attribute for user visibility
- Fallback to fixed duration on calculation failure
- New blueprint input for battery capacity sensor
- Integration with existing cheapest hours calculation

**Out of Scope:**
- Solar forecast integration (deferred to later roadmap item)
- Multiple battery capacity sensors
- Manual override for calculated duration
- Historical data analysis for charge rate optimization
- Temperature-based charging adjustments

### Technical Considerations

**Jinja2 Template Implementation:**
```jinja
{# Dynamic charging duration calculation with 95% efficiency #}
{% set current_soc = states(battery_soc_sensor) | float(0) %}
{% set target = target_soc | float(80) %}
{% set capacity_raw = states(battery_capacity_sensor) | float(0) %}
{% set capacity_unit = state_attr(battery_capacity_sensor, 'unit_of_measurement') | default('kWh') | lower %}
{% set capacity_kwh = capacity_raw / 1000 if 'wh' in capacity_unit and 'kwh' not in capacity_unit else capacity_raw %}
{% set charge_power_w = states(battery_charging_power) | float(3000) %}
{% set charge_power_kw = charge_power_w / 1000 %}
{% set efficiency = 0.95 %}

{% set soc_delta = target - current_soc %}
{% if soc_delta > 0 and capacity_kwh > 0 and charge_power_kw > 0 %}
  {% set energy_needed_kwh = (soc_delta / 100) * capacity_kwh %}
  {% set hours_needed = energy_needed_kwh / (charge_power_kw * efficiency) %}
  {% set hours_clamped = [hours_needed, 0.25] | max %}
  {{ hours_clamped | round(2) }}
{% else %}
  {{ 0 }}
{% endif %}
```

**Unit Detection Logic:**
- Check if `unit_of_measurement` contains "wh" but not "kwh" -> divide by 1000
- Handle case-insensitive comparison
- Default to kWh if unit is unrecognized

**Integration Points:**
- Calculation runs at automation trigger time (before charging window)
- Result feeds into existing cheapest hours calculation as duration parameter
- Existing 15-minute granularity from Night Charging Automation applies

**Error Handling:**
- Validate sensor states are numeric and positive
- Handle unavailable/unknown sensor states gracefully
- Log warnings for debugging when fallback is used
- Continue with fallback duration rather than failing the automation

**Blueprint Structure:**
- Add new `battery_capacity_sensor` input selector
- Add template calculation in automation action sequence
- Store calculated duration in local variable for cheapest hours call
