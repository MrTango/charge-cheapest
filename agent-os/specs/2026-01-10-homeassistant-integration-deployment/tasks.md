# Task Breakdown: Home Assistant Integration Deployment

## Overview
Total Tasks: 9 Task Groups, ~70 Sub-tasks

This task breakdown covers converting the existing "Charge Cheapest" blueprint and packages into a HACS-compatible custom integration for Home Assistant with config flow, YAML configuration, internal automation, and auto-registered dashboard.

## Task List

### Integration Foundation

#### Task Group 1: Integration Scaffold and Structure
**Dependencies:** None

- [x] 1.0 Complete integration scaffold and basic structure
  - [x] 1.1 Write 3-5 focused tests for integration loading
    - Test `async_setup` loads successfully with valid config
    - Test `async_setup_entry` creates ConfigEntry correctly
    - Test `async_unload_entry` cleans up properly
    - Test integration fails gracefully when Tibber not configured
  - [x] 1.2 Create `custom_components/charge_cheapest/` directory structure
    - Create `__init__.py` with `async_setup` and `async_setup_entry` functions
    - Create `const.py` with domain, platforms, and configuration constants
    - Create empty `coordinator.py`, `config_flow.py`, `sensor.py`, `binary_sensor.py`
  - [x] 1.3 Create `manifest.json` with HACS-required fields
    - Set `domain` to `charge_cheapest`
    - Set `name` to `Charge Cheapest`
    - Set `version` to `1.0.0`
    - Set `iot_class` to `cloud_polling`
    - Add `tibber` to `dependencies` array
    - Set `codeowners` array
    - Set `requirements` (empty - no PyPI dependencies)
    - Set minimum Home Assistant version to `2024.1.0`
  - [x] 1.4 Update repository root `hacs.json`
    - Ensure `content_in_root: false` points to `custom_components/` path
    - Verify `homeassistant` minimum version matches manifest
  - [x] 1.5 Implement basic `__init__.py` structure
    - Import required Home Assistant helpers (`ConfigEntry`, `HomeAssistant`)
    - Define `PLATFORMS` list: `[Platform.SENSOR, Platform.BINARY_SENSOR]`
    - Implement `async_setup` for YAML configuration loading
    - Implement `async_setup_entry` for ConfigEntry initialization
    - Implement `async_unload_entry` for cleanup
    - Add Tibber integration dependency check at setup time
  - [x] 1.6 Create `const.py` with all configuration constants
    - Define `DOMAIN = "charge_cheapest"`
    - Define configuration keys matching blueprint inputs (entity IDs, schedule times, SOC targets)
    - Define default values for all optional configuration
    - Define notification preference keys
    - Define solar forecast configuration keys
  - [x] 1.7 Ensure integration scaffold tests pass
    - Run ONLY the 3-5 tests written in 1.1
    - Verify integration loads without errors in test environment

**Acceptance Criteria:**
- Integration directory structure follows Home Assistant conventions
- `manifest.json` passes HACS validation
- Basic loading/unloading works in test environment
- Tibber dependency is properly declared and validated

---

#### Task Group 2: Config Flow Implementation
**Dependencies:** Task Group 1

