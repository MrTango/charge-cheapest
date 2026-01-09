# Spec Requirements: Blueprint Configuration Schema

## Initial Description

The blueprint needs a configuration schema allowing users to configure:
- Night schedule (start/end times, target SOC, target time)
- Day/winter schedule (start/end times for winter charging)
- Tibber sensor configuration
- Solar forecast integration settings
- Integration with the cheapest-energy-hours macro

## Requirements Discussion

### First Round Questions

**Q1:** I assume the night charging window will use time inputs with defaults of 23:00 (start) and 06:00 (end). Is that correct, or would you prefer different defaults?
**Answer:** Night window defaults 23:00-06:00 - CONFIRMED

**Q2:** For the target SOC (State of Charge), I'm thinking of using a number slider with a range of 0-100% and a default of 60%. Should we also include a minimum SOC threshold (below which charging always triggers regardless of price)?
**Answer:** Target SOC must be reached regardless of price - price only determines WHEN to charge (cheapest hours), but target SOC is always achieved

**Q3:** The target time (when charging should be complete) - I assume this defaults to the end of the night window (06:00). Should users be able to set an earlier completion time, like 05:00, to ensure the battery is ready before they wake up?
**Answer:** Both start and end times should be configurable

**Q4:** For winter day charging, I'm planning a toggle (input_boolean style) to enable/disable it, with a separate time window (e.g., 09:00-16:00 default). Should this also have its own SOC target, or reuse the night target?
**Answer:** Boolean toggle to enable second day schedule with its OWN target SOC and start/end values (separate from night)

**Q5:** The evening peak hours you mentioned (for coverage calculation) - I assume defaults of 17:00-21:00. Should users configure both start and end, or just define "cover until X o'clock"?
**Answer:** Evening peak schedule also needs configurable start/end times

**Q6:** Based on the ha-sensor-states.md, I see the Tibber sensor uses `today` and `tomorrow` attributes with `total` as the value key. I assume we'll use an entity selector with a default filter for `sensor.electricity_price*`. Should we also expose `attr_today`, `attr_tomorrow`, and `value_key` as advanced/optional inputs for users with non-standard Tibber setups?
**Answer:** Single input field for sensor name - user will prepare data via template sensor if needed (no advanced attr options)

**Q7:** For controlling the battery charging, I'm thinking of supporting three options: a switch entity (toggle on/off), a script entity (call a script), or a service call. Which approach should be the primary/default, and should we support all three?
**Answer:** Switch entity (toggle/bool) for now, BUT also allow setting the charging power input value for the charger

**Q8:** The macro has many advanced parameters (like `look_ahead`, `latest_possible`, `price_tolerance`, `weight`). Should these be hidden entirely, exposed as advanced options, or set with sensible defaults internally?
**Answer:** Set sensible defaults internally for now

**Q9:** What should happen if tomorrow's prices aren't available yet (typically before 13:00)? I assume we either skip charging decisions or use a fallback strategy. What's your preference?
**Answer:** Estimate unknown hours until data arrives at 1pm, so charging can happen before 1pm if user configures it that way

**Q10:** Is there anything specific you want to exclude from this first version of the configuration schema, such as multi-battery support or solar forecast integration (which are later roadmap items)?
**Answer:** (Answered in follow-up)

### Existing Code to Reference

No similar existing features identified for reference.

### Follow-up Questions

**Follow-up 1:** Charging Power Input - Should this be a static number input, an entity selector pointing to an input_number, or both?
**Answer:** Entity selector pointing to an `input_number` - user selects the entity that controls charger power

**Follow-up 2:** Price Estimation for Missing Hours - What method should we use when tomorrow's prices aren't available?
**Answer:** Use the same prices as the last 3 hours before 1pm have (so repeat/extend those prices for unknown future hours)

**Follow-up 3:** Scope for v1 - Which features should be excluded?
**Answer:** Exclude from v1: Multi-battery support, Solar forecast integration, Dynamic SOC calculation based on expected consumption

**Follow-up 4:** Existing Code Reference - Any existing automations or templates to reference?
**Answer:** No existing code reference provided

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
N/A

## Requirements Summary

### Functional Requirements

#### Night Schedule Configuration
- Start time input (time selector, default: 23:00)
- End time input (time selector, default: 06:00)
- Target SOC percentage (number slider 0-100%, default: 60%)
- Target SOC is always achieved; price only determines the optimal charging window within the schedule

#### Day/Winter Schedule Configuration
- Enable toggle (boolean, default: off)
- Start time input (time selector, default: 09:00)
- End time input (time selector, default: 16:00)
- Own target SOC percentage (number slider 0-100%, separate from night target)

#### Evening Peak Schedule Configuration
- Start time input (time selector, default: 17:00)
- End time input (time selector, default: 21:00)
- Used for calculating required SOC to cover expensive evening hours

#### Tibber Sensor Configuration
- Single entity selector for the price sensor
- User is responsible for preparing data in expected format via template sensor if needed
- No advanced attribute configuration exposed (uses standard Tibber format internally)

#### Battery Control Configuration
- Switch entity selector (toggle for charging on/off)
- Input_number entity selector for charging power setting
- Charging power entity used to calculate required charging duration

#### Internal/Advanced Settings (Not Exposed to User)
- cheapest-energy-hours macro parameters with sensible defaults:
  - `attr_today`: 'today'
  - `attr_tomorrow`: 'tomorrow'
  - `value_key`: 'total'
  - `datetime_in_data`: false
  - `mode`: 'is_now' (for automation triggers)
  - Other params: internal defaults
- Price estimation strategy: Use last 3 hours before 1pm to estimate unknown future prices

### Reusability Opportunities

No existing components identified for reuse. This is a new blueprint implementation.

Reference documentation:
- cheapest-energy-hours macro: https://github.com/TheFes/cheapest-energy-hours
- Tibber sensor format documented in `/home/maik/develop/homeassistant/tibber-cheapest-hours/ha-sensor-states.md`

### Scope Boundaries

**In Scope:**
- Night charging schedule with configurable time window and SOC target
- Day/winter charging schedule with enable toggle and separate SOC target
- Evening peak hours configuration
- Tibber price sensor entity selection
- Battery charging switch control
- Charging power input_number selection
- Integration with cheapest-energy-hours macro (internal defaults)
- Price estimation for missing future hours (repeat last 3 hours before 1pm)

**Out of Scope:**
- Multi-battery support (deferred to roadmap item 10)
- Solar forecast integration (deferred to roadmap items 8-9)
- Dynamic SOC calculation based on expected consumption
- Advanced cheapest-energy-hours macro parameter exposure
- Advanced Tibber sensor attribute configuration
- Script or service call alternatives for battery control

### Technical Considerations

- Blueprint uses Home Assistant's native input selectors (time, number, entity, boolean)
- Entity selectors should filter appropriately:
  - Price sensor: domain filter for `sensor`
  - Battery switch: domain filter for `switch`
  - Charging power: domain filter for `input_number`
- Time inputs use 24-hour format
- SOC targets are percentages (0-100)
- Price estimation logic needed for schedules that span before 1pm when tomorrow's prices unavailable
- cheapest-energy-hours macro must be installed as prerequisite (via HACS or manual)
