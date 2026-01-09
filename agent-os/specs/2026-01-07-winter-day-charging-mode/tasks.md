# Task Breakdown: Winter Day Charging Mode

## Overview
Total Tasks: 18

This feature implements a secondary daytime charging schedule that operates independently from the existing night charging automation. The implementation replicates the night charging pattern with day-specific adaptations.

## Task List

### Blueprint Logic Layer

#### Task Group 1: Day Charging Trigger and Routing
**Dependencies:** None

- [x] 1.0 Complete day charging trigger implementation
  - [x] 1.1 Write 3-5 focused tests for day trigger routing
    - Test that day trigger fires at `day_start_time` when `day_schedule_enabled` is true
    - Test that day trigger does NOT fire when `day_schedule_enabled` is false
    - Test that choose/conditions correctly routes to day charging logic
    - Test that night charging trigger continues to work independently
  - [x] 1.2 Add second time trigger for day charging
    - Add time platform trigger for `day_start_time` input
    - Pattern: `platform: time` with `at: !input day_start_time`
    - Reference existing night trigger at line 299-301
  - [x] 1.3 Add trigger condition for day_schedule_enabled
    - Gate day trigger execution on `day_schedule_enabled` boolean
    - Use template condition: `{{ day_schedule_enabled }}`
  - [x] 1.4 Implement choose/conditions routing in action block
    - Wrap existing night charging logic in choose condition
    - Add parallel condition branch for day charging
    - Route based on which trigger fired (trigger.id or trigger comparison)
    - Maintain existing night charging logic unchanged
  - [x] 1.5 Ensure trigger routing tests pass
    - Run ONLY the 3-5 tests written in 1.1
    - Verify both triggers register correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 3-5 tests written in 1.1 pass
- Day trigger fires at configured `day_start_time`
- Day trigger respects `day_schedule_enabled` toggle
- Night charging automation unchanged and functional
- Choose/conditions correctly routes between night and day logic

---

#### Task Group 2: Day Charging Duration Calculation
**Dependencies:** Task Group 1

- [x] 2.0 Complete day charging duration variable
  - [x] 2.1 Write 2-4 focused tests for day duration calculation
    - Test calculation uses `day_target_soc` instead of `target_soc`
    - Test formula: energy_needed = (soc_delta / 100) * capacity_kwh
    - Test 15-minute slot rounding (ceil to nearest 0.25 hours)
    - Test fallback to `charging_duration_hours` when sensors unavailable
  - [x] 2.2 Create `day_calculated_charging_duration` variable template
    - Copy existing `calculated_charging_duration` template (lines 270-293)
    - Replace `target_soc` reference with `day_target_soc`
    - Keep all other logic identical (capacity detection, power conversion, 95% efficiency)
    - Formula: `hours_needed = energy_needed_kwh / (charge_power_kw * 0.95)`
  - [x] 2.3 Add variable to blueprint variables section
    - Place in variables block alongside existing `calculated_charging_duration`
    - Ensure proper YAML indentation and formatting
  - [x] 2.4 Ensure duration calculation tests pass
    - Run ONLY the 2-4 tests written in 2.1
    - Verify calculation produces correct values for various SOC scenarios
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-4 tests written in 2.1 pass
- Variable correctly uses `day_target_soc` for calculation
- 15-minute slot granularity maintained
- Fallback behavior works when sensors unavailable
- 95% efficiency factor applied

---

#### Task Group 3: Day Charging Price Fetch and Slot Calculation
**Dependencies:** Task Group 2

- [x] 3.0 Complete day price fetching and slot calculation
  - [x] 3.1 Write 2-4 focused tests for day price window
    - Test price fetch uses `day_start_time` to `day_end_time` window
    - Test cheapest slots service receives `day_calculated_charging_duration`
    - Test response contains `start_datetime` and `end_datetime`
    - Test day window does not span midnight (simpler than night charging)
  - [x] 3.2 Add price fetch service call for day window
    - Use `tibber_prices.find_cheapest_slots` service
    - Set `window_start: !input day_start_time`
    - Set `window_end: !input day_end_time`
    - Set `duration_hours: "{{ day_calculated_charging_duration }}"`
    - Store response in `day_cheapest_slots` variable
  - [x] 3.3 Position service call in day charging action branch
    - Place within the day charging choose condition
    - Execute after trigger condition check
    - Reference pattern from night charging (lines 309-314)
  - [x] 3.4 Ensure price fetch tests pass
    - Run ONLY the 2-4 tests written in 3.1
    - Verify service call parameters are correct
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-4 tests written in 3.1 pass
- Service call uses correct day window parameters
- Dynamic duration passed to service
- Response variable captured for scheduling

