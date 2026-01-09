# Task Breakdown: Evening Peak Configuration

## Overview
Total Tasks: 27 (across 5 task groups)

This feature enables users to configure evening peak hours and target SOC, with emergency charging logic when targets cannot be met through normal scheduling. Implementation follows Home Assistant Blueprint architecture using YAML/Jinja2.

## Task List

### Blueprint Configuration Layer

#### Task Group 1: Blueprint Input Configuration
**Dependencies:** None

- [x] 1.0 Complete blueprint input configuration
  - [x] 1.1 Write 3-5 focused tests for blueprint input validation
    - Test evening peak time inputs accept valid time format
    - Test evening_peak_target_soc accepts values in 20-100 range
    - Test default values are applied correctly
    - Test notification boolean input defaults to true
  - [x] 1.2 Add evening_peak_start time input
    - Default: 17:00:00
    - Use existing time selector pattern from `night_start_time`
    - Add to blueprint input variables section
  - [x] 1.3 Add evening_peak_end time input
    - Default: 21:00:00
    - Use existing time selector pattern from `day_start_time`
    - Add to blueprint input variables section
  - [x] 1.4 Add evening_peak_target_soc input
    - Default: 50
    - Selector: min: 20, max: 100, step: 5, unit: "%", mode: slider
    - Follow `night_target_soc` pattern
  - [x] 1.5 Add notify_emergency_charging boolean input
    - Default: true
    - Follow existing notification boolean input pattern
  - [x] 1.6 Add notification_service input
    - Allow users to specify preferred notification target
    - Use text selector with sensible default
  - [x] 1.7 Ensure blueprint input tests pass
    - Run ONLY the 3-5 tests written in 1.1
    - Verify inputs render correctly in Home Assistant UI

**Acceptance Criteria:**
- The 3-5 tests written in 1.1 pass
- All evening peak inputs appear in blueprint configuration UI
- Default values are applied correctly
- Input selectors match existing patterns in blueprint

---

### Schedule Validation Layer

#### Task Group 2: Schedule Conflict Validation
**Dependencies:** Task Group 1

- [x] 2.0 Complete schedule validation logic
  - [x] 2.1 Write 3-4 focused tests for schedule validation
    - Test validation passes when day_end_time is before evening_peak_start
    - Test validation fails when day_end_time overlaps evening_peak_start
    - Test error message is clear and actionable
  - [x] 2.2 Create Jinja2 validation template for day schedule overlap
    - Compare `day_end_time` against `evening_peak_start`
    - Ensure day charging window does not conflict with evening peak
  - [x] 2.3 Create Jinja2 validation for emergency charging window
    - Calculate pre-peak check time
    - Validate emergency charging window does not conflict with day schedule
  - [x] 2.4 Implement clear error message display
    - User-friendly message explaining the conflict
    - Suggest resolution (adjust day_end_time or evening_peak_start)
  - [x] 2.5 Ensure schedule validation tests pass
    - Run ONLY the 3-4 tests written in 2.1
    - Verify validation triggers correctly during blueprint configuration

**Acceptance Criteria:**
- The 3-4 tests written in 2.1 pass
- Overlapping schedules are detected at configuration time
- Clear error messages guide users to resolve conflicts
- Valid configurations pass without errors

---

### Automation Trigger Layer

#### Task Group 3: Pre-Peak SOC Monitoring Trigger
**Dependencies:** Task Group 1

- [x] 3.0 Complete pre-peak monitoring trigger
  - [x] 3.1 Write 3-4 focused tests for trigger logic
    - Test trigger fires at calculated time before evening_peak_start
    - Test trigger_id is correctly set to `evening_peak_check`
    - Test trigger calculation accounts for sufficient assessment time
  - [x] 3.2 Create time-based trigger for pre-peak check
    - Calculate trigger time based on `evening_peak_start`
    - Allow sufficient time for SOC assessment and potential charging
    - Use 1-hour buffer before evening_peak_start (configurable)
  - [x] 3.3 Implement trigger with trigger_id pattern
    - Set `trigger_id: evening_peak_check`
    - Follow pattern from `night_trigger` and `day_trigger`
  - [x] 3.4 Add trigger to blueprint automation section
    - Integrate with existing trigger list
    - Ensure trigger is enabled by default
  - [x] 3.5 Ensure trigger tests pass
    - Run ONLY the 3-4 tests written in 3.1
    - Verify trigger fires at correct time

**Acceptance Criteria:**
- The 3-4 tests written in 3.1 pass
- Trigger fires at appropriate time before evening peak
- Trigger ID follows existing naming pattern
- Integration with existing triggers works correctly

---

### Emergency Charging Logic Layer

#### Task Group 4: Emergency Charging Implementation
**Dependencies:** Task Groups 1, 2, 3

- [x] 4.0 Complete emergency charging logic
  - [x] 4.1 Write 5-6 focused tests for emergency charging
    - Test charging activates when SOC is below target
    - Test charging does not activate when SOC is at or above target
    - Test charging stops when target SOC is reached
    - Test charging stops at evening_peak_start if target not reached
    - Test charging duration calculation is correct
  - [x] 4.2 Implement SOC comparison logic
    - Compare current battery SOC against `evening_peak_target_soc`
    - Use `check_soc_skip_condition()` pattern from night_charging.py
    - Only proceed if SOC is below target
  - [x] 4.3 Calculate required charging duration
    - Use `get_dynamic_duration()` from duration_calculator.py
    - Apply `calculate_charging_duration()` for raw calculation
    - Apply `round_to_slot_boundary()` for 15-minute alignment
    - Use `validate_calculation_inputs()` for input validation
  - [x] 4.4 Calculate time remaining until evening_peak_start
    - Determine if target can be reached in available time
    - If insufficient time, plan to charge until evening_peak_start
  - [x] 4.5 Implement charging stop logic
    - Stop at target SOC reached
    - OR stop at evening_peak_start time
    - Whichever comes first
    - Use `calculate_charging_end_time()` from switch_control.py
  - [x] 4.6 Activate charging switch
    - Use `build_switch_service_call()` from switch_control.py
    - Follow `execute_night_charging_automation()` pattern
  - [x] 4.7 Add EVENING_PEAK to ChargingMode enum
    - Extend ChargingMode enum in day_charging.py
    - Use new mode for emergency charging sessions
  - [x] 4.8 Ensure emergency charging tests pass
    - Run ONLY the 5-6 tests written in 4.1
    - Verify all charging logic scenarios work correctly

