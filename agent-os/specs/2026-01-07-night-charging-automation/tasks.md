# Task Breakdown: Night Charging Automation

## Overview
Total Tasks: 25
Complexity: Medium-High

This feature implements the core automation that triggers battery charging during the cheapest night hours using 15-minute granularity scheduling, configurable battery control entities, and notification support.

## Dependencies Summary
- Builds on completed roadmap items #1-4 (Blueprint Schema, Tibber Service, Cross-Midnight Fetching, Cheapest Hours Logic)
- Existing code in `/workspace/tibber_prices/` provides foundation for price fetching and calculation
- Existing blueprint in `/workspace/blueprints/automation/charge_cheapest.yaml` provides schema foundation

## Task List

### Price Calculation Layer

#### Task Group 1: 15-Minute Slot Expansion and Calculation
**Dependencies:** None (uses existing modules)
**Complexity:** Medium

- [x] 1.0 Complete 15-minute slot calculation logic
  - [x] 1.1 Write 4-6 focused tests for 15-minute slot functionality
    - Test `expand_hourly_to_slots()` converts 1 hourly entry to 4 identical 15-min slots
    - Test slot timestamps are correctly offset (00:00, 00:15, 00:30, 00:45)
    - Test `find_cheapest_slots()` finds correct minimum cost window with 15-min granularity
    - Test conversion from charging duration hours to slot count (hours * 4)
    - Test integration with existing `fetch_prices_range()` output
    - Mock external dependencies; use fast-executing unit tests
  - [x] 1.2 Create `expand_hourly_to_slots()` function in new module `/workspace/tibber_prices/slot_calculator.py`
    - Input: List of hourly price entries with `timestamp` and `price` keys
    - Output: List of 15-minute slot entries (4x input length)
    - Each slot inherits the hourly price (Tibber provides hourly; we subdivide)
    - Generate timestamps at :00, :15, :30, :45 for each hour
    - Preserve timezone information from original timestamps
    - Follow existing pattern from `price_normalizer.py`
  - [x] 1.3 Create `find_cheapest_slots()` function in `/workspace/tibber_prices/slot_calculator.py`
    - Adapt sliding window algorithm from `cheapest_hours.py` for slot-based calculation
    - Input: slot entries list, duration_hours (float), optional time_window constraint
    - Convert duration_hours to slot_count (duration_hours * 4)
    - Return dict with `start_datetime`, `slots` list, `total_cost`, `duration_slots`
    - Handle error cases: insufficient slots, invalid duration
    - Reuse `_sliding_window_minimum` pattern from `cheapest_hours.py`
  - [x] 1.4 Add `convert_duration_to_slots()` helper function
    - Input: duration in hours (float)
    - Output: number of 15-minute slots (int, rounded up)
    - Handle fractional hours (e.g., 2.5 hours = 10 slots)
  - [x] 1.5 Ensure 15-minute slot tests pass
    - Run ONLY the 4-6 tests written in 1.1
    - Verify slot expansion produces correct timestamps and prices
    - Verify cheapest slot calculation matches expected results
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 4-6 tests written in 1.1 pass
- `expand_hourly_to_slots()` correctly generates 4 slots per hour with proper timestamps
- `find_cheapest_slots()` returns correct optimal window for 15-minute granularity
- Duration conversion handles whole hours and fractional hours
- Module follows existing code patterns (logging, type hints, docstrings)

---

### Automation Core Layer

#### Task Group 2: Night Charging Automation Logic
**Dependencies:** Task Group 1
**Complexity:** High