- [x] 2.0 Complete config flow with multi-step wizard
  - [x] 2.1 Write 4-6 focused tests for config flow
    - Test Step 1 entity selection validates required fields
    - Test Step 2 optional entity selection works with empty values
    - Test Step 3 schedule configuration accepts valid time ranges
    - Test entity validation rejects non-existent entities
    - Test flow creates ConfigEntry on completion
  - [x] 2.2 Create `config_flow.py` with `ConfigFlow` class
    - Inherit from `config_entries.ConfigFlow`
    - Set `VERSION = 1`
    - Set `DOMAIN` from `const.py`
    - Import Home Assistant selectors for entity picking
  - [x] 2.3 Implement Step 1: Required Entity Selection
    - Add `async_step_user` as entry point
    - Create form with entity selectors for:
      - `battery_soc_sensor` (sensor domain, required)
      - `battery_charging_switch` (switch domain, required)
      - `price_sensor` (sensor domain, required)
    - Use `selector.EntitySelector` with domain filtering
    - Validate entities exist and are not `unavailable`
    - Show error if validation fails; proceed to Step 2 on success
  - [x] 2.4 Implement Step 2: Optional Entity Selection
    - Create `async_step_optional_entities` method
    - Add entity selectors for:
      - `solar_forecast_sensor` (sensor domain, optional)
      - `battery_capacity_sensor` (sensor domain, optional)
      - `battery_charging_power` (input_number domain, optional)
    - Allow empty/None values for optional fields
    - Proceed to Step 3 on submit
  - [x] 2.5 Implement Step 3: Schedule Configuration
    - Create `async_step_schedule` method
    - Add time selectors for:
      - `night_start_time` (default: 23:00)
      - `night_end_time` (default: 06:00)
      - `day_schedule_enabled` (boolean, default: false)
      - `day_start_time` (default: 09:00)
      - `day_end_time` (default: 16:00)
      - `evening_peak_start` (default: 17:00)
      - `evening_peak_end` (default: 21:00)
    - Add SOC target number inputs:
      - `night_target_soc` (default: 60, range: 0-100)
      - `day_target_soc` (default: 50, range: 0-100)
      - `evening_peak_target_soc` (default: 50, range: 20-100)
    - Validate schedule times do not conflict
    - Create ConfigEntry on completion
  - [x] 2.6 Implement entity validation helper
    - Create `_validate_entity_exists` method
    - Check entity exists in Home Assistant state machine
    - Check entity is not in `unavailable` or `unknown` state
    - Return appropriate error keys for translation
  - [x] 2.7 Add translations for config flow
    - Create `translations/en.json` with config flow strings
    - Include step titles, field descriptions, error messages
    - Follow Home Assistant translation conventions
  - [x] 2.8 Ensure config flow tests pass
    - Run ONLY the 4-6 tests written in 2.1
    - Verify multi-step flow completes successfully

**Acceptance Criteria:**
- Config flow appears in Home Assistant integrations UI
- All three steps display correct selectors and validation
- Entity validation prevents setup with missing/unavailable entities
- ConfigEntry is created with all user selections stored

---

#### Task Group 3: YAML Configuration Support
**Dependencies:** Task Group 1, Task Group 2

- [x] 3.0 Complete YAML configuration parsing
  - [x] 3.1 Write 3-4 focused tests for YAML configuration
    - Test valid YAML config creates ConfigEntry
    - Test YAML config with missing required fields fails
    - Test YAML config coexists with config flow entries
  - [x] 3.2 Define YAML schema in `__init__.py`
    - Import `voluptuous` for schema validation
    - Create `CONFIG_SCHEMA` matching config flow options
    - Use `cv.entity_id` validators for entity fields
    - Use `cv.time_period` for schedule times
    - Use `cv.positive_int` for SOC targets with ranges
  - [x] 3.3 Implement `async_setup` for YAML loading
    - Check if `DOMAIN` key exists in `configuration.yaml`
    - Parse and validate YAML config against `CONFIG_SCHEMA`
    - Check if ConfigEntry already exists for this config (prevent duplicates)
    - Call `config_entries.async_create` to create entry from YAML
    - Store YAML source flag in ConfigEntry data for options flow
  - [x] 3.4 Document YAML configuration schema
    - Add inline comments in `__init__.py` showing YAML example
    - Create `services.yaml` if needed for service documentation
  - [x] 3.5 Ensure YAML configuration tests pass
    - Run ONLY the 3-4 tests written in 3.1
    - Verify YAML creates valid ConfigEntry

**Acceptance Criteria:**
- Users can configure integration via `configuration.yaml`
- YAML schema matches config flow options exactly
- Validation errors display meaningful messages
- YAML and config flow entries can coexist

---

### Charging Logic

