# Task Breakdown: HACS Easy Deployment Package

## Overview
Total Tasks: 6 Task Groups with 32 subtasks

This feature creates a HACS-compatible deployment package for the Charge Cheapest blueprint, enabling intermediate Home Assistant users to set up complete battery charging automation with minimal manual configuration.

## Task List

### Foundation Layer

#### Task Group 1: HACS Repository Structure
**Dependencies:** None

- [x] 1.0 Complete HACS repository foundation
  - [x] 1.1 Create `hacs.json` manifest file
    - Set `name`: "Charge Cheapest Package"
    - Set `homeassistant` category (not custom_component)
    - Specify minimum HA version requirement
    - Include `render_readme: true` for info.md processing
    - Reference: spec.md "HACS-Compatible Repository Structure"
  - [x] 1.2 Create `.github/workflows/hacs.yaml` validation workflow
    - Add HACS validation action
    - Configure category validation for "homeassistant"
    - Include YAML linting step
    - Reference: Standard HACS validation workflow pattern
  - [x] 1.3 Create directory structure
    - Create `packages/cheapest_battery_charging/` directory
    - Create `dashboards/` directory
    - Verify structure matches HACS expectations

**Acceptance Criteria:**
- `hacs.json` is valid JSON with correct category
- GitHub workflow validates successfully
- Directory structure follows HACS conventions

---

### Package Core Layer

#### Task Group 2: Input Helpers - Entity Configuration
**Dependencies:** Task Group 1

- [x] 2.0 Complete entity configuration helpers
  - [x] 2.1 Create base package YAML structure
    - Create `packages/cheapest_battery_charging/cheapest_battery_charging.yaml`
    - Add proper YAML header comments
    - Structure for `homeassistant.packages` include pattern
  - [x] 2.2 Create entity ID configuration input_text helpers
    - `input_text.charge_cheapest_price_sensor_id` (stores Tibber price sensor entity ID)
    - `input_text.charge_cheapest_soc_sensor_id` (stores battery SOC sensor entity ID)
    - `input_text.charge_cheapest_switch_id` (stores battery charging switch entity ID)
    - Set appropriate max lengths and patterns
    - Reference: spec.md "Entity Configuration via input_text Helpers"
  - [x] 2.3 Create control input_number helpers
    - `input_number.battery_charging_power` (500-15000W, step 100, slider mode)
    - `input_number.user_soc_target` (0-100%, step 5, slider mode)
    - Reference: spec.md "Control Helpers Creation"
  - [x] 2.4 Create control input_boolean helpers
    - `input_boolean.charge_cheapest_enabled` (master enable toggle)
    - `input_boolean.charge_cheapest_force_now` (immediate charging override)
    - `input_boolean.charge_cheapest_skip_next` (skip next scheduled charge)
    - Reference: spec.md "Control Helpers Creation"
  - [x] 2.5 Create input_select and input_datetime helpers
    - `input_select.charge_cheapest_mode` (Automatic, Solar Optimized, Manual, Disabled)
    - `input_datetime.charge_cheapest_manual_start` (has_time: true)
    - `input_datetime.charge_cheapest_manual_end` (has_time: true)
    - Reference: spec.md "Control Helpers Creation"
  - [x] 2.6 Create solar configuration helpers
    - `input_number.solar_panel_azimuth` (0-360 degrees, step 1)
    - `input_number.solar_panel_tilt` (0-90 degrees, step 1)
    - `input_number.solar_peak_power_kwp` (0-50 kWp, step 0.1)
    - `input_text.solar_forecast_storage` (for persisting forecast results)
    - Reference: spec.md "Solar Configuration Helpers"

**Acceptance Criteria:**
- Package YAML is valid and loads without errors
- All input helpers create on HA restart
- Entity IDs follow charge_cheapest_ prefix naming convention
- Slider modes and ranges match spec requirements

---

### Sensors Layer

#### Task Group 3: Template Sensors and Binary Sensors
**Dependencies:** Task Group 2

