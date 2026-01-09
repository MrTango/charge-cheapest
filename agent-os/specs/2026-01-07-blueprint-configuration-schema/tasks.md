# Task Breakdown: Blueprint Configuration Schema

## Overview
Total Tasks: 18

This spec defines the input configuration schema for the Charge Cheapest blueprint. The implementation is YAML + Jinja2 based (Home Assistant Blueprint), not a traditional database/API/UI stack.

**Task Ordering Strategy:** Breadth-first Task Completion Approach (BTCA) - All similar-type work is grouped and completed together before moving to the next layer.

## Task List

### Blueprint Foundation

#### Task Group 1: Blueprint Metadata and Structure
**Dependencies:** None

- [x] 1.0 Complete blueprint foundation
  - [x] 1.1 Write 2-4 focused tests for blueprint structure validation
    - Test that blueprint YAML parses without errors
    - Test that required metadata fields (name, description, domain) are present
    - Test that input section exists with expected structure
  - [x] 1.2 Create blueprint file at `blueprints/automation/charge_cheapest.yaml`
    - Add blueprint metadata header (blueprint name, description, domain: automation)
    - Add source URL for sharing
    - Follow Home Assistant blueprint structure conventions
  - [x] 1.3 Define input section skeleton
    - Create empty input block structure
    - Add descriptive section comments for organization
  - [x] 1.4 Ensure blueprint foundation tests pass
    - Run ONLY the 2-4 tests written in 1.1
    - Verify YAML syntax is valid
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- Blueprint file exists at correct location
- YAML syntax validates without errors
- Metadata fields present (name, description, domain)
- The 2-4 foundation tests pass

---

### Schedule Configuration Inputs

#### Task Group 2: Night Schedule Inputs
**Dependencies:** Task Group 1

- [x] 2.0 Complete night schedule configuration inputs
  - [x] 2.1 Write 2-4 focused tests for night schedule inputs
    - Test night_start_time input exists with time selector and default 23:00
    - Test night_end_time input exists with time selector and default 06:00
    - Test night_target_soc input exists with number selector (0-100, default 60, step 5)
  - [x] 2.2 Add night_start_time input
    - Selector type: time
    - Default: "23:00:00"
    - Name: "Night Schedule Start Time"
    - Description: "When the night charging window begins"
  - [x] 2.3 Add night_end_time input
    - Selector type: time
    - Default: "06:00:00"
    - Name: "Night Schedule End Time"
    - Description: "When the night charging window ends (next calendar day)"
  - [x] 2.4 Add night_target_soc input
    - Selector type: number
    - Min: 0, Max: 100, Step: 5
    - Default: 60
    - Unit: "%"
    - Mode: slider
    - Name: "Night Target SOC"
    - Description: "Target state of charge for night charging (will always be reached)"
  - [x] 2.5 Ensure night schedule tests pass
    - Run ONLY the 2-4 tests written in 2.1
    - Verify inputs render correctly in blueprint UI
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- Night schedule inputs defined with correct selectors
- Default values match spec (23:00, 06:00, 60%)
- SOC slider has correct range and step
- The 2-4 night schedule tests pass

---

#### Task Group 3: Day/Winter Schedule Inputs
**Dependencies:** Task Group 1

- [x] 3.0 Complete day/winter schedule configuration inputs
  - [x] 3.1 Write 2-4 focused tests for day schedule inputs
    - Test day_schedule_enabled input exists with boolean selector and default false
    - Test day_start_time and day_end_time inputs exist with correct defaults
    - Test day_target_soc input is independent from night_target_soc
  - [x] 3.2 Add day_schedule_enabled input
    - Selector type: boolean
    - Default: false
    - Name: "Enable Day Schedule"
    - Description: "Enable secondary charging window for winter months"
  - [x] 3.3 Add day_start_time input
    - Selector type: time
    - Default: "09:00:00"
    - Name: "Day Schedule Start Time"
    - Description: "When the day charging window begins"
  - [x] 3.4 Add day_end_time input
    - Selector type: time
    - Default: "16:00:00"
    - Name: "Day Schedule End Time"
    - Description: "When the day charging window ends"
  - [x] 3.5 Add day_target_soc input
    - Selector type: number
    - Min: 0, Max: 100, Step: 5
    - Default: 50
    - Unit: "%"
    - Mode: slider
    - Name: "Day Target SOC"
    - Description: "Target state of charge for day charging (independent from night target)"
  - [x] 3.6 Ensure day schedule tests pass
    - Run ONLY the 2-4 tests written in 3.1
    - Verify toggle enables/disables day schedule concept
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- Day schedule inputs defined with correct selectors
- Boolean toggle defaults to off
- Day SOC is separate input from night SOC (default 50%)
- The 2-4 day schedule tests pass