#### Task Group 4: DataUpdateCoordinator and Charging Logic
**Dependencies:** Task Group 1, Task Group 2

- [x] 4.0 Complete coordinator with charging logic
  - [x] 4.1 Write 5-7 focused tests for coordinator
    - Test coordinator initializes with valid config
    - Test SOC-based charging duration calculation with 95% efficiency
    - Test cheapest hours calculation with cross-midnight window
    - Test failure behavior modes (skip, default_window, charge_immediately)
    - Test night/day/emergency charging schedule calculation
  - [x] 4.2 Create `coordinator.py` with `TibberCheapestChargingCoordinator`
    - Inherit from `DataUpdateCoordinator`
    - Set update interval (e.g., 5 minutes for price refresh)
    - Store ConfigEntry data as instance attributes
    - Initialize entity references from config
  - [x] 4.3 Implement SOC-based charging duration calculation
    - Port `calculated_charging_duration` logic from blueprint
    - Accept current SOC, target SOC, battery capacity, charging power
    - Apply 95% efficiency factor
    - Round to 15-minute slots (0.25 hour increments)
    - Return fallback duration if sensor values unavailable
  - [x] 4.4 Implement cheapest hours calculation
    - Create method to invoke `cheapest_energy_hours` Jinja macro
    - Use `template.async_render_with_possible_json_value` for macro execution
    - Handle cross-midnight windows via `include_tomorrow=true`
    - Return start time, end time, and estimated cost
    - Handle macro unavailability gracefully
  - [x] 4.5 Implement `_async_update_data` method
    - Fetch current price from Tibber sensor
    - Check tomorrow prices availability
    - Calculate next charging window (night, day, or emergency)
    - Update coordinator data dict with calculated values
    - Handle update errors with proper exception types
  - [x] 4.6 Implement failure behavior handling
    - Create `_handle_price_unavailable` method
    - Implement `skip_charging`: Log and return empty schedule
    - Implement `use_default_window`: Return default times from config
    - Implement `charge_immediately`: Return current time + duration
  - [x] 4.7 Implement internal automation registration
    - Use `async_track_time_change` for trigger_time scheduling
    - Register night charging trigger at configured time
    - Register day charging trigger when day_schedule_enabled
    - Register evening peak check trigger (1 hour before peak)
    - Store callback unsubscribe functions for cleanup
  - [x] 4.8 Implement charging switch control methods
    - Create `async_start_charging` method
    - Create `async_stop_charging` method
    - Use `hass.services.async_call` for switch control
    - Log charging actions for debugging
  - [x] 4.9 Implement solar forecast integration (optional feature)
    - Port `optimal_morning_soc` calculation from blueprint
    - Read solar forecast from configured sensor
    - Calculate SOC reduction based on expected solar production
    - Clamp result between `minimum_soc_floor` and `night_target_soc`
  - [x] 4.10 Ensure coordinator tests pass
    - Run ONLY the 5-7 tests written in 4.1
    - Verify charging calculations match blueprint behavior

**Acceptance Criteria:**
- Coordinator calculates charging windows correctly
- Cross-midnight windows work with Tibber today/tomorrow attributes
- SOC-based duration matches blueprint calculations
- Failure behaviors work as specified
- Internal automations register without appearing in Automations UI

---

### Entity Platforms

#### Task Group 5: Sensor and Binary Sensor Platforms
**Dependencies:** Task Group 4

