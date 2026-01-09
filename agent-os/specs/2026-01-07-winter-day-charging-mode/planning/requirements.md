# Spec Requirements: Winter Day Charging Mode

## Initial Description
Winter Day Charging Mode - Implement secondary daytime charging schedule with separate time window configuration. Add enable/disable toggle for seasonal activation. Target evening peak coverage by charging during daytime price dips.

This is Roadmap Item #7, building on the completed foundation:
- #1 Blueprint Configuration Schema (complete)
- #2 Tibber Get Prices Service Integration (complete)
- #3 Cross-Midnight Price Fetching (complete)
- #4 Cheapest Hours Calculation Logic (complete)
- #5 Night Charging Automation (complete)
- #6 SOC-Based Charge Duration (complete)

## Requirements Discussion

### First Round Questions

**Q1:** I see the blueprint already has configuration inputs for the day schedule (day_schedule_enabled, day_start_time, day_end_time, day_target_soc, evening_peak_start, evening_peak_end). I assume the task is to implement the actual automation logic that uses these existing inputs rather than creating new configuration fields. Is that correct, or do you need additional configuration options?
**Answer:** Yes - implement automation logic using existing inputs, no new configuration fields needed

**Q2:** For the day charging trigger, I assume we should calculate the optimal daytime charging window once per day, likely triggered around the start of the day window (e.g., 09:00). Should this be a separate trigger time input, or should the automation automatically trigger at the configured day_start_time?
**Answer:** Yes - automation should automatically trigger at the configured `day_start_time`

**Q3:** For evening peak coverage, the mission mentions "target evening peak coverage." I assume this means we should calculate how much energy is needed to last through the evening peak period (17:00-21:00 by default) and charge accordingly. Should we: (a) Simply charge to the day_target_soc regardless of evening consumption, OR (b) Estimate evening consumption and calculate a dynamic SOC target to ensure coverage?
**Answer:** (a) Simply charge to the `day_target_soc` regardless of evening consumption

**Q4:** For the relationship between night and day charging, I assume the day schedule should operate independently - if night charging already achieved the night_target_soc but it depleted during morning usage, the day schedule kicks in to replenish. Is this the intended interaction, or should day charging consider what SOC was achieved overnight?
**Answer:** Independent - day schedule operates independently from night charging

**Q5:** For the cheapest hours calculation during daytime, I assume we should use the same 15-minute slot granularity implemented in the night charging automation. Should we also use the same charging duration calculation logic (based on SOC delta and battery capacity), or does day charging need different parameters?
**Answer:** Yes - use the same 15-minute slot granularity and charging duration calculation logic as night charging

**Q6:** For the enable/disable toggle (day_schedule_enabled), I assume this should be a simple boolean that the user can flip manually based on season. Should we also consider adding automatic seasonal detection (e.g., based on solar production forecasts or calendar dates), or is manual toggle sufficient for this iteration?
**Answer:** Yes manual - manual toggle is sufficient for this iteration, no automatic seasonal detection

**Q7:** For failure handling when daytime price data is unavailable, should we use the same failure_behavior configuration as night charging, or does day charging need its own fallback settings?
**Answer:** Yes - use the same `failure_behavior` configuration as night charging

**Q8:** Is there anything specific you want to exclude from this winter day charging mode that might seem like an obvious inclusion?
**Answer:** No response provided

### Existing Code to Reference

**Similar Features Identified:**
- Feature: Night Charging Automation - Path: `/workspace/blueprints/automation/charge_cheapest.yaml`
- Feature: SOC-Based Charge Duration Calculation - Already implemented in the blueprint's `calculated_charging_duration` variable
- Feature: Existing day schedule inputs - Already defined in blueprint (day_schedule_enabled, day_start_time, day_end_time, day_target_soc, evening_peak_start, evening_peak_end)

The spec-writer should reference the existing night charging automation logic in the blueprint and replicate the pattern for daytime charging.

### Follow-up Questions
None required - requirements are sufficiently clear.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
Not applicable.

## Requirements Summary

### Functional Requirements