---

#### Task Group 4: Day SOC Skip Logic and Switch Control
**Dependencies:** Task Group 3

- [x] 4.0 Complete SOC skip logic and charging control
  - [x] 4.1 Write 2-4 focused tests for day SOC skip and switch control
    - Test skip when current SOC >= `day_target_soc`
    - Test charging proceeds when current SOC < `day_target_soc`
    - Test switch turns on at `day_cheapest_slots.start_datetime`
    - Test switch turns off at `day_cheapest_slots.end_datetime`
  - [x] 4.2 Add SOC skip condition for day charging
    - Template condition: `{{ states(battery_soc_sensor) | float(0) < day_target_soc | float(50) }}`
    - Place after price fetch, before switch control
    - Reference night charging pattern (lines 317-319)
  - [x] 4.3 Implement day charging switch control
    - Add `switch.turn_on` targeting `battery_charging_switch`
    - Schedule at: `{{ day_cheapest_slots.start_datetime }}`
    - Add `switch.turn_off` targeting `battery_charging_switch`
    - Schedule at: `{{ day_cheapest_slots.end_datetime }}`
    - Reference night charging switch control (lines 322-334)
  - [x] 4.4 Ensure SOC skip and switch control tests pass
    - Run ONLY the 2-4 tests written in 4.1
    - Verify skip logic prevents unnecessary charging
    - Verify switch schedules correct times
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-4 tests written in 4.1 pass
- Charging skipped when SOC already at target
- Switch control uses same entity as night charging
- Timing aligns with cheapest slots response

---

### Error Handling Layer

#### Task Group 5: Day Charging Failure Handling
**Dependencies:** Task Group 4

- [x] 5.0 Complete failure handling for day charging
  - [x] 5.1 Write 2-3 focused tests for day failure handling
    - Test `skip_charging` behavior when price data unavailable
    - Test `use_default_window` falls back to `default_charge_start_time` and `default_charge_duration`
    - Test `charge_immediately` starts charging at trigger time
  - [x] 5.2 Add failure detection for price fetch
    - Check if `day_cheapest_slots` response is valid
    - Handle empty or error responses from Tibber service
  - [x] 5.3 Implement choose conditions for failure_behavior
    - `skip_charging`: Do not charge, optionally send error notification
    - `use_default_window`: Use `default_charge_start_time` and `default_charge_duration`
    - `charge_immediately`: Start charging at current time for default duration
    - Reuse shared `failure_behavior` configuration
  - [x] 5.4 Ensure failure handling tests pass
    - Run ONLY the 2-3 tests written in 5.1
    - Verify each failure behavior option works correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-3 tests written in 5.1 pass
- All three failure behaviors implemented
- Uses shared `failure_behavior` configuration
- Graceful degradation when price data unavailable

---

### Notification Layer

#### Task Group 6: Day Charging Notifications
**Dependencies:** Task Group 5

