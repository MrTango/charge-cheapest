# Specification: HACS Easy Deployment Package

## Goal

Create a user-friendly HACS-compatible deployment package for the Charge Cheapest blueprint that enables intermediate Home Assistant users to set up complete battery charging automation with a comprehensive dashboard via minimal manual configuration steps.

## User Stories

- As an intermediate Home Assistant user, I want to install the Charge Cheapest system via HACS with minimal YAML editing so that I can start optimizing my energy costs quickly.
- As a user, I want a comprehensive Lovelace dashboard that shows charging status, price charts, statistics, and configuration options so that I can monitor and control my battery charging from one place.

## Specific Requirements

**HACS-Compatible Repository Structure**
- Create `hacs.json` manifest with `homeassistant` category and minimum HA version requirement
- Include `.github/workflows/hacs.yaml` for HACS validation workflow
- Create `info.md` for HACS store description with feature highlights and prerequisites
- Organize files in HACS-expected structure with `packages/` and `dashboards/` directories
- Include `README.md` with installation instructions and troubleshooting guide

**Package YAML Auto-Creation**
- Single package file `packages/cheapest_battery_charging/cheapest_battery_charging.yaml` creates all helpers on restart
- Package creates: input_number, input_boolean, input_select, input_datetime, input_text, template sensors, binary sensors, utility meters
- Use Home Assistant packages include pattern (`homeassistant.packages`)
- No manual entity creation required after package include and restart

**Entity Configuration via input_text Helpers**
- `input_text.charge_cheapest_price_sensor_id` stores the Tibber price sensor entity ID
- `input_text.charge_cheapest_soc_sensor_id` stores the battery SOC sensor entity ID
- `input_text.charge_cheapest_switch_id` stores the battery charging switch entity ID
- Template sensors use `states(states('input_text.xxx'))` pattern for dynamic entity resolution
- Dashboard Configuration tab provides UI fields for entering entity IDs without YAML editing

**Control Helpers Creation**
- `input_number.battery_charging_power` (500-15000W, step 100, slider mode)
- `input_number.user_soc_target` (0-100%, step 5, slider mode)
- `input_boolean.charge_cheapest_enabled` master enable toggle
- `input_boolean.charge_cheapest_force_now` for immediate charging override
- `input_boolean.charge_cheapest_skip_next` to skip next scheduled charge
- `input_select.charge_cheapest_mode` with options: Automatic, Solar Optimized, Manual, Disabled
- `input_datetime.charge_cheapest_manual_start` and `input_datetime.charge_cheapest_manual_end` for manual scheduling

**Solar Configuration Helpers**
- `input_number.solar_panel_azimuth` (0-360 degrees, step 1)
- `input_number.solar_panel_tilt` (0-90 degrees, step 1)
- `input_number.solar_peak_power_kwp` (0-50 kWp, step 0.1)
- `input_text.solar_forecast_storage` for persisting forecast results between automation runs

**Template Sensors for Dashboard Data**
- `sensor.charge_cheapest_status` with states: Idle, Scheduled, Charging, Disabled, Error
- `sensor.charge_cheapest_next_window` showing formatted start-end time range
- `sensor.charge_cheapest_recommended_soc` with solar forecast calculation result
- `sensor.charge_cheapest_current_price` reading current hour price from configured Tibber sensor
- `sensor.charge_cheapest_price_range` showing min-max price range for the day
- `sensor.charge_cheapest_savings_today` calculating savings vs average price

**Binary Sensors for Dashboard Status**
- `binary_sensor.charge_cheapest_is_charging` true when battery switch is on
- `binary_sensor.charge_cheapest_is_cheap_hour` true when current price is below daily average
- `binary_sensor.charge_cheapest_prices_available` true when Tibber has tomorrow data
- `binary_sensor.charge_cheapest_ready` true when all required entities are configured and responding

**Statistics and Utility Meters**
- `sensor.charge_cheapest_hours_today` counting hours charged today
- `sensor.charge_cheapest_count_today` counting charge sessions today
- `utility_meter.charge_cheapest_cost_daily` with daily reset cycle
- `utility_meter.charge_cheapest_cost_monthly` with monthly reset cycle

