# Task Breakdown: Two Options for Forecast Calculation

## Overview
Total Tasks: 16 subtasks across 4 task groups

This feature extends the solar forecast calculation to support two operating modes:
- **Automatic mode**: Forecast directly sets target SOC values
- **Recommendation mode** (default): Forecast suggests values via sensor, user sets desired values via input_number

## Task List

### Blueprint Inputs Setup

#### Task Group 1: Mode Toggle and User Input Configuration
**Dependencies:** None

- [x] 1.0 Complete blueprint inputs setup
  - [x] 1.1 Write 2-4 focused tests for mode toggle and input validation
    - Test mode toggle input_boolean defaults to false (recommendation mode)
    - Test user_soc_input_number selector accepts valid input_number entities
    - Test mode toggle runtime switching behavior
  - [x] 1.2 Create forecast_mode_automatic input_boolean blueprint input
    - Follow pattern from `solar_forecast_enabled` input (lines 304-309)
    - Default value: false (recommendation mode is default)
    - Name: "Forecast Mode: Automatic"
    - Description: "When enabled, forecast directly sets SOC targets. When disabled (default), forecast suggests values for user to confirm via input_number."
  - [x] 1.3 Create user_soc_input_number blueprint input selector
    - Add after `solar_forecast_storage` input section (after line 392)
    - Entity selector for input_number domain
    - Name: "User SOC Target Input"
    - Description: "Input number helper for user to set desired SOC target in recommendation mode (create manually: 0-100%, step 5)"
  - [x] 1.4 Add variable references for new inputs in variables section
    - Follow pattern from lines 420-433 (solar forecast variable references)
    - Add `forecast_mode_automatic: !input forecast_mode_automatic`
    - Add `user_soc_input_number: !input user_soc_input_number`
  - [x] 1.5 Ensure blueprint inputs tests pass
    - Run ONLY the 2-4 tests written in 1.1
    - Verify inputs render correctly in blueprint configuration

**Acceptance Criteria:**
- Mode toggle input_boolean with false as default (recommendation mode)
- User SOC input_number selector configured
- Variable references accessible in templates
- Tests from 1.1 pass

### Recommendation Sensor

#### Task Group 2: Template Sensor for Forecast Recommendation
**Dependencies:** Task Group 1

- [x] 2.0 Complete recommendation sensor implementation
  - [x] 2.1 Write 2-4 focused tests for recommendation sensor
    - Test sensor updates with optimal_morning_soc calculation value
    - Test sensor attributes include expected_solar_kwh and morning_consumption_kwh
    - Test sensor state respects clamping logic (minimum_soc_floor to night_target_soc)
  - [x] 2.2 Create template sensor variable for sensor.charge_cheapest_recommended_soc
    - Add new variable in variables section (after line 708)
    - State: reuse `optimal_morning_soc` calculated value (lines 664-685)
    - Reference existing `solar_forecast_attributes` variable (lines 693-708) for attributes
  - [x] 2.3 Define sensor attributes structure
    - expected_solar_kwh: from `solar_forecast_kwh` variable
    - morning_consumption_kwh: from `morning_consumption_kwh` input
    - calculation_timestamp: use `now().isoformat()`
    - Leverage existing `solar_forecast_attributes` template (lines 693-708)
  - [x] 2.4 Integrate sensor update into solar_forecast_polling branch
    - Modify branch starting at line 1408
    - Add service call to update template sensor state after forecast fetch (around line 1449)
    - Use trigger-based template sensor or input_text to persist sensor value
  - [x] 2.5 Ensure recommendation sensor tests pass
    - Run ONLY the 2-4 tests written in 2.1
    - Verify sensor state and attributes update correctly

**Acceptance Criteria:**
- Template sensor exposes forecast-calculated SOC value
- Sensor includes all required attributes
- Sensor updates hourly with solar forecast polling
- Tests from 2.1 pass

### Charging Logic Integration

#### Task Group 3: Mode-Aware Charging Target Selection
**Dependencies:** Task Groups 1, 2