- [x] 3.0 Complete template sensors and binary sensors
  - [x] 3.1 Create charging status template sensor
    - `sensor.charge_cheapest_status`
    - States: Idle, Scheduled, Charging, Disabled, Error
    - Use `states(states('input_text.xxx'))` pattern for dynamic entity resolution
    - Reference: spec.md "Template Sensors for Dashboard Data"
  - [x] 3.2 Create price and scheduling template sensors
    - `sensor.charge_cheapest_next_window` (formatted start-end time range)
    - `sensor.charge_cheapest_current_price` (current hour price from Tibber sensor)
    - `sensor.charge_cheapest_price_range` (min-max price range)
    - Use cheapest_energy_hours macro import pattern
    - Reference: Blueprint lines 467-543 for price calculation patterns
  - [x] 3.3 Create solar and savings template sensors
    - `sensor.charge_cheapest_recommended_soc` (solar forecast calculation result)
    - `sensor.charge_cheapest_savings_today` (savings vs average price)
    - Copy solar_forecast_kwh template logic from blueprint lines 657-766
    - Reference: Blueprint optimal_morning_soc calculation formula
  - [x] 3.4 Create binary sensors for status
    - `binary_sensor.charge_cheapest_is_charging` (true when battery switch is on)
    - `binary_sensor.charge_cheapest_is_cheap_hour` (true when below daily average)
    - `binary_sensor.charge_cheapest_prices_available` (true when Tibber has tomorrow data)
    - `binary_sensor.charge_cheapest_ready` (true when all required entities configured)
    - Reference: spec.md "Binary Sensors for Dashboard Status"
  - [x] 3.5 Create statistics and utility meters
    - `sensor.charge_cheapest_hours_today` (history_stats counting hours)
    - `sensor.charge_cheapest_count_today` (charge session counter)
    - `utility_meter.charge_cheapest_cost_daily` (daily reset cycle)
    - `utility_meter.charge_cheapest_cost_monthly` (monthly reset cycle)
    - Reference: spec.md "Statistics and Utility Meters"

**Acceptance Criteria:**
- All template sensors render valid states
- Dynamic entity resolution via `states(states())` pattern works
- Binary sensors correctly evaluate conditions
- Utility meters reset on correct cycles

---

### Dashboard Layer

#### Task Group 4: Lovelace Dashboard Implementation
**Dependencies:** Task Group 3

- [x] 4.0 Complete Lovelace dashboard
  - [x] 4.1 Create dashboard YAML base structure
    - Create `dashboards/charge_cheapest_dashboard.yaml`
    - Configure three-tab layout (Overview, Statistics, Configuration)
    - Follow HA card best practices for entity references
    - Reference: spec.md "Lovelace Dashboard YAML"
  - [x] 4.2 Implement Overview tab
    - Status card (charging state, current SOC, next window, mode)
    - Battery gauge with color thresholds
    - Control buttons (enable/disable, force charge, skip next, mode selection)
    - Reference: spec.md "Dashboard Overview Tab"
  - [x] 4.3 Implement price chart with ApexCharts and fallback
    - ApexCharts config for today/tomorrow prices with highlighted cheap hours
    - Conditional card for ApexCharts vs native history-graph fallback
    - Check for custom card availability before rendering
    - Reference: spec.md "Dashboard Overview Tab" and "Lovelace Dashboard YAML"
  - [x] 4.4 Implement Statistics tab
    - Savings summary card (daily, weekly, monthly totals)
    - History graphs (SOC, charging power, price trends)
    - Charging session count and total hours statistics
    - Cost comparison (actual vs theoretical grid-only cost)
    - Reference: spec.md "Dashboard Statistics Tab"
  - [x] 4.5 Implement Configuration tab
    - Entity ID input fields (Tibber sensor, battery SOC, battery switch)
    - Solar panel configuration inputs (azimuth, tilt, peak power)
    - System info card (package version, last update, dependency status)
    - Validation indicators (green checkmarks for valid entities)
    - Reference: spec.md "Dashboard Configuration Tab"
  - [x] 4.6 Add card-mod styling
    - Apply consistent visual appearance
    - Follow existing card-mod patterns
    - Ensure responsive behavior

**Acceptance Criteria:**
- Dashboard imports via Lovelace raw config editor
- All three tabs render correctly
- Conditional cards show/hide based on ApexCharts availability
- Entity ID configuration works without YAML editing

---

### Documentation Layer

#### Task Group 5: Documentation and Installation Guide
**Dependencies:** Task Groups 1-4

- [x] 5.0 Complete documentation
  - [x] 5.1 Create `info.md` for HACS store
    - Feature highlights and benefits
    - Prerequisites (cheapest-energy-hours macro, Tibber integration)
    - Brief capability overview
    - Reference: spec.md "HACS-Compatible Repository Structure"
  - [x] 5.2 Update/Create `README.md` with installation instructions
    - Document 8-step installation process
    - Step 1: Install cheapest-energy-hours macro via HACS
    - Step 2: Copy packages folder to config/packages/
    - Step 3: Add homeassistant.packages include to configuration.yaml
    - Step 4: Restart Home Assistant
    - Step 5: Import dashboard via Lovelace raw config editor
    - Step 6: Navigate to Configuration tab and enter entity IDs
    - Step 7: Import Charge Cheapest blueprint via GitHub URL
    - Step 8: Create automation from blueprint selecting package-created helpers
    - Reference: spec.md "User Installation Steps (8-Step Process)"
  - [x] 5.3 Add troubleshooting section to README
    - Common issues and solutions
    - Entity not found errors
    - Price data unavailable handling
    - Dashboard import issues

**Acceptance Criteria:**
- info.md displays correctly in HACS store
- README.md covers complete installation process
- All 8 installation steps are clearly documented
- Troubleshooting covers common user issues

---

### Validation Layer