---

#### Task Group 4: Evening Peak Schedule Inputs
**Dependencies:** Task Group 1

- [x] 4.0 Complete evening peak schedule configuration inputs
  - [x] 4.1 Write 2 focused tests for evening peak inputs
    - Test evening_peak_start and evening_peak_end inputs exist with time selectors
    - Test defaults are 17:00 and 21:00 respectively
  - [x] 4.2 Add evening_peak_start input
    - Selector type: time
    - Default: "17:00:00"
    - Name: "Evening Peak Start Time"
    - Description: "When expensive evening peak period begins"
  - [x] 4.3 Add evening_peak_end input
    - Selector type: time
    - Default: "21:00:00"
    - Name: "Evening Peak End Time"
    - Description: "When expensive evening peak period ends"
  - [x] 4.4 Ensure evening peak tests pass
    - Run ONLY the 2 tests written in 4.1
    - Verify inputs are informational (not a charging window)
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- Evening peak inputs defined with correct selectors
- Default values match spec (17:00-21:00)
- The 2 evening peak tests pass

---

### Entity Selection Inputs

#### Task Group 5: Tibber Sensor and Battery Control Entity Inputs
**Dependencies:** Task Group 1

- [x] 5.0 Complete entity selection inputs
  - [x] 5.1 Write 3-4 focused tests for entity inputs
    - Test price_sensor input uses entity selector with domain filter for sensor
    - Test battery_charging_switch input uses entity selector with domain filter for switch
    - Test battery_charging_power input uses entity selector with domain filter for input_number
    - Test all entity inputs are required (no defaults)
  - [x] 5.2 Add price_sensor input
    - Selector type: entity
    - Domain filter: sensor
    - Multiple: false
    - Name: "Tibber Price Sensor"
    - Description: "Sensor with today/tomorrow price attributes (standard Tibber format)"
  - [x] 5.3 Add battery_charging_switch input
    - Selector type: entity
    - Domain filter: switch
    - Name: "Battery Charging Switch"
    - Description: "Switch entity to enable/disable battery charging"
  - [x] 5.4 Add battery_charging_power input
    - Selector type: entity
    - Domain filter: input_number
    - Name: "Charging Power Setting"
    - Description: "Input number entity for charger wattage (used to calculate charging duration)"
  - [x] 5.5 Ensure entity selection tests pass
    - Run ONLY the 3-4 tests written in 5.1
    - Verify domain filters work correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- All three entity inputs defined with correct domain filters
- Single entity selection only (no multi-select)
- The 3-4 entity selection tests pass

---

### Internal Configuration

#### Task Group 6: Macro Defaults and Documentation
**Dependencies:** Task Groups 2-5

- [x] 6.0 Complete internal configuration and documentation
  - [x] 6.1 Write 2-3 focused tests for internal defaults
    - Test that blueprint has comments documenting hardcoded macro parameters
    - Test that no inputs exist for advanced macro parameters (attr_today, attr_tomorrow, value_key, etc.)
  - [x] 6.2 Add internal documentation comments
    - Document hardcoded macro parameters in YAML comments:
      - attr_today: 'today'
      - attr_tomorrow: 'tomorrow'
      - value_key: 'total'
      - datetime_in_data: false
      - mode: 'is_now'
    - Document price estimation strategy (last 3 hours before 1pm)
  - [x] 6.3 Add prerequisite documentation comment
    - Document that cheapest-energy-hours macro is required
    - Reference installation via HACS or manual copy to custom_templates/
  - [x] 6.4 Ensure internal configuration tests pass
    - Run ONLY the 2-3 tests written in 6.1
    - Verify no advanced parameters are exposed to users
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- All hardcoded macro defaults documented in comments
- No advanced configuration inputs exposed
- Prerequisite (cheapest-energy-hours) documented
- The 2-3 internal configuration tests pass

