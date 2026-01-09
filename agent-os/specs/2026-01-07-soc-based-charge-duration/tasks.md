# Task Breakdown: SOC-Based Charge Duration

## Overview
Total Tasks: 22

This feature adds dynamic charging duration calculation based on current battery SOC, target SOC, battery capacity, and charge rate. It replaces the fixed `charging_duration_hours` input with an intelligent calculation that automatically determines required charging time.

## Task List

### Backend Layer

#### Task Group 1: Duration Calculator Module
**Dependencies:** None

- [x] 1.0 Complete duration calculator module
  - [x] 1.1 Write 4-6 focused tests for duration calculation functionality
    - Test basic duration calculation with valid inputs (SOC delta, capacity, charge power)
    - Test 95% efficiency factor is applied correctly
    - Test minimum 15-minute enforcement when calculated duration is small but positive
    - Test zero/skip output when current_soc >= target_soc
    - Test rounding up to nearest 15-minute slot (0.25 hours)
    - Test fallback to default when calculation fails (invalid inputs)
  - [x] 1.2 Create `duration_calculator.py` module in `/workspace/tibber_prices/`
    - Follow existing module patterns from `slot_calculator.py` and `price_normalizer.py`
    - Include module docstring describing purpose
    - Set up logging using existing pattern: `logger = logging.getLogger(__name__)`
  - [x] 1.3 Implement `calculate_charging_duration()` function
    - Parameters: `current_soc`, `target_soc`, `capacity_kwh`, `charge_power_kw`
    - Formula: `hours = ((target_soc - current_soc) / 100) * capacity_kwh / (charge_power_kw * 0.95)`
    - Return calculated hours rounded to 2 decimal places
    - Use `math.ceil()` pattern from `slot_calculator.py` for 15-minute rounding
  - [x] 1.4 Implement `enforce_minimum_duration()` helper function
    - Enforce minimum of 0.25 hours (15 minutes) for positive durations
    - Return 0 for zero or negative calculated durations (skip charging)
    - Pattern: `max(calculated_duration, 0.25) if calculated_duration > 0 else 0`
  - [x] 1.5 Implement `round_to_slot_boundary()` helper function
    - Round up to nearest 15-minute boundary (0.25, 0.5, 0.75, 1.0, etc.)
    - Reuse `SLOTS_PER_HOUR = 4` constant from `slot_calculator.py`
    - Formula: `math.ceil(hours * 4) / 4`
  - [x] 1.6 Ensure duration calculator tests pass
    - Run ONLY the 4-6 tests written in 1.1
    - Verify all calculation edge cases handled correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 4-6 tests written in 1.1 pass
- Duration calculation matches formula with 95% efficiency
- Minimum 15-minute duration enforced correctly
- Returns 0 when current SOC >= target SOC
- Durations rounded up to nearest 15-minute slot

---

#### Task Group 2: Unit Conversion and Validation
**Dependencies:** Task Group 1

- [x] 2.0 Complete unit conversion and input validation
  - [x] 2.1 Write 4-6 focused tests for unit conversion and validation
    - Test Wh to kWh conversion (divide by 1000)
    - Test kWh passthrough (no conversion)
    - Test case-insensitive unit detection ("wh", "WH", "Wh", "kwh", "kWh", "KWH")
    - Test default to kWh when unit is missing or unrecognized
    - Test validation rejects non-numeric, negative, or zero values
    - Test SOC range validation (0-100)
  - [x] 2.2 Implement `convert_capacity_to_kwh()` function in `duration_calculator.py`
    - Parameters: `capacity_value`, `unit_of_measurement`
    - Check if unit contains "wh" but not "kwh" (case-insensitive) -> divide by 1000
    - Use value directly if unit is "kwh" or unrecognized
    - Handle None/empty unit by defaulting to kWh interpretation
  - [x] 2.3 Implement `validate_calculation_inputs()` function
    - Validate all inputs are numeric using `isinstance(value, (int, float))`
    - Validate capacity > 0 and charge_power > 0
    - Validate SOC values are in 0-100 range
    - Return tuple: `(is_valid: bool, error_message: str | None)`
    - Follow validation patterns from `price_normalizer.validate_price()`
  - [x] 2.4 Implement `get_dynamic_duration()` orchestrator function
    - Parameters: `current_soc`, `target_soc`, `capacity_raw`, `capacity_unit`, `charge_power_kw`, `fallback_duration`
    - Call validation -> conversion -> calculation -> rounding
    - Return fallback_duration on any validation failure
    - Log warning when fallback is used (follow existing logging patterns)
  - [x] 2.5 Ensure unit conversion and validation tests pass
    - Run ONLY the 4-6 tests written in 2.1
    - Verify unit conversion handles all specified variations
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 4-6 tests written in 2.1 pass
- Wh/kWh unit detection works case-insensitively
- Invalid inputs trigger fallback behavior
- Validation catches all failure conditions from spec