**Dashboard Overview Tab**
- Status card showing charging state, current SOC, next window, mode
- Battery gauge showing current SOC percentage with color thresholds
- Price chart using ApexCharts with today/tomorrow prices and highlighted cheap hours
- Control buttons for enable/disable, force charge, skip next, mode selection
- Native chart fallback using history-graph when ApexCharts unavailable

**Dashboard Statistics Tab**
- Savings summary card with daily, weekly, monthly totals
- History graphs for SOC, charging power, price trends
- Charging session count and total hours statistics
- Cost comparison showing actual vs theoretical grid-only cost

**Dashboard Configuration Tab**
- Entity ID input fields for Tibber sensor, battery SOC, battery switch
- Solar panel configuration inputs (azimuth, tilt, peak power)
- System info showing package version, last update, dependency status
- Validation indicators showing green checkmarks when entities are valid

**Lovelace Dashboard YAML**
- Single file `dashboards/charge_cheapest_dashboard.yaml` importable via Lovelace raw config editor
- Use conditional cards to show/hide ApexCharts vs native fallback based on custom card availability
- Follow Home Assistant card best practices with proper entity references
- Include card-mod styling for consistent visual appearance

**User Installation Steps (8-Step Process)**
- Step 1: Install cheapest-energy-hours macro via HACS (prerequisite)
- Step 2: Copy `packages/` folder to Home Assistant `config/packages/` directory
- Step 3: Add `homeassistant.packages` include to `configuration.yaml`
- Step 4: Restart Home Assistant to create all helpers
- Step 5: Import dashboard via Lovelace raw config editor
- Step 6: Navigate to Configuration tab and enter entity IDs
- Step 7: Import Charge Cheapest blueprint via GitHub URL
- Step 8: Create automation from blueprint selecting package-created helpers

## Visual Design

No visual assets provided.

## Existing Code to Leverage

**Blueprint entity patterns (`/workspace/blueprints/automation/cheapest_battery_charging.yaml`)**
- Replicate input selector patterns for consistency between package helpers and blueprint inputs
- Use same naming conventions (charge_cheapest_ prefix, snake_case)
- Reference variable calculation patterns for template sensors
- Follow notification patterns for dashboard status messages

**Solar forecast variables (`/workspace/blueprints/automation/cheapest_battery_charging.yaml` lines 657-766)**
- Copy `solar_forecast_kwh` template logic for `sensor.charge_cheapest_recommended_soc`
- Replicate `optimal_morning_soc` calculation formula in package template sensor
- Use same fallback patterns when forecast unavailable
- Reference `solar_forecast_attributes` structure for sensor attributes

**Price calculation patterns (`/workspace/blueprints/automation/cheapest_battery_charging.yaml` lines 467-543)**
- Use `cheapest_energy_hours` macro import pattern for template sensors
- Follow `tomorrow_prices_available` check pattern for `binary_sensor.charge_cheapest_prices_available`
- Replicate cost calculation patterns for savings sensors

**Duration calculation logic (`/workspace/blueprints/automation/cheapest_battery_charging.yaml` lines 801-825)**
- Use same 95% efficiency factor for energy calculations in template sensors
- Follow capacity unit conversion pattern (Wh to kWh detection)
- Apply same clamping and rounding approaches

**Charging trigger patterns (`/workspace/blueprints/automation/cheapest_battery_charging.yaml` lines 908-949)**
- Reference trigger ID patterns for dashboard automation suggestions
- Follow time-based trigger conventions for user documentation

## Out of Scope

- Custom HACS integration (this is a package-based solution, not a custom component)
- Automatic blueprint import (users must manually import the blueprint)
- Multi-language dashboard translations (English only)
- Mobile-specific dashboard layouts (responsive but not mobile-first)
- Historical data migration from existing installations
- Automated entity discovery (users must manually enter entity IDs)
- Integration with non-Tibber energy providers
- Real-time push notifications to mobile devices
- Energy arbitrage or grid export optimization
- EV charging integration or coordination
