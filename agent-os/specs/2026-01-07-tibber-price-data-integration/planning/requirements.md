# Spec Requirements: Tibber Price Data Integration

## Initial Description

From roadmap item 2: "Implement template logic to read hourly price data from Tibber sensor attributes (today/tomorrow arrays). Support both core integration and custom component formats with configurable attribute names."

From raw-idea.md: Create the Tibber Price Data Integration feature for the Home Assistant Blueprint.

## Requirements Discussion

### First Round Questions

**Q1:** I assume the primary goal is to create Jinja2 template logic that extracts the `today` and `tomorrow` price arrays from the Tibber sensor and makes them available for the `cheapest-energy-hours` macro. Is that correct, or should this spec include additional data transformations?
**Answer:** Yes, the goal is to use the cheapest-energy-hours macro from https://github.com/TheFes/cheapest-energy-hours

**Q2:** The roadmap mentions supporting "both core integration and custom component formats with configurable attribute names," but the completed Blueprint Configuration Schema spec explicitly states that advanced attribute configuration is NOT exposed to users (hardcoded to `today`/`tomorrow`/`total`). Should we: A) Follow the schema spec and only support standard Tibber format (simpler), or B) Override that decision and add attribute name configuration inputs?
**Answer:** Option B - Override the schema decision and add attribute name configuration inputs

**Q3:** I'm thinking the template logic should include validation to detect when `tomorrow` prices are unavailable (empty array before ~13:00) and flag this state for downstream logic. Should this spec also implement the price estimation strategy (repeating last 3 hours before 1pm), or defer that to a separate task?
**Answer:** No - don't implement price estimation strategy in this spec

**Q4:** The existing blueprint has `price_sensor` as a configured input. I assume the template logic will reference this via `!input price_sensor` and access its state/attributes. Should the template logic be implemented as: A) Inline Jinja2 within the blueprint's trigger/condition/action sections, or B) A separate template sensor definition that preprocesses the data?
**Answer:** Important clarification about a limitation: The existing blueprint has a configurable sensor (e.g., `sensor.electricity_price_prognose_laaver_weg_2`), but there's a limitation - it only returns today's prices and cuts off everything after midnight. To get prices after midnight, they need to call `tibber.get_prices` service with a time range from midnight until 1pm next day and merge the results. They want to incorporate this logic directly rather than relying on the external blueprint.

**Q5:** For testing the template logic, I assume we'll use the existing Jest test infrastructure (seen in `/workspace/tests/`). Is that correct, or do you prefer testing via Home Assistant's Developer Tools > Template?
**Answer:** Yes, use Jest test infrastructure

**Q6:** Is there anything that should be explicitly excluded from this spec (e.g., specific edge cases, integration with other sensors, error handling approaches)?
**Answer:** (Not answered - no explicit exclusions mentioned)

### Existing Code to Reference

**Similar Features Identified:**
- Feature: Blueprint Configuration Schema - Path: `/workspace/blueprints/automation/charge_cheapest.yaml`
- Feature: Tibber sensor data format documentation - Path: `/workspace/ha-sensor-states.md`
- Feature: Service response format - Path: `/workspace/agent-os/specs/2026-01-07-tibber-price-data-integration/planning/prices.yaml`
- External dependency: cheapest-energy-hours macro - URL: https://github.com/TheFes/cheapest-energy-hours

### Follow-up Questions

**Follow-up 1:** You mentioned calling `tibber.get_prices` service to get prices after midnight. This is a significant architectural decision. The `cheapest-energy-hours` macro supports a `price_data` parameter that accepts action response data directly. Should the blueprint: A) Call `tibber.get_prices` as a service action and pass the response to the macro via `price_data`, OR B) Create a template sensor that merges the data and then reference that sensor in the macro?
**Answer:** Option B - Create a template sensor that merges the data

**Follow-up 2:** For the `tibber.get_prices` service call, what parameters does it accept and what is the response format?
**Answer:** The `tibber.get_prices` service accepts start and end date/time parameters. The response format shows:
- 15-minute interval granularity
- Each entry has `start_time` (ISO 8601 format with timezone, e.g., "2026-01-08T00:15:00.000+01:00") and `price` (decimal value)
- Response is keyed under "null" in the YAML structure

**Follow-up 3:** For the attribute name configuration, which attributes should be configurable: `attr_today`, `attr_tomorrow`, `value_key`? Should we also include `time_key` and `datetime_in_data`?
**Answer:** Yes - the attribute configuration set is correct (attr_today, attr_tomorrow, value_key)

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
Not applicable.

## Requirements Summary

### Functional Requirements

**Core Data Access**
- Read hourly price data from Tibber sensor's `today` attribute (array of price objects)
- Read hourly price data from Tibber sensor's `tomorrow` attribute (when available, after ~13:00)
- Call `tibber.get_prices` service to retrieve post-midnight prices (midnight to 1pm next day)
- Merge sensor attribute data with service call response into unified price dataset