---

### Integration Layer

#### Task Group 3: Night Charging Integration
**Dependencies:** Task Groups 1-2

- [x] 3.0 Complete integration with night charging automation
  - [x] 3.1 Write 3-5 focused tests for night charging integration
    - Test `execute_night_charging_automation()` uses dynamic duration when calculation succeeds
    - Test automation uses fallback duration when dynamic calculation fails
    - Test calculated duration is passed correctly to `find_cheapest_slots()`
    - Test notification context includes calculated duration
  - [x] 3.2 Update `night_charging.py` to import duration calculator
    - Add import: `from tibber_prices.duration_calculator import get_dynamic_duration`
    - No changes to existing function signatures (backward compatible)
  - [x] 3.3 Create `calculate_dynamic_duration_for_automation()` wrapper function
    - Accept Home Assistant context parameters (sensor entity states, attributes)
    - Extract current_soc from `battery_soc_sensor` state
    - Extract capacity and unit from `battery_capacity_sensor` state and attributes
    - Extract charge_power from `battery_charging_power` state (convert W to kW)
    - Call `get_dynamic_duration()` with extracted values
    - Return calculated duration or fallback
  - [x] 3.4 Extend notification context with calculated duration
    - Add `calculated_duration_hours` to notification context dict
    - Update `build_notification_message()` call sites to include duration
    - Follow existing context extension pattern from `_add_notification()`
  - [x] 3.5 Ensure integration tests pass
    - Run ONLY the 3-5 tests written in 3.1
    - Verify end-to-end flow from sensor values to cheapest slots
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 3-5 tests written in 3.1 pass
- Dynamic duration calculation integrates seamlessly with existing automation
- Fallback behavior works when calculation fails
- Notifications include calculated duration information

---

### Blueprint Layer

#### Task Group 4: Blueprint Configuration
**Dependencies:** Task Group 3

- [x] 4.0 Complete blueprint input configuration
  - [x] 4.1 Write 2-4 focused tests for blueprint input handling
    - Test `battery_capacity_sensor` input is correctly parsed
    - Test Jinja2 template extracts sensor state and unit_of_measurement attribute
    - Test fallback to `charging_duration_hours` when sensor unavailable
  - [x] 4.2 Add `battery_capacity_sensor` input to blueprint
    - Location: `/workspace/blueprints/automation/charge_cheapest.yaml`
    - Add to input section under "Entity Selection Inputs"
    - Use entity selector with domain: sensor
    - Description: "Sensor entity for battery maximum capacity (auto-detects Wh or kWh)"
    - No default value (required input)
    - Follow existing `battery_soc_sensor` pattern exactly
  - [x] 4.3 Implement Jinja2 template for dynamic duration calculation
    - Add template variable section in automation action sequence
    - Extract sensor values using `states()` and `state_attr()` functions
    - Implement calculation logic matching Python implementation
    - Store result in `calculated_charging_duration` variable
    - Follow Jinja2 template pattern from requirements.md technical considerations
  - [x] 4.4 Update automation to use calculated duration
    - Replace static `charging_duration_hours` reference with `calculated_charging_duration`
    - Maintain `charging_duration_hours` input as fallback value in template
    - Ensure calculated duration feeds into cheapest hours calculation
  - [x] 4.5 Add calculated duration to notification templates
    - Include `{{ calculated_charging_duration }}` in scheduled notification
    - Allow users to see charging window length and why it was chosen
    - Follow existing notification template patterns
  - [x] 4.6 Ensure blueprint tests pass
    - Run ONLY the 2-4 tests written in 4.1
    - Verify input selector works correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-4 tests written in 4.1 pass