**Core Automation Flow:**
- Trigger automation at the configured `day_start_time` when `day_schedule_enabled` is true
- Fetch price data for the day charging window (day_start_time to day_end_time)
- Calculate cheapest 15-minute slots using the same logic as night charging
- Calculate charging duration dynamically based on current SOC, day_target_soc, and battery capacity/charge rate
- Turn on charging switch at optimal start time within the day window
- Turn off charging switch after the calculated charging duration
- Skip charging entirely if battery SOC is already above day_target_soc at trigger time

**Enable/Disable Toggle:**
- Use existing `day_schedule_enabled` boolean input
- Manual toggle by user - no automatic seasonal detection
- When disabled, the day charging automation should not execute

**Independence from Night Charging:**
- Day schedule operates completely independently from night charging
- Does not consider or depend on night charging results
- Each schedule has its own SOC target (night_target_soc vs day_target_soc)

**Granularity:**
- Use 15-minute time slots for price calculation and scheduling (same as night charging)

**Charging Control:**
- Control charging via the same `battery_charging_switch` entity used by night charging
- Boolean switch control (no service calls)

**Notifications:**
- Use the same notification configuration as night charging
- Reuse existing notification toggles (notify_charging_scheduled, notify_charging_started, etc.)
- Notifications should indicate this is "Day Charging" to distinguish from night charging

**Failure Handling:**
- Use the same `failure_behavior` configuration as night charging
- Options: skip_charging, use_default_window, charge_immediately
- Use `default_charge_start_time` and `default_charge_duration` for fallback if applicable

**Existing Inputs Used (no new inputs needed):**
- `day_schedule_enabled` - Toggle to enable/disable day charging
- `day_start_time` - Day charging window start (also serves as trigger time)
- `day_end_time` - Day charging window end
- `day_target_soc` - Target SOC for day charging
- `evening_peak_start` - Evening peak start (informational, not used for calculation in this iteration)
- `evening_peak_end` - Evening peak end (informational, not used for calculation in this iteration)
- `battery_charging_switch` - Same switch as night charging
- `battery_soc_sensor` - Same SOC sensor as night charging
- `battery_capacity_sensor` - For charging duration calculation
- `battery_charging_power` - For charging duration calculation
- `failure_behavior` - Same failure behavior as night charging
- `default_charge_start_time` - Fallback start time
- `default_charge_duration` - Fallback duration
- Notification toggles (notify_charging_scheduled, etc.)

### Reusability Opportunities
- Existing night charging automation logic in `/workspace/blueprints/automation/charge_cheapest.yaml`
- Existing `calculated_charging_duration` variable template (adapt for day_target_soc)
- Existing cheapest slots calculation service call pattern
- Existing notification logic and configuration
- Existing failure handling logic

### Scope Boundaries

**In Scope:**
- Day charging automation with optimal timing during configured window
- 15-minute granularity scheduling (same as night charging)
- Boolean switch control for charging
- SOC-based skip logic (skip if already above day_target_soc)
- Dynamic charging duration calculation based on SOC delta
- Manual enable/disable toggle via day_schedule_enabled
- Same failure handling as night charging
- Same notification patterns as night charging

**Out of Scope:**
- New configuration inputs (use existing inputs only)
- Automatic seasonal detection (manual toggle only)
- Evening consumption estimation or dynamic evening coverage calculation
- Coordination or dependency between night and day charging
- Solar forecast integration (roadmap item #9)
- Multi-battery support (roadmap item #11)
- Automatic seasonal mode switching

### Technical Considerations

**Blueprint Structure:**
- Add new trigger for day_start_time (conditional on day_schedule_enabled)
- Add day charging action sequence parallel to night charging
- Reuse existing variable templates with adaptation for day_target_soc
- Follows YAML/Jinja2 approach as defined in tech-stack.md

**Charging Duration Calculation:**
- Adapt existing `calculated_charging_duration` template
- Use `day_target_soc` instead of `target_soc` for day charging
- Same formula: SOC delta * capacity / (charge power * efficiency)

**Price Data:**
- Day window typically does not span midnight, so cross-midnight handling may not be needed
- Still use the same price fetching approach for consistency

**Integration Points:**
- Uses existing `tibber.get_prices` service integration
- Uses existing cheapest slots calculation
- Integrates with Home Assistant notification system
- Uses same battery control entities as night charging

**State Management:**
- Store calculated day charging schedule
- Track charging start/stop times
- Monitor SOC sensor for skip logic
- Distinguish day charging events from night charging in logs/notifications