- [x] 2.0 Complete automation core logic module
  - [x] 2.1 Write 4-6 focused tests for automation orchestration
    - Test `calculate_night_charging_schedule()` integrates price fetch and slot calculation
    - Test SOC skip logic: returns skip result when current_soc >= target_soc
    - Test fallback behavior selection (skip_charging, use_default_window, charge_immediately)
    - Test cross-midnight datetime construction from time inputs
    - Test charging window calculation outputs correct start/end times
    - Mock price fetching and sensor reading; keep tests fast
  - [x] 2.2 Create automation orchestration module `/workspace/tibber_prices/night_charging.py`
    - Main function: `calculate_night_charging_schedule()`
    - Inputs: night_start_time, night_end_time, charging_duration_hours, trigger_datetime
    - Integrate with `fetch_prices_range()` from `cross_midnight.py`
    - Integrate with `find_cheapest_slots()` from `slot_calculator.py`
    - Return structured result: `schedule`, `start_datetime`, `end_datetime`, `estimated_cost`
  - [x] 2.3 Implement `check_soc_skip_condition()` function
    - Input: current_soc (float), target_soc (float)
    - Output: boolean (True = skip charging, False = proceed)
    - Simple comparison: skip if current_soc >= target_soc
  - [x] 2.4 Implement `get_fallback_schedule()` function
    - Input: failure_behavior setting, default_start_time, default_duration
    - Handle three modes:
      - `skip_charging`: Return None/skip result
      - `use_default_window`: Return schedule using default times
      - `charge_immediately`: Return schedule starting now
    - Return same structure as normal schedule for consistency
  - [x] 2.5 Implement `build_night_window_datetimes()` helper
    - Input: night_start_time (time), night_end_time (time), reference_date
    - Output: (start_datetime, end_datetime) with proper cross-midnight handling
    - Handle case where end_time < start_time (spans to next calendar day)
    - Preserve timezone from reference_date
  - [x] 2.6 Ensure automation logic tests pass
    - Run ONLY the 4-6 tests written in 2.1
    - Verify orchestration integrates components correctly
    - Verify SOC skip and fallback logic work as expected
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 4-6 tests written in 2.1 pass
- `calculate_night_charging_schedule()` returns valid schedule with correct timing
- SOC skip condition correctly prevents unnecessary charging
- Fallback behavior provides graceful degradation when prices unavailable
- Cross-midnight datetime construction handles date boundary correctly

---

### Blueprint Configuration Layer

#### Task Group 3: Blueprint Schema Extension
**Dependencies:** Task Group 2
**Complexity:** Medium

- [x] 3.0 Complete blueprint input configuration
  - [x] 3.1 Write 3-5 focused tests for blueprint schema validation
    - Test YAML structure is valid and parseable
    - Test all required inputs have defaults defined
    - Test selector types match expected entity domains
    - Test notification toggle inputs are boolean type
    - Use YAML parsing library; validate structure not runtime behavior
  - [x] 3.2 Add battery SOC sensor input to blueprint
    - Location: `/workspace/blueprints/automation/charge_cheapest.yaml`
    - Input name: `battery_soc_sensor`
    - Selector: `entity` with domain `sensor`
    - Description: "Sensor entity for current battery state of charge"
    - No default (required input)
  - [x] 3.3 Add charging configuration inputs
    - `target_soc`: Number selector (0-100%, default 80, step 5)
    - `charging_duration_hours`: Number selector (0.5-8, default 3, step 0.5)
    - `trigger_time`: Time selector (default "22:30:00")
    - Follow existing input patterns in the blueprint
  - [x] 3.4 Add failure behavior configuration
    - `failure_behavior`: Selector with dropdown options
    - Options: `skip_charging`, `use_default_window`, `charge_immediately`
    - Default: `skip_charging`
    - Add `default_charge_start_time`: Time selector (default "01:00:00")
    - Add `default_charge_duration`: Number selector (default 3 hours)
  - [x] 3.5 Add notification toggle inputs
    - `notify_charging_scheduled`: Boolean (default true)
    - `notify_charging_started`: Boolean (default true)
    - `notify_charging_completed`: Boolean (default true)
    - `notify_charging_skipped`: Boolean (default true)
    - `notify_charging_error`: Boolean (default true)
    - Group under comment section "Notification Settings"
  - [x] 3.6 Ensure blueprint schema tests pass
    - Run ONLY the 3-5 tests written in 3.1
    - Verify YAML is syntactically valid
    - Verify all inputs have correct types and defaults
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 3-5 tests written in 3.1 pass
- Blueprint YAML remains valid and parseable
- All new inputs follow existing naming and structure conventions
- Selectors use correct domains and value ranges
- Documentation descriptions are clear and helpful