- [x] 5.0 Complete entity platform implementations
  - [x] 5.1 Write 4-6 focused tests for entities
    - Test sensors report correct values from coordinator
    - Test binary sensors reflect charging state correctly
    - Test entities have correct device class and unit of measurement
    - Test entities update when coordinator refreshes
  - [x] 5.2 Create `sensor.py` with sensor entities
    - Create `TibberCheapestChargingSensor` base class
    - Inherit from `CoordinatorEntity` and `SensorEntity`
    - Implement sensors from package template sensors:
      - `charging_status`: States: Idle, Scheduled, Charging, Disabled, Error
      - `current_price`: Current electricity price from Tibber
      - `next_window`: Formatted next charging window time range
      - `recommended_soc`: Calculated optimal SOC target
      - `price_range`: Today's min-max price range
      - `estimated_savings`: Potential savings vs average price
    - Set appropriate `device_class`, `native_unit_of_measurement`, `icon`
    - Use `charge_cheapest_` entity ID prefix
  - [x] 5.3 Create `binary_sensor.py` with binary sensor entities
    - Create `TibberCheapestChargingBinarySensor` base class
    - Inherit from `CoordinatorEntity` and `BinarySensorEntity`
    - Implement binary sensors:
      - `is_charging`: True when charging switch is on
      - `is_cheap_hour`: True when current price below daily average
      - `prices_available_tomorrow`: True when tomorrow's prices exist
      - `system_ready`: True when all required entities configured and available
    - Set appropriate `device_class` (battery_charging, connectivity)
  - [x] 5.4 Register entities under integration device
    - Create device info in coordinator
    - Set `identifiers` using domain and entry_id
    - Set `name`, `manufacturer`, `model` for device registry
    - All sensors and binary sensors reference this device
  - [x] 5.5 Implement `async_setup_entry` for each platform
    - Create entity instances from coordinator data
    - Add entities via `async_add_entities`
    - Handle platform setup errors gracefully
  - [x] 5.6 Add entity descriptions with translations
    - Create sensor descriptions with `SensorEntityDescription`
    - Create binary sensor descriptions with `BinarySensorEntityDescription`
    - Add translations for entity names in `translations/en.json`
  - [x] 5.7 Ensure entity platform tests pass
    - Run ONLY the 4-6 tests written in 5.1
    - Verify entities appear in Home Assistant

**Acceptance Criteria:**
- All sensors display correct values in HA UI
- Binary sensors reflect correct on/off states
- Entities are grouped under integration device
- Entity IDs use `charge_cheapest_` prefix consistently

---

### Dashboard and Options Flow

#### Task Group 6: Dashboard Auto-Registration
**Dependencies:** Task Group 5

- [x] 6.0 Complete dashboard auto-registration
  - [x] 6.1 Write 2-4 focused tests for dashboard registration
    - Test dashboard is created on first setup
    - Test dashboard is not recreated on reload
    - Test `recreate_dashboard` service works
  - [x] 6.2 Convert `dashboards/charge_cheapest.yaml` to Python dict
    - Create `dashboard.py` module
    - Define `DASHBOARD_CONFIG` dict matching YAML structure
    - Include all three views: Overview, Statistics, Configuration
    - Preserve ApexCharts conditional cards
    - Include fallback history-graph for non-ApexCharts users
  - [x] 6.3 Implement dashboard creation in `async_setup_entry`
    - Check if dashboard already exists (by URL path)
    - Use `lovelace.async_create_dashboard` or storage collection API
    - Set dashboard URL path to `charge-cheapest`
    - Mark dashboard as `mode: storage` (user-owned)
    - Set `show_in_sidebar: true`
  - [x] 6.4 Implement `recreate_dashboard` service
    - Register service in `async_setup_entry`
    - Delete existing dashboard if present
    - Create fresh dashboard from `DASHBOARD_CONFIG`
    - Handle errors gracefully with notifications
  - [x] 6.5 Handle ApexCharts unavailability
    - Use conditional cards in dashboard config
    - Show history-graph fallback when ApexCharts not installed
    - Add markdown card explaining how to install ApexCharts
  - [x] 6.6 Ensure dashboard tests pass
    - Run ONLY the 2-4 tests written in 6.1
    - Verify dashboard appears in Home Assistant

**Acceptance Criteria:**
- Dashboard is auto-created on first integration setup
- Dashboard appears in sidebar after setup
- Users can freely edit the dashboard
- `recreate_dashboard` service restores default dashboard

---

#### Task Group 7: Options Flow Implementation
**Dependencies:** Task Group 6

