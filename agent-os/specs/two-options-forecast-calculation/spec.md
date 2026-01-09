# Specification: Two Options for Forecast Calculation

## Goal
Extend the solar forecast calculation to support two operating modes: Automatic mode where the forecast directly sets target SOC values, and Recommendation mode (default) where the forecast suggests values via a sensor while the user sets the desired target via an input_number helper.

## User Stories
- As a home battery owner, I want the solar forecast to automatically set my charging target so that I can optimize my energy usage without manual intervention.
- As a user who prefers manual control, I want to see the recommended SOC value and adjust it myself before charging executes, so that I can override the forecast based on my knowledge of upcoming conditions.

## Specific Requirements

**Mode Toggle Mechanism**
- Create an input_boolean blueprint input for mode selection (automatic vs recommendation)
- Recommendation mode is the default (input_boolean default: false where false = recommendation mode)
- Mode can be switched at runtime without blueprint reconfiguration
- Both night and day charging schedules respect the same mode setting

**Recommendation Sensor Entity**
- Create a template sensor that exposes the forecast-calculated SOC value
- Sensor updates whenever the solar forecast calculation runs (hourly polling)
- Include attributes: expected_solar_kwh, morning_consumption_kwh, calculation_timestamp
- Sensor entity name pattern: sensor.charge_cheapest_recommended_soc

**User SOC Input Number**
- Add blueprint input to select user-provided input_number entity for manual SOC target
- Input_number should be pre-populated with the recommended value when recommendation updates
- Use input_number.set_value service to update the helper automatically
- Value range: 0-100% with step of 5

**Charging Logic with Mode Awareness**
- In automatic mode: use optimal_morning_soc directly (existing behavior)
- In recommendation mode: use the value from user's input_number entity
- Charging still executes at cheapest hours in both modes
- Duration calculation uses the effective target SOC (automatic or user-defined)

**Night Charging Integration**
- Modify night_charging_target_soc variable to check mode setting
- When automatic: use optimal_morning_soc from solar forecast calculation
- When recommendation: use states(user_soc_input_number) value
- Update skip notification to indicate which mode was used

**Day Charging Integration**
- Apply same mode logic to day charging if solar forecast affects day schedule
- Day charging should respect the mode toggle identically to night charging
- Use same user input_number for consistency across both schedules

## Visual Design
No visual assets provided.

## Existing Code to Leverage

**solar_forecast_enabled input and variables (charge_cheapest.yaml)**
- Existing boolean input pattern at line 293-298 for enabling solar forecast feature
- Variable references pattern at lines 412-422 for accessing input values in templates
- Follow same structure for new mode toggle input_boolean

**optimal_morning_soc calculation (charge_cheapest.yaml lines 502-523)**
- Existing SOC calculation template that computes target based on solar forecast
- This calculated value should populate the recommendation sensor and input_number
- Reuse the clamping logic (minimum_soc_floor to night_target_soc range)

**night_charging_target_soc variable (charge_cheapest.yaml lines 553-558)**
- Existing conditional template for determining effective target SOC
- Extend to include mode check: automatic uses optimal_morning_soc, recommendation uses user input_number
- Maintain fallback to night_target_soc when solar forecast unavailable

**input_text.set_value service pattern (charge_cheapest.yaml lines 1202-1206)**
- Existing pattern for updating helper entity values from automation
- Replicate for input_number.set_value to pre-populate user SOC target
- Execute during solar forecast polling branch to keep recommendation current

**solar_forecast_polling branch (charge_cheapest.yaml lines 1173-1250)**
- Existing hourly polling trigger and logic for updating forecast data
- Add step to update user input_number with recommended value when in recommendation mode
- Add step to update recommendation sensor state

## Out of Scope
- Push notifications when recommendation value changes
- Separate mode settings for night vs day charging (must use unified mode)
- Timeout-based automatic confirmation (user must explicitly set value)
- Blocking charging until user confirms in recommendation mode
- Dashboard card or UI components for mode switching
- Automatic creation of helper entities (user must create input_number manually)
- Historical tracking of recommendation vs actual SOC used
- Machine learning or adaptive recommendations based on user behavior
- Integration with other forecast sources beyond Forecast.Solar
- Per-schedule input_number entities (single input_number serves both schedules)