---

### Validation and Testing

#### Task Group 7: Test Review and Integration Validation
**Dependencies:** Task Groups 1-6

- [x] 7.0 Review existing tests and validate complete schema
  - [x] 7.1 Review tests from Task Groups 1-6
    - Review the 2-4 tests from Task 1.1 (blueprint foundation)
    - Review the 2-4 tests from Task 2.1 (night schedule)
    - Review the 2-4 tests from Task 3.1 (day schedule)
    - Review the 2 tests from Task 4.1 (evening peak)
    - Review the 3-4 tests from Task 5.1 (entity selection)
    - Review the 2-3 tests from Task 6.1 (internal config)
    - Total existing tests: approximately 13-21 tests
  - [x] 7.2 Analyze test coverage gaps for this feature only
    - Identify gaps in schema completeness validation
    - Focus ONLY on blueprint configuration schema requirements
    - Do NOT assess entire application test coverage
  - [x] 7.3 Write up to 5 additional integration tests if needed
    - Test complete blueprint schema validates in Home Assistant
    - Test input dependencies work correctly (e.g., day schedule inputs only relevant when enabled)
    - Test that all required inputs are present and no optional inputs are missing required defaults
    - Do NOT write comprehensive coverage for all scenarios
  - [x] 7.4 Run feature-specific tests only
    - Run ONLY tests related to this spec's feature (tests from 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, and 7.3)
    - Expected total: approximately 18-26 tests maximum
    - Do NOT run the entire application test suite
    - Verify complete blueprint schema is valid

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 18-26 tests total)
- Complete blueprint schema validates without errors
- All inputs match spec requirements
- No more than 5 additional tests added when filling gaps
- Blueprint can be imported successfully into Home Assistant

---

## Execution Order

Recommended implementation sequence using Breadth-first Task Completion Approach (BTCA):

**Layer 1 - Foundation (Sequential)**
1. Blueprint Foundation (Task Group 1)

**Layer 2 - All Input Definitions (Parallel)**
2. Night Schedule Inputs (Task Group 2)
3. Day/Winter Schedule Inputs (Task Group 3)
4. Evening Peak Schedule Inputs (Task Group 4)
5. Entity Selection Inputs (Task Group 5)

**Layer 3 - Documentation and Validation (Sequential)**
6. Internal Configuration (Task Group 6)
7. Test Review and Integration Validation (Task Group 7)

---

## Reference Files

- **Target output file:** `/workspace/blueprints/automation/charge_cheapest.yaml`
- **Tibber sensor format reference:** `/workspace/ha-sensor-states.md`
- **Tech stack reference:** `/workspace/agent-os/product/tech-stack.md`
- **Spec document:** `/workspace/agent-os/specs/2026-01-07-blueprint-configuration-schema/spec.md`
- **Requirements document:** `/workspace/agent-os/specs/2026-01-07-blueprint-configuration-schema/planning/requirements.md`

---

## Input Schema Summary

| Input Name | Selector | Default | Notes |
|------------|----------|---------|-------|
| night_start_time | time | 23:00:00 | Night charging window start |
| night_end_time | time | 06:00:00 | Night charging window end (next day) |
| night_target_soc | number (0-100, step 5) | 60 | Must be reached; price only affects timing |
| day_schedule_enabled | boolean | false | Toggle for winter/day schedule |
| day_start_time | time | 09:00:00 | Day charging window start |
| day_end_time | time | 16:00:00 | Day charging window end |
| day_target_soc | number (0-100, step 5) | 50 | Independent from night target |
| evening_peak_start | time | 17:00:00 | Expensive period start (informational) |
| evening_peak_end | time | 21:00:00 | Expensive period end (informational) |
| price_sensor | entity (sensor) | - | Required; standard Tibber format |
| battery_charging_switch | entity (switch) | - | Required; controls charging on/off |
| battery_charging_power | entity (input_number) | - | Required; charger wattage setting |
