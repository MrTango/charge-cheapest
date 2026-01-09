# Specification: Blueprint Configuration Schema

## Goal

Define the complete input configuration schema for the Charge Cheapest blueprint, enabling users to configure night/day charging schedules, SOC targets, Tibber price sensor, and battery control entities through Home Assistant's native blueprint UI.

## User Stories

- As a homeowner with battery storage, I want to configure my charging schedule times and SOC targets so that my battery charges during the cheapest hours while meeting my energy needs.
- As a Home Assistant user, I want to select my existing Tibber sensor and battery control entities so that the blueprint integrates seamlessly with my current setup.

## Specific Requirements

**Night Schedule Configuration Inputs**
- Time selector for schedule start time (default: 23:00, 24-hour format)
- Time selector for schedule end time (default: 06:00, 24-hour format)
- Number slider for target SOC percentage (range: 0-100%, default: 60%, step: 5)
- Target SOC is mandatory goal; price optimization only determines WHEN charging occurs within the window
- Schedule spans overnight (end time is next calendar day)

**Day/Winter Schedule Configuration Inputs**
- Boolean toggle to enable/disable day schedule (default: off)
- Time selector for schedule start time (default: 09:00, 24-hour format)
- Time selector for schedule end time (default: 16:00, 24-hour format)
- Number slider for day schedule target SOC (range: 0-100%, default: 50%, step: 5, independent from night target)
- Day schedule is optional and designed for winter months when solar production is insufficient

**Evening Peak Schedule Configuration Inputs**
- Time selector for evening peak start time (default: 17:00, 24-hour format)
- Time selector for evening peak end time (default: 21:00, 24-hour format)
- Evening peak times define the expensive period that day charging aims to cover
- Used internally for SOC calculations (not a charging window itself)

**Tibber Price Sensor Configuration**
- Entity selector with domain filter for `sensor`
- Single entity selection (no multi-select)
- User responsible for ensuring sensor provides `today` and `tomorrow` attributes with `total` price values
- No advanced attribute configuration exposed; blueprint uses standard Tibber format internally
- Users with non-standard setups must create template sensor to match expected format

**Battery Control Entity Configuration**
- Entity selector for charging switch with domain filter for `switch`
- Entity selector for charging power with domain filter for `input_number`
- Charging power entity represents charger wattage setting used to calculate required charging duration
- Both entities required for the blueprint to function

**Internal cheapest-energy-hours Macro Defaults**
- `attr_today`: 'today' (hardcoded, not exposed)
- `attr_tomorrow`: 'tomorrow' (hardcoded, not exposed)
- `value_key`: 'total' (hardcoded, not exposed)
- `datetime_in_data`: false (hardcoded, not exposed)
- `mode`: 'is_now' for automation triggers (hardcoded, not exposed)
- All macro parameters use sensible defaults; no advanced configuration exposed to users

**Price Estimation for Missing Hours**
- When tomorrow's prices unavailable (before ~13:00), blueprint estimates future hours
- Estimation strategy: repeat the prices from the last 3 hours before 1pm for unknown future hours
- Enables charging decisions for schedules that span or occur before price data arrives
- Estimation logic is internal; no user configuration required

## Visual Design

No visual mockups provided.

## Existing Code to Leverage

**Tibber Sensor Data Format (`/workspace/ha-sensor-states.md`)**
- Documents the expected attribute structure: `today` and `tomorrow` arrays containing objects with `total` key
- Price values in EUR/kWh format
- Blueprint schema must align with this documented format for standard Tibber integration compatibility

**cheapest-energy-hours Jinja Macro (TheFes/cheapest-energy-hours)**
- External dependency providing the core cheapest hour calculation logic
- Blueprint passes configured time windows and calculated hours to macro
- Must be installed via HACS or manual copy to `custom_templates/`
- Blueprint documentation should list this as a prerequisite

**Home Assistant Blueprint Input Selector Types**
- Use `time` selector for all schedule time inputs (native 24-hour time picker)
- Use `number` selector with min/max/step for SOC percentages (renders as slider)
- Use `boolean` selector for day schedule toggle
- Use `entity` selector with domain filter for sensor/switch/input_number selections

**Tech Stack Blueprint Structure (`/workspace/agent-os/product/tech-stack.md`)**
- Documents the target file location: `blueprints/automation/charge_cheapest.yaml`
- Confirms YAML + Jinja2 as the implementation approach
- Provides macro usage example to follow for cheapest-energy-hours integration

## Out of Scope

- Multi-battery support (deferred to roadmap item 10)
- Solar forecast integration and dynamic SOC adjustment (deferred to roadmap items 8-9)
- Dynamic SOC calculation based on expected household consumption
- Advanced cheapest-energy-hours macro parameter exposure (look_ahead, weight, price_tolerance, etc.)
- Advanced Tibber sensor attribute configuration (custom attr_today, attr_tomorrow, value_key)
- Script entity or service call alternatives for battery control
- Validation UI for verifying sensor data format
- Battery capacity/current SOC inputs (handled in separate roadmap item 5)
- Actual charging automation logic (handled in roadmap item 4)