- [x] 7.0 Complete options flow for runtime configuration
  - [x] 7.1 Write 3-4 focused tests for options flow
    - Test options flow opens from integration settings
    - Test changes are saved to ConfigEntry
    - Test "Recreate Dashboard" button triggers service
  - [x] 7.2 Add `OptionsFlow` class to `config_flow.py`
    - Create `TibberCheapestChargingOptionsFlow` class
    - Inherit from `config_entries.OptionsFlow`
    - Reference from `ConfigFlow.async_get_options_flow`
  - [x] 7.3 Implement options form
    - Display current values from ConfigEntry options
    - Allow modification of:
      - SOC targets (night, day, evening peak)
      - Schedule times (all schedule configuration)
      - Notification preferences (all notification toggles)
      - Solar forecast settings (enabled, automatic mode, offsets)
    - Use same selectors as config flow for consistency
  - [x] 7.4 Implement "Recreate Dashboard" button
    - Add submit button that triggers dashboard recreation
    - Call `recreate_dashboard` service when pressed
    - Show confirmation notification on success
  - [x] 7.5 Handle options update
    - Merge new options with existing ConfigEntry
    - Trigger coordinator reload on options change
    - No restart required - changes apply immediately
  - [x] 7.6 Add translations for options flow
    - Update `translations/en.json` with options strings
    - Include descriptions for all modifiable settings
  - [x] 7.7 Ensure options flow tests pass
    - Run ONLY the 3-4 tests written in 7.1
    - Verify options changes take effect

**Acceptance Criteria:**
- Options flow accessible from integration settings
- All modifiable settings displayed with current values
- Changes apply without restart
- "Recreate Dashboard" button works correctly

---

### HACS and Documentation

#### Task Group 8: HACS Compatibility and Documentation
**Dependencies:** Task Groups 1-7

- [x] 8.0 Complete HACS compatibility and documentation
  - [x] 8.1 Write 2-3 focused tests for HACS validation
    - Test `manifest.json` has all required fields
    - Test `hacs.json` points to correct content path
    - Test integration version format is valid
  - [x] 8.2 Validate and update `manifest.json`
    - Ensure all HACS-required fields present
    - Add `issue_tracker` URL
    - Add `documentation` URL
    - Verify `dependencies` includes `tibber`
  - [x] 8.3 Update repository `hacs.json`
    - Set `country` if applicable
    - Ensure `render_readme: true`
    - Verify minimum HA version consistency
  - [x] 8.4 Create/update README.md with installation instructions
    - Add HACS installation steps
    - Add manual installation steps
    - Document prerequisites (Tibber integration, cheapest-energy-hours macro)
    - Include configuration examples (both UI and YAML)
    - Add troubleshooting section
  - [x] 8.5 Document external dependency requirements
    - Clearly state `cheapest-energy-hours` Jinja macro requirement
    - Provide installation link for TheFes/cheapest-energy-hours
    - Explain that Tibber integration must be configured first
    - Document ApexCharts as optional for price visualization
  - [x] 8.6 Add dependency validation at setup
    - Check for Tibber integration presence
    - Check for `cheapest_energy_hours.jinja` macro availability
    - Show clear error messages if dependencies missing
    - Block setup if hard dependencies not met
  - [x] 8.7 Ensure HACS validation tests pass
    - Run ONLY the 2-3 tests written in 8.1
    - Validate against HACS action if available

**Acceptance Criteria:**
- Integration passes HACS validation action
- README provides clear installation and setup instructions
- Dependency requirements clearly documented
- Setup fails gracefully with helpful messages if dependencies missing

---

### Testing

#### Task Group 9: Test Review and Gap Analysis
**Dependencies:** Task Groups 1-8