- [x] 3.0 Complete charging logic integration
  - [x] 3.1 Write 3-5 focused tests for mode-aware charging logic
    - Test automatic mode uses optimal_morning_soc directly
    - Test recommendation mode uses user input_number value
    - Test input_number pre-population with recommended value
    - Test night and day charging both respect mode setting
  - [x] 3.2 Add input_number.set_value service call for pre-population
    - Follow pattern from `input_text.set_value` service (lines 1444-1448)
    - Add to solar_forecast_polling branch (after line 1449)
    - Set `user_soc_input_number` entity to `optimal_morning_soc` value
    - Only execute when in recommendation mode (forecast_mode_automatic is false)
  - [x] 3.3 Modify night_charging_target_soc variable for mode awareness
    - Extend existing template (lines 715-720)
    - Current logic: checks `solar_forecast_enabled` only
    - New logic:
      - If `solar_forecast_enabled` AND `forecast_mode_automatic`: use `optimal_morning_soc`
      - If `solar_forecast_enabled` AND NOT `forecast_mode_automatic`: use `states(user_soc_input_number)`
      - Else: use `night_target_soc` (existing fallback)
  - [x] 3.4 Apply same mode logic to day charging target
    - Modify day charging branch (lines 1076-1325)
    - Create `day_charging_target_soc` variable with mode awareness
    - Use same `user_soc_input_number` entity for consistency
  - [x] 3.5 Update skip notification to indicate mode used
    - Modify night charging skip notification (lines 940-951)
    - Add mode indicator: "automatic" or "recommendation"
    - Update `night_charging_target_source` variable (lines 726-732) to include mode info
  - [x] 3.6 Ensure charging logic tests pass
    - Run ONLY the 3-5 tests written in 3.1
    - Verify mode switching works at runtime
    - Verify charging duration calculation uses effective target SOC

**Acceptance Criteria:**
- Automatic mode uses optimal_morning_soc directly
- Recommendation mode uses user's input_number value
- Input_number pre-populated with recommended value on forecast update
- Both night and day schedules respect same mode setting
- Tests from 3.1 pass

### Testing

#### Task Group 4: Test Review and Gap Analysis
**Dependencies:** Task Groups 1-3

- [x] 4.0 Review existing tests and fill critical gaps only
  - [x] 4.1 Review tests from Task Groups 1-3
    - Review 2-4 tests from blueprint inputs (Task 1.1)
    - Review 2-4 tests from recommendation sensor (Task 2.1)
    - Review 3-5 tests from charging logic (Task 3.1)
    - Total existing tests: approximately 7-13 tests
  - [x] 4.2 Analyze test coverage gaps for this feature only
    - Identify untested mode switching edge cases
    - Check integration between sensor updates and charging logic
    - Focus ONLY on this spec's feature requirements
  - [x] 4.3 Write up to 5 additional strategic tests maximum
    - End-to-end test: forecast update triggers input_number pre-population
    - Integration test: mode switch mid-schedule respects new setting
    - Test fallback behavior when solar forecast unavailable
  - [x] 4.4 Run feature-specific tests only
    - Run ONLY tests related to this spec's feature
    - Expected total: approximately 12-18 tests maximum
    - Verify all critical workflows pass

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 12-18 tests total)
- Mode switching behavior verified across scenarios
- Integration between sensor and charging logic tested
- No more than 5 additional tests added

## Execution Order

Recommended implementation sequence:

1. **Task Group 1: Blueprint Inputs Setup**
   - Foundation for all other tasks
   - Creates mode toggle and user input references

2. **Task Group 2: Recommendation Sensor**
   - Depends on variable references from Task Group 1
   - Exposes forecast data before charging logic uses it

3. **Task Group 3: Charging Logic Integration**
   - Depends on both inputs and sensor
   - Implements core mode-aware behavior

4. **Task Group 4: Test Review and Gap Analysis**
   - Final validation of complete feature
   - Ensures all components work together

## Key Code Locations in charge_cheapest.yaml

| Pattern | Current Line Numbers | Purpose |
|---------|---------------------|---------|
| `solar_forecast_enabled` input | 304-309 | Reference pattern for new boolean input |
| Solar forecast input variables | 420-433 | Reference pattern for variable definitions |
| `optimal_morning_soc` calculation | 664-685 | Core SOC calculation to reuse/expose |
| `solar_forecast_attributes` | 693-708 | Attribute structure to leverage for sensor |
| `night_charging_target_soc` | 715-720 | Primary variable to extend with mode logic |
| `night_charging_target_source` | 726-732 | Source indicator to update with mode info |
| Night charging skip notification | 940-951 | Update to indicate mode used |
| Day charging branch | 1076-1325 | Apply mode logic to day schedule |
| Solar forecast polling branch | 1408-1492 | Add sensor update and input pre-population |
| `input_text.set_value` pattern | 1444-1448 | Reference pattern for input_number.set_value |

## Out of Scope Reminders

Do NOT implement:
- Push notifications when recommendation changes
- Separate mode settings for night vs day charging
- Timeout-based automatic confirmation
- Blocking charging until user confirms
- Dashboard card or UI components
- Automatic creation of helper entities
- Historical tracking of recommendations
- ML adaptations
- Other forecast sources beyond Forecast.Solar
- Per-schedule input_number entities
