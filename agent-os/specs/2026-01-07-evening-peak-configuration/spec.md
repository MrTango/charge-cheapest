# Specification: Evening Peak Configuration

## Goal
Enable users to configure evening peak hours (e.g., 17:00-21:00) and define a target battery SOC to ensure sufficient charge before expensive evening electricity rates begin, with emergency charging logic when the target cannot be met through normal scheduling.

## User Stories
- As a homeowner, I want to configure evening peak hours so that my battery has sufficient charge before expensive electricity rates begin
- As a user with variable consumption patterns, I want notifications when emergency charging is needed so that I understand when my battery may not cover the full evening peak period

## Specific Requirements

**Evening Peak Time Window Configuration**
- Add `evening_peak_start` time input (default: 17:00:00) using existing blueprint time selector pattern
- Add `evening_peak_end` time input (default: 21:00:00) using existing blueprint time selector pattern
- Time inputs should follow the same format as `night_start_time` and `day_start_time` in the existing blueprint
- Store both values as blueprint input variables for use in automation logic

**Target SOC Configuration for Evening Peak**
- Add `evening_peak_target_soc` input with default value of 50%
- Configure selector with min: 20, max: 100, step: 5, unit: "%" and slider mode
- Follow the same pattern as `night_target_soc` and `day_target_soc` inputs in the existing blueprint
- This represents the minimum desired battery level before `evening_peak_start`

**Pre-Peak SOC Monitoring Trigger**
- Create a new time-based trigger that fires at a calculated time before `evening_peak_start`
- The trigger time should allow sufficient time to assess SOC and potentially initiate emergency charging
- Use the existing `trigger_id` pattern (similar to `night_trigger` and `day_trigger`) with id `evening_peak_check`

**Emergency Charging Logic**
- When triggered, compare current SOC against `evening_peak_target_soc`
- If current SOC is below target, calculate required charging duration using `duration_calculator.py` patterns
- Calculate time remaining until `evening_peak_start` to determine if target can be reached
- If target cannot be reached, charge as much as possible until `evening_peak_start`
- Stop emergency charging at whichever comes first: target SOC reached OR `evening_peak_start` time

**Schedule Conflict Validation**
- Validate that `day_end_time` does not overlap with `evening_peak_start`
- Validate that emergency charging window does not conflict with day charging schedule
- Implement validation at blueprint configuration time using Jinja2 template conditions
- Display clear error message to user when schedule conflicts are detected

**Emergency Charging Notification**
- Add `notify_emergency_charging` boolean input (default: true) following existing notification input pattern
- Add configurable `notification_service` input to allow users to specify their preferred notification target
- Notification message must include: current SOC percentage, target SOC percentage, time until evening peak starts
- Use `NotificationType` enum pattern from `notifications.py` - add new `EMERGENCY` type
- Follow `build_notification_message` pattern for message construction

**Integration with Existing Charging Schedules**
- Evening peak configuration should work alongside night and day charging schedules
- Emergency charging should only activate if SOC is below target when the pre-peak check triggers
- Normal day charging (if enabled and scheduled) should be prioritized over emergency charging
- Use existing `ChargingMode` enum pattern from `day_charging.py` - add `EVENING_PEAK` mode

## Visual Design
No visual assets provided.

## Existing Code to Leverage

**Blueprint Input Pattern (`charge_cheapest.yaml`)**
- Reuse time selector pattern from `night_start_time`, `day_start_time` inputs
- Reuse SOC percentage selector pattern from `night_target_soc`, `day_target_soc` inputs
- Reuse notification boolean input pattern from `notify_charging_scheduled`, etc.
- Evening peak inputs already partially scaffolded (lines 105-118)

**Duration Calculator (`duration_calculator.py`)**
- Use `get_dynamic_duration()` to calculate required charging time to reach target SOC
- Leverage `calculate_charging_duration()` for raw duration calculation
- Apply `round_to_slot_boundary()` for 15-minute slot alignment
- Use `validate_calculation_inputs()` for input validation

**Notification System (`notifications.py`)**
- Extend `NotificationType` enum with new `EMERGENCY` type
- Follow `build_notification_message()` pattern for emergency notification content
- Use `create_notification_payload()` for Home Assistant service call formatting
- Leverage `NotificationConfig` dataclass pattern for opt-in/out settings

**Switch Control (`switch_control.py`)**
- Use `build_switch_service_call()` for emergency charging switch activation
- Use `calculate_charging_end_time()` to determine when emergency charging should stop

**Night Charging Orchestration (`night_charging.py`)**
- Follow `execute_night_charging_automation()` pattern for emergency charging workflow
- Reuse `check_soc_skip_condition()` logic for SOC threshold comparison
- Use `_add_notification()` helper pattern for notification integration

## Out of Scope
- Solar forecast integration for predicting afternoon SOC (roadmap item 9, separate spec)
- Dynamic morning SOC target adjustment based on consumption (roadmap item 10, separate spec)
- Multi-battery support and coordination (roadmap item 11, separate spec)
- Historical consumption analysis for automatic SOC recommendations
- Automatic evening peak detection based on Tibber price patterns
- Machine learning for consumption prediction
- Weather-based consumption adjustments
- User-configurable emergency charging power levels (uses same power setting as normal charging)
- Integration with EV charging schedules
- Weekend vs weekday evening peak schedule variations