---

### Notification Layer

#### Task Group 4: Notification Service Integration
**Dependencies:** Task Group 3
**Complexity:** Low-Medium

- [x] 4.0 Complete notification functionality
  - [x] 4.1 Write 3-4 focused tests for notification logic
    - Test `build_notification_message()` generates correct content for each event type
    - Test `should_send_notification()` respects opt-out settings
    - Test notification payload structure matches Home Assistant service format
    - Mock Home Assistant service calls; test message construction only
  - [x] 4.2 Create notification module `/workspace/tibber_prices/notifications.py`
    - Define notification types as constants: SCHEDULED, STARTED, COMPLETED, SKIPPED, ERROR
    - Create `NotificationConfig` dataclass for opt-in/out settings
    - Follow existing module patterns (logging, type hints, docstrings)
  - [x] 4.3 Implement `build_notification_message()` function
    - Input: event_type, context_data (schedule details, SOC, cost, etc.)
    - Output: dict with `title` and `message` keys
    - Message templates:
      - SCHEDULED: "Charging scheduled from {start} to {end}. Estimated cost: {cost}"
      - STARTED: "Battery charging started at {time}"
      - COMPLETED: "Battery charging completed at {time}"
      - SKIPPED: "Charging skipped - SOC already at {current_soc}% (target: {target_soc}%)"
      - ERROR: "Charging error: {error_message}. Fallback: {fallback_action}"
  - [x] 4.4 Implement `should_send_notification()` function
    - Input: event_type, notification_config
    - Output: boolean
    - Check corresponding opt-out setting for each notification type
    - Return True if notification should be sent, False if opted out
  - [x] 4.5 Implement `create_notification_payload()` function
    - Input: title, message, notification_id (optional)
    - Output: dict formatted for `persistent_notification.create` service
    - Structure: `{"title": str, "message": str, "notification_id": str}`
    - Auto-generate notification_id from timestamp if not provided
  - [x] 4.6 Ensure notification tests pass
    - Run ONLY the 3-4 tests written in 4.1
    - Verify message templates produce expected output
    - Verify opt-out logic works correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 3-4 tests written in 4.1 pass
- All five notification types have appropriate message templates
- Notification opt-out settings are respected
- Payload structure matches Home Assistant service expectations
- Messages include relevant context (times, costs, SOC values)

---

### Switch Control Layer

#### Task Group 5: Charging Switch Control Logic
**Dependencies:** Task Group 2
**Complexity:** Low-Medium

- [x] 5.0 Complete switch control functionality
  - [x] 5.1 Write 2-4 focused tests for switch control logic
    - Test `build_switch_service_call()` generates correct payload for turn_on/turn_off
    - Test charging duration calculation produces correct end time
    - Test switch entity validation accepts valid switch entities
    - Mock Home Assistant service calls; test payload construction only
  - [x] 5.2 Create switch control module `/workspace/tibber_prices/switch_control.py`
    - Define service constants: `SWITCH_TURN_ON`, `SWITCH_TURN_OFF`
    - Follow existing module patterns
  - [x] 5.3 Implement `build_switch_service_call()` function
    - Input: entity_id, action (on/off)
    - Output: dict formatted for `switch.turn_on` or `switch.turn_off` service
    - Structure: `{"entity_id": str}`
    - Validate action is one of "on" or "off"
  - [x] 5.4 Implement `calculate_charging_end_time()` function
    - Input: start_datetime, duration_hours
    - Output: end_datetime
    - Handle case where charging extends beyond night_end_time (allow completion)
    - Use timedelta for duration calculation
  - [x] 5.5 Ensure switch control tests pass
    - Run ONLY the 2-4 tests written in 5.1
    - Verify service call payloads are correct
    - Verify duration calculations are accurate
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-4 tests written in 5.1 pass
- Service call payloads match Home Assistant expected format
- Charging end time calculation handles duration correctly
- Module integrates cleanly with automation orchestration