**Template Sensor Creation**
- Create a template sensor that combines today's prices from sensor attributes with tomorrow's prices from the `tibber.get_prices` service call
- Handle the data format differences between sources:
  - Sensor attributes: hourly data, key `total` for price value, no explicit timestamp (position-based)
  - Service response: 15-minute intervals, key `price` for value, key `start_time` for ISO 8601 timestamp
- Normalize data to consistent format compatible with `cheapest-energy-hours` macro

**Data Format Handling**

Tibber Sensor Attribute Format (from `/workspace/ha-sensor-states.md`):
```yaml
today:
  - total: 0.2696  # Hour 0
  - total: 0.2632  # Hour 1
  # ... 24 entries, position = hour
tomorrow:
  # Same structure, available after ~13:00
```

Tibber Service Response Format (from `/workspace/agent-os/specs/2026-01-07-tibber-price-data-integration/planning/prices.yaml`):
```yaml
prices:
  "null":
    - start_time: "2026-01-08T00:15:00.000+01:00"
      price: 0.26
    - start_time: "2026-01-08T00:30:00.000+01:00"
      price: 0.2561
    # 15-minute intervals
```

**Configurable Attribute Names**
- `attr_today`: Attribute name for today's prices (default: 'today')
- `attr_tomorrow`: Attribute name for tomorrow's prices (default: 'tomorrow')
- `value_key`: Key within price objects containing the price value (default: 'total')

**Integration with cheapest-energy-hours Macro**
- Output data format must be compatible with the macro's expected input
- Support passing data via sensor attributes or `price_data` parameter
- Macro parameters to use:
  - `sensor`: The merged template sensor entity
  - `attr_today` / `attr_tomorrow`: Configurable attribute names
  - `value_key`: Configurable price value key
  - `datetime_in_data`: Set based on data format (false for position-based, true for timestamped)
  - `time_key`: Set to 'start_time' when using service response data

### Configuration Inputs Needed

The following inputs must be added to the blueprint (extending the existing schema):

```yaml
# Tibber Attribute Configuration
attr_today:
  name: Today Prices Attribute
  description: Attribute name containing today's price array
  default: "today"
  selector:
    text:

attr_tomorrow:
  name: Tomorrow Prices Attribute
  description: Attribute name containing tomorrow's price array
  default: "tomorrow"
  selector:
    text:

value_key:
  name: Price Value Key
  description: Key within each price object containing the price value
  default: "total"
  selector:
    text:
```

### Reusability Opportunities

- Existing blueprint at `/workspace/blueprints/automation/charge_cheapest.yaml` already has the `price_sensor` entity selector configured
- The `cheapest-energy-hours` macro provides battle-tested price calculation logic
- Jest test infrastructure in `/workspace/tests/` for testing template logic
- Sensor data format documentation in `/workspace/ha-sensor-states.md` for reference

### Scope Boundaries

**In Scope:**
- Template sensor creation that merges Tibber sensor data with service call data
- Data format normalization between sensor attributes and service response
- Configurable attribute name inputs (attr_today, attr_tomorrow, value_key)
- Integration with cheapest-energy-hours macro
- Jest tests for the template logic
- Handling of tomorrow's prices unavailability (before ~13:00)

**Out of Scope:**
- Price estimation strategy when tomorrow's prices unavailable (explicitly deferred)
- Multi-battery support (roadmap item 10)
- Solar forecast integration (roadmap items 8-9)
- Advanced macro parameters (look_ahead, weight, price_tolerance, etc.)
- time_key and datetime_in_data configuration (hardcoded based on data source)

### Technical Considerations

**Data Granularity Mismatch**
- Sensor attributes: Hourly data (24 entries per day)
- Service response: 15-minute intervals (4 entries per hour)
- Decision needed: Convert 15-minute to hourly (average) or pass raw to macro (macro handles `data_minutes` parameter)

**Service Call Timing**
- The `tibber.get_prices` service should be called to get prices from midnight to 1pm next day
- This provides overlap coverage for overnight charging schedules (23:00-06:00)

**Template Sensor Update Trigger**
- Sensor should update when source Tibber sensor updates
- May need periodic refresh to re-call service for latest data

**cheapest-energy-hours Macro Compatibility**
- Macro supports `data_minutes` parameter (default: 60) for non-hourly data
- Macro can handle mixed formats via `price_data` parameter
- Macro auto-detects some source formats (Nordpool, Amber, etc.) but Tibber custom format needs explicit configuration

**Existing Blueprint Integration**
- Current blueprint already references `price_sensor` input
- New attribute configuration inputs extend the existing schema
- Template sensor becomes an intermediary between raw Tibber data and charging automation