**Acceptance Criteria:**
- The 5-6 tests written in 4.1 pass
- Emergency charging activates only when SOC is below target
- Charging stops correctly at target SOC or evening_peak_start
- Duration calculations are accurate
- Integration with existing charging infrastructure works

---

### Notification Layer

#### Task Group 5: Emergency Charging Notification
**Dependencies:** Task Group 4

- [x] 5.0 Complete notification system
  - [x] 5.1 Write 3-4 focused tests for notifications
    - Test notification is sent when emergency charging triggers
    - Test notification includes all required fields (current SOC, target SOC, time until peak)
    - Test notification respects notify_emergency_charging setting
    - Test notification uses configured notification_service
  - [x] 5.2 Add EMERGENCY to NotificationType enum
    - Extend NotificationType enum in notifications.py
    - Use for emergency charging notifications
  - [x] 5.3 Implement emergency notification message builder
    - Follow `build_notification_message()` pattern
    - Include: current SOC percentage
    - Include: target SOC percentage
    - Include: time until evening peak starts
    - Clear, actionable message content
  - [x] 5.4 Create notification payload
    - Use `create_notification_payload()` for Home Assistant service call
    - Target user-configured `notification_service`
  - [x] 5.5 Integrate notification with emergency charging workflow
    - Use `_add_notification()` helper pattern from night_charging.py
    - Respect `notify_emergency_charging` boolean setting
    - Send notification when emergency charging activates
  - [x] 5.6 Ensure notification tests pass
    - Run ONLY the 3-4 tests written in 5.1
    - Verify notifications are sent correctly

**Acceptance Criteria:**
- The 3-4 tests written in 5.1 pass
- Notifications include all required information
- Notification respects user opt-in/out setting
- Message is clear and informative

---

### Testing Layer

#### Task Group 6: Test Review and Gap Analysis
**Dependencies:** Task Groups 1-5

- [x] 6.0 Review existing tests and fill critical gaps
  - [x] 6.1 Review tests from Task Groups 1-5
    - Review 3-5 tests from blueprint inputs (Task 1.1)
    - Review 3-4 tests from schedule validation (Task 2.1)
    - Review 3-4 tests from trigger logic (Task 3.1)
    - Review 5-6 tests from emergency charging (Task 4.1)
    - Review 3-4 tests from notifications (Task 5.1)
    - Total existing tests: approximately 17-23 tests
  - [x] 6.2 Analyze test coverage gaps for evening peak feature only
    - Identify critical end-to-end workflows lacking coverage
    - Focus ONLY on this feature's requirements
    - Prioritize integration points over unit test gaps
  - [x] 6.3 Write up to 10 additional strategic tests maximum
    - End-to-end workflow: Configuration to charging activation
    - Integration: Emergency charging with existing night/day schedules
    - Integration: Notification delivery during emergency charging
    - Edge case: SOC exactly at target (should not trigger)
    - Edge case: Time exactly at evening_peak_start boundary
    - Do NOT write exhaustive edge case coverage
  - [x] 6.4 Run feature-specific tests only
    - Run ONLY tests related to evening peak configuration feature
    - Expected total: approximately 27-33 tests maximum
    - Do NOT run entire application test suite
    - Verify all critical workflows pass

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 27-33 tests total)
- Critical end-to-end workflows are covered
- No more than 10 additional tests added
- Testing focused exclusively on evening peak configuration feature

---

## Execution Order

Recommended implementation sequence:

1. **Blueprint Configuration Layer (Task Group 1)** - Foundation for all other tasks
2. **Schedule Validation Layer (Task Group 2)** - Depends on inputs being defined
3. **Automation Trigger Layer (Task Group 3)** - Can run parallel to Task Group 2
4. **Emergency Charging Logic Layer (Task Group 4)** - Core functionality, depends on inputs and triggers
5. **Notification Layer (Task Group 5)** - Depends on emergency charging being implemented
6. **Test Review and Gap Analysis (Task Group 6)** - Final validation after all implementation complete

## File Locations

Files to create or modify:

| Component | File Path | Action |
|-----------|-----------|--------|
| Blueprint | `blueprints/automation/charge_cheapest.yaml` | Modify |
| Duration Calculator | `scripts/duration_calculator.py` | Reference |
| Notifications | `scripts/notifications.py` | Modify |
| Switch Control | `scripts/switch_control.py` | Reference |
| Night Charging | `scripts/night_charging.py` | Reference |
| Day Charging | `scripts/day_charging.py` | Modify |
| Tests | `tests/test_evening_peak.py` | Create |

## Notes

- This feature builds on existing patterns from night and day charging schedules
- Emergency charging should integrate seamlessly with existing charging modes
- All time calculations must handle timezone correctly via Home Assistant
- Blueprint validation occurs at configuration time, not runtime
- Notification service must be user-configurable for flexibility