---

### Integration Layer

#### Task Group 6: End-to-End Integration
**Dependencies:** Task Groups 1-5
**Complexity:** Medium

- [x] 6.0 Complete integration and orchestration
  - [x] 6.1 Write 3-5 focused integration tests
    - Test full workflow: trigger -> fetch prices -> calculate slots -> generate schedule
    - Test SOC skip workflow: check SOC -> skip -> send notification
    - Test fallback workflow: price fetch fails -> fallback behavior -> notification
    - Test cross-midnight scenario end-to-end (23:00 to 06:00)
    - Mock external services (Tibber API, Home Assistant); test integration of components
  - [x] 6.2 Create main automation entry point in `night_charging.py`
    - Function: `execute_night_charging_automation()`
    - Inputs: All blueprint configuration values
    - Orchestrate: price fetch -> slot calculation -> SOC check -> schedule/skip -> notify
    - Return: automation result with status, schedule (if applicable), notifications sent
  - [x] 6.3 Add comprehensive logging throughout workflow
    - Log automation trigger with configuration summary
    - Log price fetch result (success/failure, price count)
    - Log slot calculation result (optimal window, cost)
    - Log SOC check result (current vs target, decision)
    - Log switch control actions (on/off, times)
    - Log notification dispatch (type, sent/skipped)
    - Use appropriate log levels (INFO for normal flow, WARNING for fallbacks, ERROR for failures)
  - [x] 6.4 Implement error handling and graceful degradation
    - Catch price fetching failures -> trigger fallback behavior
    - Catch slot calculation errors -> log and notify
    - Catch switch control failures -> notify error
    - Never crash the automation; always attempt notification on error
  - [x] 6.5 Ensure integration tests pass
    - Run ONLY the 3-5 tests written in 6.1
    - Verify complete workflows execute correctly
    - Verify error handling triggers appropriate fallbacks
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 3-5 tests written in 6.1 pass
- Complete automation workflow executes successfully
- Error handling provides graceful degradation with notifications
- Logging provides sufficient detail for debugging
- All components integrate cleanly

---

### Testing and Validation

#### Task Group 7: Test Review and Gap Analysis
**Dependencies:** Task Groups 1-6
**Complexity:** Low

- [x] 7.0 Review existing tests and fill critical gaps only
  - [x] 7.1 Review tests from Task Groups 1-6
    - Review the 4-6 tests written in Task 1.1 (slot calculation) - `/workspace/tests/test_slot_calculator.py`
    - Review the 4-6 tests written in Task 2.1 (automation logic) - `/workspace/tests/test_night_charging.py`
    - Review the 3-5 tests written in Task 3.1 (blueprint schema) - `/workspace/tests/blueprint-schema-extension.test.js`
    - Review the 3-4 tests written in Task 4.1 (notifications) - `/workspace/tests/test_notifications.py`
    - Review the 2-4 tests written in Task 5.1 (switch control) - `/workspace/tests/test_switch_control.py`
    - Review the 3-5 tests written in Task 6.1 (integration) - `/workspace/tests/test_night_charging_integration.py`
    - Total existing tests: 55 tests (50 Python + 5 JavaScript)
  - [x] 7.2 Analyze test coverage gaps for this feature only
    - Identified critical user workflows that lack test coverage
    - Focused ONLY on gaps related to night charging automation requirements
    - Did NOT assess entire application test coverage
    - Prioritized end-to-end workflows over unit test gaps
    - Checked: SOC boundary conditions (covered), price edge cases (added all-same-price test)
  - [x] 7.3 Write up to 8 additional strategic tests maximum
    - Added 8 new tests in `/workspace/tests/test_night_charging_gaps.py`
    - Gap areas covered:
      - Fractional duration hours (2.75 hours = 11 slots)
      - Empty price response handling
      - All-same-price edge case
      - Notification with long content
      - Duration exceeding available slots
      - Minimum duration (15 minutes) boundary
      - Cross-midnight with negative timezone offset
      - Missing price data handling
    - Did NOT write comprehensive coverage for all scenarios
    - Skipped performance tests and non-critical edge cases
  - [x] 7.4 Run feature-specific tests only
    - Ran ONLY tests related to night charging automation
    - Total: 63 tests (58 Python + 5 JavaScript)
    - All tests pass
    - Did NOT run the entire application test suite
    - Verified all critical workflows pass
  - [x] 7.5 Document test coverage in brief summary
    - Created `/workspace/agent-os/specs/2026-01-07-night-charging-automation/TEST_COVERAGE_SUMMARY.md`
    - Listed test files and their coverage areas
    - Noted intentionally deferred test scenarios

