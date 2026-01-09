# Specification: Winter Day Charging Mode

## Goal
Implement a secondary daytime charging schedule that operates independently from night charging, enabling users to charge their battery during daytime price dips to cover evening peak consumption periods during winter months.

## User Stories
- As a homeowner with a battery system, I want to charge my battery during cheap daytime hours so that I have sufficient capacity to avoid expensive evening peak electricity prices
- As a seasonal user, I want to enable/disable day charging manually so that I only use this feature during winter months when solar production is low

## Specific Requirements

**Day Charging Trigger Logic**
- Trigger automation at the configured `day_start_time` when `day_schedule_enabled` is true
- Use Home Assistant time platform trigger, matching the pattern from night charging
- Automation should not execute when `day_schedule_enabled` is false
- Trigger independently from night charging schedule (no coordination or dependency)

**Price Data Fetching for Day Window**
- Fetch Tibber price data for the window between `day_start_time` and `day_end_time`
- Use the same `tibber_prices.find_cheapest_slots` service call pattern as night charging
- Day window typically does not span midnight, simplifying the price fetch compared to night charging
- Use existing `price_sensor` entity configured in the blueprint

**Cheapest Slots Calculation**
- Use identical 15-minute slot granularity as implemented in night charging
- Find the cheapest contiguous window within the day charging period
- Pass the dynamically calculated charging duration to the service
- Receive `start_datetime` and `end_datetime` response for scheduling

**Dynamic Charging Duration Calculation**
- Create a `day_calculated_charging_duration` variable template parallel to the existing `calculated_charging_duration`
- Use `day_target_soc` instead of `target_soc` for the SOC delta calculation
- Formula: energy_needed_kwh = (soc_delta / 100) * capacity_kwh; hours_needed = energy_needed_kwh / (charge_power_kw * 0.95)
- Round up to nearest 15-minute slot (multiply hours by 4, ceil, divide by 4)
- Fall back to `charging_duration_hours` when sensor values are unavailable

**SOC-Based Skip Logic**
- Check current SOC via `battery_soc_sensor` at trigger time
- Skip charging entirely if current SOC >= `day_target_soc`
- Use template condition matching the night charging pattern
- Send "charging skipped" notification when SOC threshold already met

**Charging Switch Control**
- Use the same `battery_charging_switch` entity as night charging
- Turn on switch at `cheapest_slots.start_datetime`
- Turn off switch at `cheapest_slots.end_datetime`
- Boolean switch control only (no service calls for charging rate adjustment)

**Failure Handling**
- Use the shared `failure_behavior` configuration (skip_charging, use_default_window, charge_immediately)
- When `use_default_window`: use `default_charge_start_time` and `default_charge_duration` as fallback
- When `skip_charging`: do not charge and optionally send error notification
- When `charge_immediately`: start charging at trigger time for default duration
- Send error notification when `notify_charging_error` is enabled

**Notification Integration**
- Reuse existing notification toggles: `notify_charging_scheduled`, `notify_charging_started`, `notify_charging_completed`, `notify_charging_skipped`, `notify_charging_error`
- Prefix notification titles with "Day Charging" to distinguish from night charging
- Include charging window times, duration, and estimated cost in scheduled notification
- Use `persistent_notification.create` service with unique `notification_id` for day charging

**Blueprint Structure**
- Add second time trigger for `day_start_time` with condition on `day_schedule_enabled`
- Add day charging action sequence in the action block
- Use choose/conditions to route between night and day charging logic based on trigger
- Maintain existing night charging logic unchanged

## Visual Design
No visual assets provided.

## Existing Code to Leverage

**Night Charging Automation Pattern (`/workspace/blueprints/automation/charge_cheapest.yaml`)**
- Replicate the trigger-condition-action structure for day charging
- Follow the same service call pattern for `tibber_prices.find_cheapest_slots`
- Use identical switch control approach with `switch.turn_on` and `switch.turn_off`
- Match the notification pattern with `persistent_notification.create`

**`calculated_charging_duration` Variable Template**
- Adapt for day charging by creating `day_calculated_charging_duration` variable
- Replace `target_soc` reference with `day_target_soc`
- Keep all other calculation logic identical (capacity detection, power conversion, efficiency factor)
- Maintain the same fallback to `charging_duration_hours`

**Existing Blueprint Input Definitions**
- All required inputs already exist: `day_schedule_enabled`, `day_start_time`, `day_end_time`, `day_target_soc`
- `evening_peak_start` and `evening_peak_end` inputs exist but are informational only for this iteration
- Reuse `failure_behavior`, `default_charge_start_time`, `default_charge_duration` for failure handling
- Reuse all notification toggle inputs and entity selection inputs

**SOC Skip Condition Template**
- Adapt the existing condition template: `{{ states(battery_soc_sensor) | float(0) < day_target_soc | float(50) }}`
- Same pattern, different SOC target variable

**Notification Message Templates**
- Follow existing message format for charging scheduled notification
- Use timestamp formatting: `as_timestamp | timestamp_custom('%H:%M')`
- Include duration and estimated cost from cheapest_slots response

## Out of Scope
- New configuration inputs (use only existing blueprint inputs)
- Automatic seasonal detection or calendar-based enable/disable
- Evening consumption estimation or dynamic SOC target calculation
- Coordination or dependency between night and day charging schedules
- Solar forecast integration for charging decisions
- Multi-battery support or multi-charger coordination
- Grid export avoidance logic during day charging
- Time-of-use tariff integration beyond Tibber prices
- Automatic mode switching based on weather or solar production
- Cross-midnight day charging windows (day window assumed to be within same calendar day)
