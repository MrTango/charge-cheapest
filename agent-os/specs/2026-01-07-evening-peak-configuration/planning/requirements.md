# Spec Requirements: Evening Peak Configuration

## Initial Description

Create the spec folder structure with the dated folder format (YYYY-MM-DD-spec-name) and save the raw idea.

**Context from Roadmap (Item #8):**
Add configurable evening peak hours definition (e.g., 17:00-21:00). Calculate required afternoon SOC to cover evening consumption without grid dependency during expensive hours.

## Requirements Discussion

### First Round Questions

**Q1:** What time inputs are needed for evening peak configuration?
**Answer:** Users need to configure `evening_peak_start` and `evening_peak_end` times (e.g., 17:00-21:00) to define when expensive evening electricity prices occur.

**Q2:** What is the target SOC configuration for evening peak coverage?
**Answer:** Default 50% with a configurable range of 20%-100%. This represents the minimum battery charge level users want to have before evening peak hours begin.

**Q3:** How should emergency charging behave when target SOC cannot be reached by evening peak start?
**Answer:** Emergency charge should stop right before `evening_peak_start` OR when target SOC has been reached (whichever comes first). If target SOC cannot be reached within the available time, charge as much as possible before the evening peak begins.

**Q4:** How should schedule conflicts between day charging and evening peak be handled?
**Answer:** Validate and show an error during blueprint configuration if schedules overlap. This prevents misconfiguration where day charging window overlaps with evening peak hours.

**Q5:** What notification details should be included when emergency charging is triggered?
**Answer:** Include details (current SOC, target SOC, time until evening peak) and use a configurable notification service/target. This allows users to be informed when their battery will not meet the target SOC and emergency measures are being taken.

### Existing Code to Reference

**Similar Features Identified:**
- Feature: Night Charging Schedule - Implemented in blueprint (roadmap items 1-6 completed)
- Feature: Winter Day Charging Mode - Related feature (roadmap item 7, not yet implemented)
- Components to potentially reuse: SOC-based charge duration calculation, cheapest hours calculation logic, cross-midnight price fetching

The existing night charging implementation provides patterns for:
- Time window configuration (start/end time inputs)
- SOC target configuration
- Battery control entity integration
- Charging automation triggers

### Follow-up Questions

**Follow-up 1:** Target SOC Input - What should be the default value and valid range?
**Answer:** Default 50% with a range of 20%-100%

**Follow-up 2:** Emergency Charge Behavior - When should emergency charging stop?
**Answer:** Emergency charge should stop right before `evening_peak_start` OR when target SOC has been reached (whichever comes first). If target SOC cannot be reached within the hour, charge as much as possible.

**Follow-up 3:** Schedule Conflict Resolution - Should overlapping schedules be validated?
**Answer:** Yes, validate and show an error during blueprint configuration if schedules overlap.

**Follow-up 4:** Notification Details - What information should notifications include?
**Answer:** Include details (current SOC, target SOC, time until evening peak). Use a configurable notification service/target.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
Not applicable - no visual files were found in the planning/visuals/ folder.

## Requirements Summary

### Functional Requirements
- **Evening Peak Time Configuration**: Users can define evening peak start and end times (e.g., 17:00-21:00)
- **Target SOC Configuration**: Configurable target state of charge with default of 50% and range 20%-100%
- **Pre-Peak SOC Check**: System checks battery SOC before evening peak starts
- **Emergency Charging Logic**:
  - Triggers when SOC is below target as evening peak approaches
  - Stops at `evening_peak_start` OR when target SOC reached (whichever first)
  - Charges as much as possible if target cannot be reached in time
- **Schedule Validation**: Validates that day charging schedule does not overlap with evening peak hours; shows error if conflict detected
- **Notification System**:
  - Configurable notification service/target
  - Notification includes: current SOC, target SOC, time until evening peak
  - Triggered when emergency charging activates

### Reusability Opportunities
- Time window input pattern from night charging schedule
- SOC target input configuration pattern
- SOC-based charge duration calculation logic
- Battery control entity integration
- Charging automation start/stop patterns

### Scope Boundaries

**In Scope:**
- Evening peak time window configuration (start/end times)
- Target SOC configuration with default and valid range
- Emergency charging logic that respects evening peak start time
- Schedule overlap validation with day charging mode
- Configurable notifications with detailed information

**Out of Scope:**
- Solar forecast integration (roadmap item 9, separate spec)
- Dynamic morning SOC target adjustment (roadmap item 10, separate spec)
- Multi-battery support (roadmap item 11, separate spec)
- Historical consumption analysis for SOC recommendations
- Automatic evening peak detection based on price patterns

### Technical Considerations
- **Blueprint Architecture**: Implementation as Home Assistant Blueprint using YAML/Jinja2
- **Integration Points**:
  - Tibber integration for price data
  - Battery control entities (switch, script, or service call)
  - Notification services (configurable)
- **Validation**: Blueprint input validation for schedule conflicts
- **Dependencies**:
  - Relates to Winter Day Charging Mode (roadmap item 7)
  - Uses existing SOC calculation patterns from night charging
- **Constraints**:
  - Must work within Jinja2 templating limitations
  - Emergency charging must complete before evening peak start
  - Schedule validation must occur at configuration time