**Acceptance Criteria:**
- [x] All feature-specific tests pass (63 tests total)
- [x] Critical user workflows for night charging are covered
- [x] No more than 8 additional tests added when filling gaps (exactly 8 added)
- [x] Testing focused exclusively on this spec's feature requirements

---

## Execution Order

Recommended implementation sequence:

```
1. Task Group 1: 15-Minute Slot Expansion and Calculation
   - Foundation for all price-based scheduling
   - No dependencies on other groups

2. Task Group 2: Night Charging Automation Logic
   - Core business logic
   - Depends on Group 1 for slot calculation

3. Task Group 3: Blueprint Schema Extension
   - Configuration layer
   - Can be done in parallel with Group 2 after Group 1

4. Task Group 4: Notification Service Integration
   - User feedback layer
   - Can be done in parallel with Groups 3 and 5

5. Task Group 5: Charging Switch Control Logic
   - Device control layer
   - Depends on Group 2 for schedule data

6. Task Group 6: End-to-End Integration
   - Ties all components together
   - Depends on Groups 1-5

7. Task Group 7: Test Review and Gap Analysis
   - Final validation
   - Depends on Groups 1-6
```

### Parallelization Opportunities

Tasks that can be worked on simultaneously:
- Groups 3, 4, and 5 can progress in parallel after Group 1 is complete
- Test writing (x.1 tasks) can begin before implementation if API contracts are defined

---

## File Structure

New files to be created:
```
/workspace/tibber_prices/
  slot_calculator.py      # Task Group 1 - 15-minute slot logic
  night_charging.py       # Task Group 2 - Automation orchestration
  notifications.py        # Task Group 4 - Notification service
  switch_control.py       # Task Group 5 - Switch control

/workspace/tests/
  test_slot_calculator.py # Task Group 1 tests
  test_night_charging.py  # Task Group 2 tests
  test_notifications.py   # Task Group 4 tests
  test_switch_control.py  # Task Group 5 tests
  test_night_charging_integration.py # Task Group 6 tests
  test_night_charging_gaps.py # Task Group 7 gap-filling tests
```

Files to be modified:
```
/workspace/blueprints/automation/charge_cheapest.yaml  # Task Group 3
```

---

## Technical Notes

### 15-Minute Granularity Implementation
- Tibber provides hourly prices; expand each hour to 4 identical 15-min slots
- Slot timestamps: HH:00, HH:15, HH:30, HH:45
- Sliding window operates on slots, not hours
- Duration conversion: `slots = int(math.ceil(duration_hours * 4))`

### Cross-Midnight Handling
- Reuse existing `spans_midnight()` and `fetch_prices_range()` from `cross_midnight.py`
- Build datetime objects from time inputs using reference date
- If end_time < start_time, end is on next calendar day

### Home Assistant Integration Points
- Switch control: `switch.turn_on`, `switch.turn_off` services
- Notifications: `persistent_notification.create` service
- Blueprint inputs: Standard Home Assistant selector types

### Error Handling Strategy
- Price fetch failure: Trigger configurable fallback
- Calculation failure: Log, notify, skip charging
- Switch control failure: Notify error, do not retry
- Always send error notification (unless opted out)
