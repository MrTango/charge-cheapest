# Specification: Night Charging Automation

## Goal
Create the core automation that triggers battery charging during the calculated cheapest night hours, using 15-minute granularity scheduling and configurable battery control entities with notification support.

## User Stories
- As a homeowner with a battery storage system, I want my battery to automatically charge during the cheapest night hours so that I minimize my electricity costs
- As a user, I want to receive notifications about charging events (start, stop, skip) so that I stay informed about my energy management

## Specific Requirements

**Automation Trigger and Timing**
- Trigger the automation at a configurable time before the night charging window begins
- Use a time-based trigger that runs once daily at the configured trigger time
- Default trigger should be approximately 30 minutes before night_start_time to allow price fetching and calculation
- Store the trigger time as a separate input configuration (not derived from night_start_time)

**Price Fetching for Night Window**
- Use the existing `fetch_prices_range()` function from `cross_midnight.py` to fetch prices spanning the night window
- Calculate start and end datetimes from night_start_time and night_end_time inputs
- Handle the cross-midnight scenario automatically (23:00 to 06:00 spans two calendar days)
- If price fetching fails, proceed to configurable fallback behavior

**15-Minute Slot Calculation**
- Adapt the cheapest hours calculation to work with 15-minute granularity instead of hourly
- Tibber provides hourly prices; expand each hourly price into four 15-minute slots with the same price
- Create a new function `find_cheapest_slots()` that works with 15-minute intervals
- Use sliding window algorithm similar to existing `find_cheapest_hours()` but with slot-based window size
- Convert charging duration (hours) to number of 15-minute slots (duration_hours * 4)

**SOC-Based Skip Logic**
- At the calculated start time, check the battery SOC sensor value
- If current SOC is greater than or equal to target_soc, skip charging entirely
- Send a "charging skipped" notification if SOC threshold is already met
- Do not recalculate or retry later in the same night window

**Charging Switch Control**
- Control charging via a boolean switch entity (turn on/off)
- Turn on the switch at the calculated optimal start time
- Turn off the switch after the configured charging duration elapses
- Use Home Assistant's `switch.turn_on` and `switch.turn_off` services
- Handle the case where charging duration extends beyond night_end_time (allow completion)

**Configurable Notifications**
- Support opt-in/opt-out for each notification type independently
- Notification types: charging_scheduled, charging_started, charging_completed, charging_skipped, charging_error
- Use Home Assistant's `persistent_notification.create` service for notifications
- Include relevant details in each notification (time, duration, estimated cost where applicable)
- Store notification preferences as boolean inputs in the blueprint

**Failure Handling with Configurable Defaults**
- Provide a configuration option for default behavior when price data is unavailable
- Options: skip_charging, use_default_window, charge_immediately
- If use_default_window is selected, require default_start_time and default_duration inputs
- Send error notification when fallback behavior is triggered
- Log all failures for debugging purposes

**Blueprint Input Configuration**
- battery_charging_switch: Switch entity for charging control
- battery_soc_sensor: Sensor entity for current SOC reading
- target_soc: Number input (0-100%) threshold for skip logic
- charging_duration_hours: Number input for fixed charging duration
- night_start_time: Time input for window start (default 23:00)
- night_end_time: Time input for window end (default 06:00)
- trigger_time: Time input for automation trigger (default 22:30)
- failure_behavior: Selector for fallback behavior option
- Individual boolean inputs for each notification type opt-out

## Visual Design
No visual assets provided.

## Existing Code to Leverage

**`/workspace/tibber_prices/cross_midnight.py` - Cross-Midnight Price Fetching**
- `fetch_prices_range()` handles both same-day and cross-midnight scenarios automatically
- `spans_midnight()` detects if time range crosses midnight boundary
- Already integrates with `tibber_price_service.py` for actual API calls
- Returns normalized, sorted price entries ready for calculation

**`/workspace/tibber_prices/cheapest_hours.py` - Cheapest Hours Algorithm**
- `find_cheapest_hours()` implements sliding window algorithm for finding optimal window
- `_sliding_window_minimum()` contains the core optimization logic
- Supports optional time window constraints
- Returns structured result with start_datetime, hours list, and total_cost
- Needs adaptation for 15-minute slots (multiply window size by 4)

**`/workspace/tibber_prices/price_normalizer.py` - Price Data Normalization**
- `normalize_price_entries()` converts raw API response to consistent format
- `parse_timestamp()` handles ISO 8601 timestamps with timezone preservation
- `convert_to_hourly()` already exists for aggregation; inverse logic can expand hourly to 15-min

**`/workspace/blueprints/automation/charge_cheapest.yaml` - Blueprint Schema**
- Contains existing input definitions for night_start_time, night_end_time, night_target_soc
- Defines battery_charging_switch and price_sensor inputs
- Follows Home Assistant blueprint YAML structure
- Extend this schema with new inputs for SOC sensor, notifications, failure behavior

## Out of Scope
- SOC-based charge duration calculation (deferred to roadmap item #6 "SOC-Based Charge Duration")
- Service call or script-based charging control (boolean switch only for this iteration)
- Winter day charging mode (roadmap item #7)
- Solar forecast integration (roadmap item #9)
- Multi-battery support (roadmap item #11)
- Dynamic recalculation during the night window (daily calculation only)
- Real-time price monitoring and rescheduling
- Web UI or dashboard for configuration (blueprint inputs only)
- Cost tracking or historical analytics
- Integration with other energy providers besides Tibber