- [x] 9.0 Review existing tests and fill critical gaps
  - [x] 9.1 Review tests from Task Groups 1-8
    - Review integration loading tests (Task 1.1)
    - Review config flow tests (Task 2.1)
    - Review YAML configuration tests (Task 3.1)
    - Review coordinator tests (Task 4.1)
    - Review entity platform tests (Task 5.1)
    - Review dashboard tests (Task 6.1)
    - Review options flow tests (Task 7.1)
    - Review HACS validation tests (Task 8.1)
    - Total existing tests: approximately 24-38 tests
  - [x] 9.2 Analyze test coverage gaps for this feature
    - Identify critical end-to-end workflows lacking coverage
    - Focus on integration between coordinator and entities
    - Check charging window calculation edge cases
    - Verify cross-midnight price handling coverage
    - Assess failure behavior mode coverage
  - [x] 9.3 Write up to 10 additional strategic tests
    - Add integration test: Full setup flow to charging activation
    - Add test: Cross-midnight window calculation accuracy
    - Add test: SOC calculation matches blueprint output
    - Add test: Options flow changes trigger coordinator update
    - Add test: Dashboard service registration and execution
    - Add test: Entity state updates on coordinator refresh
    - Add test: Graceful handling of Tibber unavailability
    - Add remaining tests based on gap analysis (max 3 more)
  - [x] 9.4 Configure pytest for Home Assistant testing
    - Set up `pytest-homeassistant-custom-component` if needed
    - Create `conftest.py` with common fixtures
    - Add mock fixtures for Tibber integration
    - Add mock fixtures for cheapest-energy-hours macro
  - [x] 9.5 Run feature-specific tests only
    - Run ONLY tests related to this integration
    - Expected total: approximately 34-48 tests maximum
    - Verify all critical workflows pass
    - Do NOT run unrelated Home Assistant tests

**Acceptance Criteria:**
- All feature-specific tests pass (34-48 tests total)
- Critical user workflows are covered
- No more than 10 additional tests added
- Tests mock external dependencies appropriately

---

## Execution Order

Recommended implementation sequence:

1. **Task Group 1: Integration Scaffold** - Foundation for all other work
2. **Task Group 2: Config Flow** - User-facing setup wizard
3. **Task Group 3: YAML Configuration** - Power user support
4. **Task Group 4: Coordinator and Charging Logic** - Core functionality
5. **Task Group 5: Entity Platforms** - Expose data to Home Assistant
6. **Task Group 6: Dashboard Auto-Registration** - User interface
7. **Task Group 7: Options Flow** - Runtime configuration
8. **Task Group 8: HACS Compatibility** - Distribution readiness
9. **Task Group 9: Test Review** - Quality assurance

## Key Files Reference

**Existing Code to Port:**
- `/workspace/blueprints/automation/charge_cheapest.yaml` - Core charging logic and Jinja templates
- `/workspace/packages/cheapest_battery_charging/cheapest_battery_charging.yaml` - Helper definitions and template sensors
- `/workspace/dashboards/charge_cheapest.yaml` - Dashboard structure

**Integration Output Structure:**
```
custom_components/charge_cheapest/
  __init__.py          # Integration setup
  manifest.json        # HACS metadata
  config_flow.py       # Config and options flows
  coordinator.py       # DataUpdateCoordinator with charging logic
  const.py             # Constants and defaults
  sensor.py            # Sensor platform
  binary_sensor.py     # Binary sensor platform
  dashboard.py         # Dashboard configuration dict
  services.yaml        # Service definitions
  translations/
    en.json            # English translations
```

**Repository Files:**
- `/workspace/hacs.json` - HACS repository configuration
- `README.md` - Installation and usage documentation

## Notes

- **External Dependency**: The `cheapest-energy-hours` Jinja macro (TheFes/cheapest-energy-hours) must be installed separately by users. The integration validates its presence at setup.
- **Tibber Requirement**: Tibber integration is a hard dependency. Setup fails if Tibber is not configured.
- **Dashboard Ownership**: Dashboard is user-owned after creation. Integration does not auto-update it.
- **No Multi-Battery**: Multi-battery support is out of scope per roadmap (future enhancement).
- **Python 3.11+**: Required for Home Assistant 2024.1.0 compatibility.