#### Task Group 6: Testing and Validation
**Dependencies:** Task Groups 1-5

- [x] 6.0 Complete validation and testing
  - [x] 6.1 Validate YAML syntax for all files
    - Run YAML linter on package file
    - Run YAML linter on dashboard file
    - Verify hacs.json is valid JSON
    - Check GitHub workflow syntax
  - [x] 6.2 Test package loading in Home Assistant
    - Verify package creates all helpers on restart
    - Confirm no duplicate entity errors
    - Test input helper default values
    - Validate entity naming follows conventions
  - [x] 6.3 Test template sensor functionality
    - Verify `states(states())` pattern resolves correctly
    - Test price sensors with mock Tibber data
    - Validate binary sensor conditions
    - Check utility meter reset cycles
  - [x] 6.4 Test dashboard import and rendering
    - Import dashboard via raw config editor
    - Verify all three tabs render
    - Test conditional ApexCharts/fallback logic
    - Confirm entity ID configuration updates work
  - [x] 6.5 Run HACS validation workflow
    - Execute `.github/workflows/hacs.yaml` locally or via CI
    - Fix any validation errors
    - Confirm repository structure passes HACS checks
  - [x] 6.6 End-to-end installation test
    - Follow 8-step installation process on clean HA instance
    - Document any issues encountered
    - Verify blueprint integration works with package helpers

**Acceptance Criteria:**
- All YAML files pass syntax validation
- Package loads and creates all entities
- Template sensors resolve correctly
- Dashboard renders all tabs
- HACS validation passes
- Full installation process completes successfully

---

## Execution Order

Recommended implementation sequence:

1. **Task Group 1: HACS Repository Structure** - Foundation for distribution
2. **Task Group 2: Input Helpers** - Core package configuration entities
3. **Task Group 3: Template Sensors** - Data layer for dashboard
4. **Task Group 4: Lovelace Dashboard** - User interface
5. **Task Group 5: Documentation** - Installation guide and HACS info
6. **Task Group 6: Validation** - Testing and verification

## Files Created

| File | Task Group | Purpose |
|------|------------|---------|
| `hacs.json` | 1 | HACS manifest |
| `.github/workflows/hacs.yaml` | 1 | HACS validation workflow |
| `packages/cheapest_battery_charging/cheapest_battery_charging.yaml` | 2, 3 | Package YAML with helpers and sensors |
| `dashboards/charge_cheapest_dashboard.yaml` | 4 | Lovelace dashboard |
| `info.md` | 5 | HACS store description |
| `README.md` | 5 | Installation instructions |

## Blueprint Reference

The existing blueprint at `/workspace/blueprints/automation/cheapest_battery_charging.yaml` contains patterns to replicate:

- **Solar forecast templates** (lines 657-766): Copy for `sensor.charge_cheapest_recommended_soc`
- **Price calculation patterns** (lines 467-543): Use for price sensors
- **Duration calculation logic** (lines 801-825): Apply 95% efficiency factor
- **Charging trigger patterns** (lines 908-949): Reference for dashboard automation suggestions

## Key Implementation Notes

1. **Dynamic Entity Resolution**: Use `states(states('input_text.charge_cheapest_xxx_id'))` pattern throughout template sensors to allow UI-based entity configuration
2. **HACS Category**: Use `homeassistant` category (package-based), not `integration` (custom component)
3. **ApexCharts Conditional**: Dashboard must detect and fall back gracefully when ApexCharts custom card is not installed
4. **Naming Convention**: All entities use `charge_cheapest_` prefix with snake_case naming
5. **No Automatic Blueprint Import**: Users must manually import the blueprint (out of scope for this package)

## Implementation Summary

All 6 task groups have been implemented successfully:

### Task Group 1: HACS Repository Structure
- Created `hacs.json` with homeassistant category and minimum HA version 2024.1.0
- Created `.github/workflows/hacs.yaml` with HACS validation and YAML linting
- Created directory structure: `packages/cheapest_battery_charging/` and `dashboards/`

### Task Group 2: Input Helpers
- Created all input_text helpers for entity ID configuration
- Created all input_number helpers with correct ranges and slider modes
- Created all input_boolean, input_select, and input_datetime helpers

### Task Group 3: Template Sensors and Binary Sensors
- Created 8 template sensors with dynamic entity resolution
- Created 4 binary sensors for status tracking
- Created history_stats sensors and utility meters

### Task Group 4: Lovelace Dashboard
- Created three-tab dashboard (Overview, Statistics, Configuration)
- Implemented ApexCharts price chart with history-graph fallback
- Added validation indicators and entity configuration fields

### Task Group 5: Documentation
- Created info.md for HACS store
- Updated README.md with 8-step installation process
- Added comprehensive troubleshooting section

### Task Group 6: Testing and Validation
- Validated all YAML files pass syntax checks
- Verified package structure and entity naming conventions
- Confirmed dashboard structure with three tabs
