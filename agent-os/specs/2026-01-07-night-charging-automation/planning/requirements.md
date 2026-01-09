# Spec Requirements: Night Charging Automation

## Initial Description
Night Charging Automation - Create the core automation that triggers battery charging during the calculated cheapest night hours using configurable battery control entities.

This is Roadmap Item #5, building on the completed foundation:
- #1 Blueprint Configuration Schema (complete)
- #2 Tibber Get Prices Service Integration (complete)
- #3 Cross-Midnight Price Fetching (complete)
- #4 Cheapest Hours Calculation Logic (complete)

## Requirements Discussion

### First Round Questions

**Q1:** For the automation flow, I assume we need to: (a) trigger at a configurable time before the night window starts, (b) use the existing cross-midnight price fetching to get prices for the full window, (c) calculate the cheapest hours using the existing logic, and (d) turn on the charging switch at the optimal start time and turn it off after the charging duration. Is that the correct flow?
**Answer:** Yes, correct - trigger before window, use cross-midnight price fetching, calculate cheapest hours, turn on/off switch

**Q2:** For the battery SOC sensor, I assume the blueprint already has an input for the battery SOC sensor entity from the configuration schema. Should we use that existing input, or does this automation need a separate sensor configuration?
**Answer:** Yes, require a separate battery SOC sensor entity

**Q3:** For the charging window granularity, the existing cheapest hours calculation appears to work with whole hours. Should we keep this hourly granularity for the night charging, or do you need finer control (e.g., 15-minute or 30-minute slots)?
**Answer:** Use 15-minute granularity (not whole hours)

**Q4:** For recalculation timing, I assume we calculate cheapest hours once per night (when the automation triggers before the window). Should we also support re-calculation if prices update mid-window, or is daily calculation sufficient for this iteration?
**Answer:** Daily recalculation, skip charging if SOC is above target at start datetime

**Q5:** For the charging control, the roadmap mentions "switch, script, or service call". Should we support all three options, or should we start with just the switch entity for this initial implementation?
**Answer:** Keep it as a boolean switch (no service calls needed)

**Q6:** For notifications/logging, should the automation: (a) create Home Assistant notifications when charging starts/stops, (b) log events for debugging, (c) expose sensors showing next scheduled charge time and estimated cost, or (d) none of these for the initial version?
**Answer:** Yes to notifications, but they should be configurable with opt-out options for each

**Q7:** For failure handling, if price data is unavailable or the calculation fails, should the automation: (a) skip charging for that night, (b) charge during a configurable default window, or (c) send a notification and wait for manual intervention?
**Answer:** Use configurable default behavior

**Q8:** Is there anything specific you want to exclude from this automation that might seem like an obvious inclusion?
**Answer:** Charging duration should use a fixed number of charging hours for now (defer SOC-based calculation to roadmap item #6 "SOC-Based Charge Duration")

### Existing Code to Reference

**Similar Features Identified:**
- Feature: Cross-Midnight Price Fetching - Roadmap item #3 (complete)
- Feature: Cheapest Hours Calculation Logic - Roadmap item #4 (complete)
- Feature: Blueprint Configuration Schema - Roadmap item #1 (complete)
- Feature: Tibber Get Prices Service Integration - Roadmap item #2 (complete)

User did not provide specific file paths to reference. The spec-writer should locate the existing blueprint implementation to understand the current structure.

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
- Trigger automation at a configurable time before the night charging window begins
- Fetch price data using existing cross-midnight price fetching capability
- Calculate cheapest 15-minute slots using existing calculation logic (adapted for 15-minute granularity)
- Turn on charging switch at optimal start time
- Turn off charging switch after the configured charging duration
- Skip charging entirely if battery SOC is already above target at start time

**Granularity:**
- Use 15-minute time slots for price calculation and scheduling
- This differs from the existing hourly implementation and may require adaptation

**Charging Control:**
- Control charging via a boolean switch entity
- No service calls or scripts required for initial implementation

**Notifications (Configurable):**
- Each notification type should have an opt-out option
- Suggested notification events:
  - Charging scheduled (with time and estimated cost)
  - Charging started
  - Charging completed
  - Charging skipped (SOC already above target)
  - Error/failure notification

**Failure Handling:**
- Configurable default behavior when price data is unavailable
- Options should include: skip charging, use default window, or other configurable fallback

**Inputs Required:**
- Charging switch entity (boolean switch)
- Battery SOC sensor entity
- Target SOC threshold (to determine if charging should be skipped)
- Fixed charging duration (in hours or minutes)
- Night window start time
- Night window end time
- Trigger time (before window)
- Notification preferences (opt-in/opt-out per notification type)
- Default behavior for failures

### Reusability Opportunities
- Existing cross-midnight price fetching logic (roadmap item #3)
- Existing cheapest hours calculation logic (roadmap item #4, needs 15-minute adaptation)
- Existing blueprint configuration schema (roadmap item #1)
- Existing Tibber service integration (roadmap item #2)

### Scope Boundaries

**In Scope:**
- Night charging automation with optimal timing
- 15-minute granularity scheduling
- Boolean switch control for charging
- SOC-based skip logic (skip if already above target)
- Configurable notifications with opt-out
- Configurable failure handling with default behavior
- Fixed charging duration input

**Out of Scope:**
- SOC-based charge duration calculation (deferred to roadmap item #6)
- Service call or script-based charging control
- Winter day charging mode (roadmap item #7)
- Solar forecast integration (roadmap item #9)
- Multi-battery support (roadmap item #11)
- Dynamic recalculation during the window

### Technical Considerations

**15-Minute Granularity:**
- The existing calculation logic appears to use hourly granularity
- Tibber typically provides hourly price data
- Implementation may need to:
  - Interpolate hourly prices to 15-minute slots, OR
  - Request 15-minute data if Tibber supports it
  - Adapt the cheapest hours calculation for finer granularity

**Integration Points:**
- Uses existing `tibber.get_prices` service integration
- Uses existing cross-midnight price fetching
- Uses existing cheapest hours calculation (adapted for 15-minute slots)
- Integrates with Home Assistant notification system

**Blueprint Structure:**
- Should extend the existing blueprint configuration schema
- Follows YAML/Jinja2 approach as defined in tech-stack.md
- May fall back to Python if 15-minute calculation complexity requires it

**State Management:**
- Store calculated charging schedule for the night
- Track charging start/stop times
- Monitor SOC sensor for skip logic
