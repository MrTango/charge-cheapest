# Specification: Tibber Price Data Integration

## Goal

Implement a custom `tibber.get_prices` service wrapper with cross-midnight price fetching capability and recreate the cheapest hours calculation logic internally, fixing the limitation where Tibber price data cuts off at midnight.

## User Stories

- As a battery owner, I want complete price coverage for overnight charging windows (23:00-06:00) so that the cheapest hours are correctly identified even when the window spans midnight
- As a developer, I want full control over the cheapest hours calculation logic so that I can fix bugs and customize behavior without depending on external blueprints

## Specific Requirements

**Tibber Get Prices Service Integration**
- Create a wrapper function to call the `tibber.get_prices` Home Assistant service
- Accept start datetime and end datetime parameters for the price range
- Parse the service response from the `prices.null` key structure
- Extract `start_time` (ISO 8601 with timezone) and `price` from each entry
- Handle 15-minute interval granularity in the response format
- Return a normalized array of price data with consistent structure

**Cross-Midnight Price Fetching**
- Detect when a requested time range spans midnight (end time < start time or end date > start date)
- Split cross-midnight requests into two separate `tibber.get_prices` calls
- First call: from start datetime until 23:59:59 on the start date
- Second call: from 00:00:00 until end datetime on the following day
- Merge both result sets into a single continuous price array sorted by timestamp
- Handle timezone considerations to ensure correct date boundary detection
- Validate merged array has no gaps or duplicate timestamps

**Cheapest Hours Calculation Logic**
- Accept parameters: price array, number of hours needed, optional time window constraints
- Implement sliding window algorithm to find consecutive hours with lowest total cost
- Calculate total cost by summing price values within each candidate window
- Track the window with minimum total cost and its start time
- Return result object containing: start datetime, list of hours in cheapest window, total cost
- Handle edge case where requested hours exceed available price data

**15-Minute to Hourly Data Conversion**
- Convert 15-minute interval service data to hourly granularity
- Group intervals by hour based on `start_time` timestamp
- Calculate hourly price as average of 4 constituent 15-minute intervals
- Handle partial hours at boundaries (use available intervals only)
- Preserve timezone information during conversion

**Data Normalization**
- Standardize price array format: `{ timestamp: ISO8601, price: number }`
- Parse ISO 8601 timestamps with timezone offset (e.g., "2026-01-08T00:15:00.000+01:00")
- Sort price entries chronologically by timestamp
- Validate price values are numeric and non-negative
- Handle missing or null price entries gracefully

**Pytest Test Coverage**
- Test `tibber.get_prices` response parsing with sample data from `planning/prices.yaml`
- Test cross-midnight detection for various time range scenarios
- Test service call splitting and result merging logic
- Test cheapest hours calculation with known price arrays and expected results
- Test 15-minute to hourly conversion accuracy
- Mock external service calls to isolate unit tests

## Visual Design

No visual assets provided for this specification.

## Existing Code to Leverage

**`/workspace/blueprints/automation/charge_cheapest.yaml`**
- Contains existing `price_sensor` entity selector pattern
- Documents current hardcoded macro parameters (attr_today, attr_tomorrow, value_key)
- Shows blueprint input configuration structure for future integration
- Night schedule inputs (night_start_time, night_end_time) define typical cross-midnight windows

**`/workspace/agent-os/specs/2026-01-07-tibber-price-data-integration/planning/prices.yaml`**
- Contains actual `tibber.get_prices` service response format
- Shows 15-minute interval structure with `start_time` and `price` keys
- Demonstrates ISO 8601 timestamp format with +01:00 timezone offset
- Use as test fixture data for parsing and conversion tests

**`/workspace/ha-sensor-states.md`**
- Documents Tibber sensor attribute format with `today` array containing `total` values
- Shows position-based hourly structure (24 entries, index = hour)
- Demonstrates data format difference between sensor attributes and service response

**`/workspace/tests/*.test.js`**
- Provides test file naming conventions (feature-name.test.js)
- Shows YAML parsing approach using js-yaml library for test fixtures
- Demonstrates assertion patterns for configuration validation

## Out of Scope

- External `cheapest-energy-hours` blueprint or macro dependency (explicitly replacing with custom implementation)
- Template sensor creation (this spec focuses on service call wrapper and calculation logic only)
- Price estimation strategy when tomorrow's prices are unavailable
- Solar forecast integration
- Multi-battery support
- Blueprint input configuration changes (attr_today, attr_tomorrow, value_key inputs)
- Real-time price updates or WebSocket subscriptions
- Historical price data storage or analysis
- Cost calculation or reporting features
