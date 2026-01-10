# Specification: Home Assistant Integration Deployment

## Goal

Convert the existing "Charge Cheapest" blueprint and packages into a HACS-compatible custom integration with one-click installation, UI-based configuration, internal automation management, and auto-registered dashboard.

## User Stories

- As a Home Assistant user, I want to install the Charge Cheapest integration via HACS so that I can set up battery charging optimization without manually copying files
- As a user configuring the integration, I want a setup wizard that lets me select my battery and Tibber entities so that I can complete configuration without editing YAML files

## Specific Requirements

**HACS-Compatible Integration Structure**
- Create standard `custom_components/tibber_cheapest_charging/` directory structure
- Include `manifest.json` with HACS-required fields: domain, name, version, documentation, dependencies, codeowners, iot_class
- Set `iot_class` to `cloud_polling` (for Tibber price data) and list `tibber` as a dependency
- Include `hacs.json` at repository root with `content_in_root: false` pointing to custom_components path
- Minimum Home Assistant version: 2024.1.0 (aligns with existing hacs.json)
- Python 3.11+ compatibility required

**Config Flow Implementation**
- Implement `config_flow.py` with multi-step setup wizard using Home Assistant's config flow framework
- Step 1: Entity selection - battery SOC sensor (required), battery charging switch (required), Tibber price sensor (required)
- Step 2: Optional entities - solar forecast sensor, battery capacity sensor, charging power input_number
- Step 3: Schedule configuration - night schedule times, day schedule enable/times, evening peak times
- Use entity selectors with appropriate domain filtering (sensor, switch, input_number)
- Validate selected entities exist and are responsive before completing setup
- Store configuration in ConfigEntry for persistence across restarts

**YAML Configuration Support**
- Support identical configuration options via `configuration.yaml` under `tibber_cheapest_charging:` key
- Parse YAML config in `__init__.py` async_setup and create ConfigEntry programmatically
- No additional power-user options beyond config flow - maintain feature parity
- Document YAML schema in integration documentation

**Options Flow for Runtime Configuration**
- Implement `options_flow` in config_flow.py for post-setup adjustments
- Allow modifying SOC targets, schedule times, notification preferences, and solar forecast settings
- Include "Recreate Dashboard" button that triggers dashboard regeneration service
- Changes apply immediately without requiring restart

**Internal Automation Registration**
- Convert blueprint automation logic to Python-based event handlers in `coordinator.py`
- Register time-based triggers using Home Assistant's `async_track_time_change` helper
- Implement charging window calculation by calling external `cheapest-energy-hours` Jinja macro via `template.async_render_with_possible_json_value`
- Handle cross-midnight price fetching using Tibber's `today` and `tomorrow` price attributes
- Register automations internally - users should not see these in Automations UI

**Charging Logic Coordinator**
- Create `coordinator.py` with DataUpdateCoordinator pattern for centralized state management
- Implement SOC-based charging duration calculation with 95% efficiency factor
- Support failure behaviors: skip_charging, use_default_window, charge_immediately
- Calculate and schedule night charging, day charging, and emergency pre-peak charging windows
- Expose calculated values (next window, estimated cost, recommended SOC) as sensor attributes

**Dashboard Auto-Registration**
- On first setup, auto-register Lovelace dashboard using `lovelace.async_create_dashboard` or storage collection APIs
- Convert existing `dashboards/charge_cheapest.yaml` content to Python dict structure
- Dashboard becomes user-owned immediately - integration does not manage or update it after creation
- Implement `recreate_dashboard` service callable from options flow
- Include conditional cards that handle missing ApexCharts custom card gracefully

**Entity Platform Setup**
- Create `sensor.py` for template sensors: charging_status, current_price, next_window, recommended_soc, price_range, estimated_savings
- Create `binary_sensor.py` for: is_charging, is_cheap_hour, prices_available_tomorrow, system_ready
- Create `switch.py` or reuse user's existing charging switch entity (do not duplicate)
- All entities use `charge_cheapest_` prefix and register under integration's device

**External Dependency Handling**
- Document requirement for `cheapest-energy-hours` Jinja macro (TheFes/cheapest-energy-hours)
- Users must install this separately via HACS custom templates
- Validate macro availability at setup time; show clear error if missing
- Tibber integration is a hard dependency - fail setup if not configured

## Existing Code to Leverage

**`blueprints/automation/charge_cheapest.yaml`**
- Contains complete cheapest hours calculation using `cheapest_energy_hours.jinja` macro
- Cross-midnight window handling via `include_tomorrow=true` parameter
- SOC-based charging duration calculation with efficiency factor
- Three failure behavior modes already implemented
- Night, day, and emergency charging trigger logic to replicate

**`packages/cheapest_battery_charging/cheapest_battery_charging.yaml`**
- Input helper definitions (input_text, input_number, input_boolean, input_select, input_datetime)
- Template sensor definitions for dashboard data
- Binary sensor patterns for status indicators
- History stats and utility meter configurations to reference

**`dashboards/charge_cheapest.yaml`**
- Three-tab dashboard structure (Overview, Statistics, Configuration)
- ApexCharts price visualization with data_generator template
- Conditional cards pattern for handling unconfigured states
- Entity card groupings and markdown content blocks

**`hacs.json` at repository root**
- Existing HACS configuration with minimum HA version 2024.1.0
- Content structure preferences already defined

## Out of Scope

- Multi-battery support (future enhancement per roadmap item 11)
- Managed/auto-updating dashboard after initial creation
- Additional YAML-only power-user options beyond config flow options
- User-visible blueprint-based automations (internal only)
- Migration tooling from existing manual installations (fresh start approach)
- Bundling the `cheapest-energy-hours` Jinja macro (remains external dependency)
- Custom Lovelace cards (ApexCharts) - users install separately if desired
- Tibber integration setup - prerequisite users handle independently
- Mobile app or companion app integration
- Price threshold alerts or notifications beyond charging events