- [x] 6.0 Complete notification integration for day charging
  - [x] 6.1 Write 2-4 focused tests for day notifications
    - Test "Day Charging" prefix in notification titles
    - Test notification respects `notify_charging_scheduled` toggle
    - Test notification respects `notify_charging_skipped` toggle
    - Test unique `notification_id` for day charging (distinct from night)
  - [x] 6.2 Add day charging scheduled notification
    - Title: "Day Charging Scheduled"
    - Include start/end times from `day_cheapest_slots`
    - Include `day_calculated_charging_duration` and estimated cost
    - Use timestamp formatting: `as_timestamp | timestamp_custom('%H:%M')`
    - Conditional on `notify_charging_scheduled` toggle
    - Use `notification_id: "charge_cheapest_day_charging_scheduled"`
  - [x] 6.3 Add day charging skipped notification
    - Title: "Day Charging Skipped"
    - Message: "Battery SOC already at or above day target"
    - Include current SOC and `day_target_soc` values
    - Conditional on `notify_charging_skipped` toggle
    - Use `notification_id: "charge_cheapest_day_charging_skipped"`
  - [x] 6.4 Add day charging error notification
    - Title: "Day Charging Error"
    - Include error details and failure behavior applied
    - Conditional on `notify_charging_error` toggle
    - Use `notification_id: "charge_cheapest_day_charging_error"`
  - [x] 6.5 Add day charging started/completed notifications
    - "Day Charging Started" notification at switch-on time
    - "Day Charging Completed" notification at switch-off time
    - Conditional on respective notification toggles
    - Use unique notification_ids
  - [x] 6.6 Ensure notification tests pass
    - Run ONLY the 2-4 tests written in 6.1
    - Verify notifications display correctly
    - Verify toggle conditions respected
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-4 tests written in 6.1 pass
- All notifications prefixed with "Day Charging"
- Reuses existing notification toggle inputs
- Unique notification_ids prevent conflicts with night charging

---

### Testing

#### Task Group 7: Test Review and Integration Validation
**Dependencies:** Task Groups 1-6

- [x] 7.0 Review tests and validate full integration
  - [x] 7.1 Review tests from Task Groups 1-6
    - Review 3-5 trigger routing tests (Task 1.1)
    - Review 2-4 duration calculation tests (Task 2.1)
    - Review 2-4 price fetch tests (Task 3.1)
    - Review 2-4 SOC/switch tests (Task 4.1)
    - Review 2-3 failure handling tests (Task 5.1)
    - Review 2-4 notification tests (Task 6.1)
    - Total existing tests: approximately 13-24 tests
  - [x] 7.2 Analyze test coverage gaps for day charging feature only
    - Identify critical end-to-end workflows lacking coverage
    - Focus on integration between components (trigger -> price -> schedule -> notify)
    - Do NOT assess entire blueprint test coverage
    - Prioritize full day charging workflow over unit-level gaps
  - [x] 7.3 Write up to 6 additional integration tests if needed
    - Full day charging workflow: trigger -> calculate -> fetch -> schedule -> notify
    - Day and night charging independence (both can run without interference)
    - Edge case: day window boundary conditions
    - Error recovery: price fetch failure -> failure_behavior execution
    - Do NOT write exhaustive edge case tests
  - [x] 7.4 Run feature-specific tests only
    - Run ONLY tests related to day charging feature
    - Expected total: approximately 19-30 tests maximum
    - Verify all critical workflows pass
    - Do NOT run entire application test suite
  - [x] 7.5 Validate blueprint YAML syntax
    - Verify blueprint loads without syntax errors
    - Confirm all inputs referenced correctly
    - Validate Jinja2 templates render properly

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 19-30 tests total)
- Full day charging workflow functions end-to-end
- Night charging remains unchanged and functional
- Blueprint YAML is valid and loads correctly
- No more than 6 additional tests added for gap coverage

---

## Execution Order

Recommended implementation sequence:

1. **Task Group 1: Day Charging Trigger and Routing** - Foundation for day charging automation
2. **Task Group 2: Day Charging Duration Calculation** - Variable needed for slot calculation
3. **Task Group 3: Price Fetch and Slot Calculation** - Core scheduling logic
4. **Task Group 4: SOC Skip Logic and Switch Control** - Actual charging execution
5. **Task Group 5: Failure Handling** - Robust error recovery
6. **Task Group 6: Notifications** - User feedback
7. **Task Group 7: Test Review and Integration** - Final validation

## Files to Modify

| File | Changes |
|------|---------|
| `/workspace/blueprints/automation/charge_cheapest.yaml` | Add day charging trigger, variables, action logic, notifications |

## Key Implementation Notes

- **Reuse Pattern**: Day charging closely mirrors night charging pattern; copy and adapt existing code
- **Independence**: Day and night schedules must operate independently with no coordination
- **No New Inputs**: All required inputs already exist in the blueprint
- **Same Entities**: Use same `battery_charging_switch`, `battery_soc_sensor`, and other entities
- **Unique Identifiers**: Day charging must use distinct notification_ids and response variables
- **15-Minute Granularity**: Maintain same slot size as night charging
- **Same Day Window**: Day charging window does not span midnight (simpler than night charging)