- New `battery_capacity_sensor` input appears in blueprint
- Jinja2 template correctly calculates duration
- Calculated duration visible in notifications

---

### Testing Layer

#### Task Group 5: Test Review and Gap Analysis
**Dependencies:** Task Groups 1-4

- [x] 5.0 Review existing tests and fill critical gaps only
  - [x] 5.1 Review tests from Task Groups 1-4
    - Review the 4-6 tests from Task Group 1 (duration calculation)
    - Review the 4-6 tests from Task Group 2 (unit conversion/validation)
    - Review the 3-5 tests from Task Group 3 (night charging integration)
    - Review the 2-4 tests from Task Group 4 (blueprint configuration)
    - Total existing tests: approximately 13-21 tests
  - [x] 5.2 Analyze test coverage gaps for THIS feature only
    - Identify critical user workflows lacking test coverage
    - Focus ONLY on SOC-based charge duration feature requirements
    - Do NOT assess entire application test coverage
    - Prioritize end-to-end workflows over unit test gaps
  - [x] 5.3 Write up to 8 additional strategic tests maximum (if necessary)
    - End-to-end test: sensor values -> calculation -> cheapest slots -> schedule
    - Integration test: fallback behavior chain when multiple failures occur
    - Edge case: battery capacity sensor reports 0 (should fallback)
    - Edge case: charge power is 0 (should fallback)
    - Edge case: SOC values at exact boundaries (0, 100)
    - Do NOT write comprehensive coverage for all scenarios
    - Skip performance tests and accessibility tests
  - [x] 5.4 Run feature-specific tests only
    - Run ONLY tests related to SOC-based charge duration feature
    - Expected total: approximately 21-29 tests maximum
    - Do NOT run the entire application test suite
    - Verify all critical workflows pass

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 21-29 tests total)
- Critical user workflows for SOC-based charge duration are covered
- No more than 8 additional tests added when filling in gaps
- Testing focused exclusively on this spec's feature requirements

---

## Execution Order

Recommended implementation sequence:

1. **Task Group 1: Duration Calculator Module** - Core calculation logic with no dependencies
2. **Task Group 2: Unit Conversion and Validation** - Build on calculator with input handling
3. **Task Group 3: Night Charging Integration** - Connect calculator to existing automation
4. **Task Group 4: Blueprint Configuration** - Add user-facing inputs and templates
5. **Task Group 5: Test Review and Gap Analysis** - Ensure comprehensive test coverage

## Technical Notes

### Files to Create
- `/workspace/tibber_prices/duration_calculator.py` - New module for duration calculation
- `/workspace/tests/test_duration_calculator.py` - Tests for new module

### Files to Modify
- `/workspace/tibber_prices/night_charging.py` - Add integration with duration calculator
- `/workspace/blueprints/automation/charge_cheapest.yaml` - Add new input and templates
- `/workspace/tibber_prices/notifications.py` - Extend notification context (if needed)

### Key Constants and Values
- Efficiency factor: 0.95 (95%)
- Minimum duration: 0.25 hours (15 minutes)
- Slot granularity: 15 minutes (SLOTS_PER_HOUR = 4)

### Existing Patterns to Follow
- Module structure: See `slot_calculator.py` for logging and docstring patterns
- Validation: See `price_normalizer.validate_price()` for validation pattern
- Error handling: See `get_fallback_schedule()` for graceful degradation pattern
- Blueprint inputs: See `battery_soc_sensor` for entity selector pattern
