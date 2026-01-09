# Task Breakdown: Solar Forecast Integration

## Overview
Total Tasks: 32

This feature integrates Forecast.Solar API data into the battery charging optimization system to calculate optimal morning SOC targets based on expected solar production.

## Task List

### External API Integration

#### Task Group 1: Forecast.Solar API Client
**Dependencies:** None

- [x] 1.0 Complete Forecast.Solar API client module
  - [x] 1.1 Write 4-6 focused tests for solar forecast API client
    - Test successful API response parsing with valid forecast data
    - Test extraction of daily kWh production from response
    - Test handling of API error responses (rate limit, invalid params)
    - Test retry logic with exponential backoff for transient failures
    - Mock all external API calls
  - [x] 1.2 Create `solar_forecast_service.py` module in `/workspace/tibber_prices/`
    - Follow `tibber_price_service.py` pattern for external API integration
    - Use callable `api_caller` pattern for testability
    - Include docstrings matching existing module style
  - [x] 1.3 Implement `build_forecast_url()` function
    - Build URL: `https://api.forecast.solar/estimate/{lat}/{lon}/{dec}/{az}/{kwp}`
    - Accept parameters: latitude, longitude, declination (tilt), azimuth, peak power kWp
    - Validate parameters are numeric and within valid ranges
  - [x] 1.4 Implement `fetch_solar_forecast()` function
    - Make HTTP GET request to Forecast.Solar API
    - Handle HTTP errors and timeouts gracefully
    - Log request/response details at debug level
    - Return raw response dictionary
  - [x] 1.5 Implement `parse_forecast_response()` function
    - Follow `parse_service_response()` pattern from tibber_price_service.py
    - Extract watt_hours or watt_hours_day from response structure
    - Return daily production forecast in kWh
    - Log warnings for malformed responses
  - [x] 1.6 Implement retry with exponential backoff
    - Max 3 retry attempts for transient failures
    - Exponential backoff: 1s, 2s, 4s delays
    - Follow error handling standards (fail fast, specific exceptions)
  - [x] 1.7 Ensure API client tests pass
    - Run ONLY the 4-6 tests written in 1.1
    - Verify all API parsing and error handling works
    - Do NOT run the entire test suite

**Acceptance Criteria:**
- The 4-6 tests written in 1.1 pass
- API URL construction is correct for all parameter combinations
- Response parsing extracts daily kWh production correctly
- Error handling covers rate limits, network errors, and invalid responses
- Retry logic executes with exponential backoff

---

### SOC Calculation Logic

#### Task Group 2: Optimal SOC Calculator
**Dependencies:** Task Group 1

- [x] 2.0 Complete optimal SOC calculation module
  - [x] 2.1 Write 4-6 focused tests for SOC calculation logic
    - Test basic formula: `target_soc = default_night_target - (expected_solar - morning_consumption - headroom) / capacity * 100`
    - Test clamping between minimum floor and default target
    - Test edge cases: zero solar forecast, high morning consumption
    - Test fallback to default target when calculation fails
  - [x] 2.2 Create `solar_soc_calculator.py` module in `/workspace/tibber_prices/`
    - Follow `duration_calculator.py` pattern for calculation logic
    - Include constants for default values
    - Use logging patterns consistent with existing modules
  - [x] 2.3 Implement `validate_soc_inputs()` function
    - Follow `validate_calculation_inputs()` pattern from duration_calculator.py
    - Validate: expected_solar_kwh, morning_consumption_kwh, battery_capacity_kwh, offset_kwh
    - Validate: default_target_soc and minimum_soc_floor are in 0-100 range
    - Return tuple of (is_valid, error_message)
  - [x] 2.4 Implement `calculate_optimal_soc()` function
    - Apply formula: `target_soc = default_night_target - (expected_solar_kwh - morning_consumption_kwh - headroom_offset_kwh) / battery_capacity_kwh * 100`
    - Clamp result between minimum_soc_floor and default_night_target
    - Return calculated SOC percentage as float
    - Log calculation steps at debug level
  - [x] 2.5 Implement `get_optimal_morning_soc()` orchestration function
    - Follow `get_dynamic_duration()` pattern from duration_calculator.py
    - Validate inputs, perform calculation, handle errors
    - Return fallback (default_night_target) on any failure
    - Log info-level summary of result
  - [x] 2.6 Ensure SOC calculator tests pass
    - Run ONLY the 4-6 tests written in 2.1
    - Verify formula produces correct results
    - Do NOT run the entire test suite

**Acceptance Criteria:**
- The 4-6 tests written in 2.1 pass
- Formula correctly calculates optimal SOC
- Clamping prevents values outside min/max bounds
- Fallback behavior activates on validation failure

---

### Blueprint Configuration

#### Task Group 3: Blueprint Input Configuration
**Dependencies:** None (can run in parallel with Task Groups 1-2)

- [x] 3.0 Complete blueprint input configuration for solar forecast
  - [x] 3.1 Write 2-4 focused tests for blueprint input validation
    - Test that new inputs have valid default values
    - Test input value constraints (min/max ranges)
    - Test toggle behavior for logging mode
    - These tests can be manual YAML validation checks if automated tests are impractical
  - [x] 3.2 Add solar forecast toggle input to blueprint
    - Input name: `solar_forecast_enabled`
    - Type: boolean selector
    - Default: false (backward compatible)
    - Description: Enable solar forecast integration for dynamic SOC targets
    - Place in new "Solar Forecast Configuration" section
  - [x] 3.3 Add morning consumption input
    - Input name: `morning_consumption_kwh`
    - Type: number selector
    - Range: 0-20 kWh, step 0.5
    - Default: 3 kWh
    - Description: Expected energy consumption between wake time and solar production start
  - [x] 3.4 Add SOC offset adjustment input
    - Input name: `soc_offset_kwh`
    - Type: number selector
    - Range: -10 to +10 kWh, step 0.5
    - Default: 0 kWh
    - Description: Adjustment offset for SOC calculation tuning (positive = higher SOC target)
  - [x] 3.5 Add minimum SOC floor input
    - Input name: `minimum_soc_floor`
    - Type: number selector
    - Range: 10-50%, step 5
    - Default: 20%
    - Description: Minimum SOC target regardless of solar forecast
  - [x] 3.6 Add logging mode toggle input
    - Input name: `solar_forecast_detailed_logging`
    - Type: boolean selector
    - Default: false
    - Description: Enable detailed logging for solar forecast calculations
  - [x] 3.7 Add solar system entity inputs for API parameters
    - Input name: `solar_panel_azimuth_sensor` (entity selector, domain: sensor/input_number)
    - Input name: `solar_panel_tilt_sensor` (entity selector, domain: sensor/input_number)
    - Input name: `solar_peak_power_kwp_sensor` (entity selector, domain: sensor/input_number)
    - These pull values from existing HA sensors rather than duplicating configuration
  - [x] 3.8 Validate blueprint YAML syntax
    - Load blueprint in Home Assistant test environment
    - Verify all new inputs appear in UI
    - Confirm default values are applied correctly

**Acceptance Criteria:**
- All new inputs have valid selectors and defaults
- Blueprint YAML parses without errors
- Input constraints enforce valid ranges
- New inputs are grouped in a logical section
- Backward compatibility maintained (feature disabled by default)

---

### Template Variables and Sensor Output

#### Task Group 4: Blueprint Variables and Sensor Template
**Dependencies:** Task Groups 1, 2, 3

- [x] 4.0 Complete blueprint variables and sensor template
  - [x] 4.1 Write 2-4 focused tests for template variable logic
    - Test optimal SOC calculation variable produces correct values
    - Test fallback behavior when solar forecast unavailable
    - Test sensor attribute formatting
    - Manual Jinja2 template testing acceptable
  - [x] 4.2 Add input variable references to blueprint variables section
    - Add references for all new inputs from Task Group 3
    - Follow existing pattern: `solar_forecast_enabled: !input solar_forecast_enabled`
    - Include: morning_consumption_kwh, soc_offset_kwh, minimum_soc_floor, etc.
  - [x] 4.3 Create solar forecast fetch variable template
    - Template variable: `solar_forecast_kwh`
    - Call solar forecast service with HA sensor values for lat/lon/azimuth/tilt/kwp
    - Store result in variable for use in SOC calculation
    - Return -1 or null when forecast unavailable
  - [x] 4.4 Create optimal SOC calculation variable template
    - Template variable: `optimal_morning_soc`
    - Implement SOC formula in Jinja2 (mirroring Python module logic)
    - Use: expected_solar_kwh, morning_consumption_kwh, soc_offset_kwh, battery_capacity, night_target_soc
    - Clamp between minimum_soc_floor and night_target_soc
    - Fall back to night_target_soc when solar_forecast_enabled is false or forecast unavailable
  - [x] 4.5 Create sensor attributes template
    - Include attributes: expected_solar_kwh, morning_consumption_kwh, offset_applied, calculation_timestamp, forecast_source
    - Format as dictionary for sensor state attributes
    - Follow existing variable template patterns
  - [x] 4.6 Ensure template variable tests pass
    - Validate Jinja2 templates render correctly
    - Test with sample sensor values
    - Verify fallback behavior

**Acceptance Criteria:**
- Template variables calculate correct optimal SOC
- Sensor attributes include all required fields
- Fallback to default target works when forecast disabled/unavailable
- Templates follow existing blueprint patterns

---

### Polling and Automation Triggers

#### Task Group 5: Hourly Polling Automation
**Dependencies:** Task Group 4

- [x] 5.0 Complete hourly polling automation triggers
  - [x] 5.1 Write 2-3 focused tests for polling trigger logic
    - Test hourly trigger fires correctly
    - Test forecast storage updates on successful fetch
    - Test reduced polling during nighttime hours (optional enhancement)
  - [x] 5.2 Add hourly time trigger for solar forecast polling
    - Trigger type: time_pattern
    - Pattern: every hour on the hour (`hours: '/1'`)
    - Condition: only fire when solar_forecast_enabled is true
    - Follow existing trigger patterns in blueprint
  - [x] 5.3 Add solar forecast fetch action sequence
    - Action: call solar forecast service/script
    - Store result in template sensor or input_text helper
    - Log fetch status (success/failure) at appropriate level
    - Handle API rate limits (12 requests/hour for free tier)
  - [x] 5.4 Add forecast result storage mechanism
    - Use input_text or template sensor to persist latest forecast
    - Include timestamp of last successful fetch
    - Make forecast value accessible to SOC calculation templates
  - [x] 5.5 Add optional nighttime polling reduction
    - Condition: reduce polling frequency between sunset and sunrise
    - Implementation: skip fetch if sun is below horizon
    - Or use longer interval (every 3 hours) during night
  - [x] 5.6 Ensure polling trigger tests pass
    - Verify trigger fires at correct intervals
    - Confirm forecast storage works correctly

**Acceptance Criteria:**
- Hourly polling trigger activates correctly
- Forecast results persist between polls
- Rate limits respected (max 12 requests/hour)
- Polling respects solar_forecast_enabled toggle

---

### Night Charging Integration

#### Task Group 6: Integration with Night Charging
**Dependencies:** Task Groups 2, 4, 5

- [x] 6.0 Complete integration with existing night charging logic
  - [x] 6.1 Write 3-4 focused tests for night charging integration
    - Test optimal SOC replaces static night_target_soc when forecast enabled
    - Test backward compatibility when solar_forecast_enabled is false
    - Test fallback to night_target_soc when forecast unavailable
    - Test integration with existing skip logic (SOC already at target)
  - [x] 6.2 Modify night charging calculation to use optimal SOC
    - Update `calculated_charging_duration` variable to use `optimal_morning_soc` when available
    - Maintain existing calculation when solar_forecast_enabled is false
    - Follow existing conditional template patterns
  - [x] 6.3 Update night charging automation action sequence
    - Replace hardcoded night_target_soc with optimal_morning_soc where applicable
    - Ensure switch control uses correct target for duration calculation
    - Maintain existing fallback behavior patterns
  - [x] 6.4 Add solar-aware skip condition
    - Extend existing SOC skip logic to consider optimal_morning_soc
    - If current_soc >= optimal_morning_soc, skip charging
    - Log which target was used for skip decision
  - [x] 6.5 Ensure integration tests pass
    - Run ONLY the 3-4 tests written in 6.1
    - Verify charging uses correct SOC target
    - Do NOT run entire test suite

**Acceptance Criteria:**
- Night charging uses optimal SOC when solar forecast enabled
- Backward compatibility maintained when feature disabled
- Fallback to static target works correctly
- Skip logic respects dynamic SOC target

---

### Notifications and Logging

#### Task Group 7: Notification and Logging Extensions
**Dependencies:** Task Group 6

- [x] 7.0 Complete notification and logging for solar forecast
  - [x] 7.1 Write 2-4 focused tests for notification messages
    - Test basic logging message format
    - Test detailed logging message format with calculation breakdown
    - Test fallback warning notification
    - Test notification payload structure
  - [x] 7.2 Extend NotificationType enum (if needed)
    - Add `SOLAR_FORECAST` type for forecast-related notifications
    - Add `SOLAR_FALLBACK` type for fallback warnings
    - Follow existing enum pattern in notifications.py
  - [x] 7.3 Implement basic logging message builder
    - Format: "Target SOC: 45% (expected solar: 12 kWh, morning consumption: 5 kWh)"
    - Follow `build_notification_message()` pattern
    - Include key values in concise format
  - [x] 7.4 Implement detailed logging message builder
    - Include: battery headroom calculation breakdown
    - Include: forecast API response timestamp
    - Include: raw forecast values (watt-hours per period)
    - Include: calculation formula steps with intermediate values
  - [x] 7.5 Add notification action to automation
    - Send notification after SOC calculation completes
    - Respect logging mode toggle (basic vs detailed)
    - Use existing notification service pattern
  - [x] 7.6 Add fallback warning notification
    - Trigger when forecast API fails after retries
    - Message: "Solar forecast unavailable, using default SOC target: X%"
    - Log at warning level
  - [x] 7.7 Ensure notification tests pass
    - Run ONLY the 2-4 tests written in 7.1
    - Verify message formatting is correct

**Acceptance Criteria:**
- Basic and detailed logging modes work correctly
- Notification messages are clear and informative
- Fallback warning triggers on API failure
- Logging mode toggle respected

---

### Testing

#### Task Group 8: Test Review and Gap Analysis
**Dependencies:** Task Groups 1-7

- [x] 8.0 Review existing tests and fill critical gaps only
  - [x] 8.1 Review tests from Task Groups 1-7
    - Review tests from Task 1.1 (API client: 12 tests)
    - Review tests from Task 2.1 (SOC calculator: 15 tests)
    - Review tests from Task 3.1 (Blueprint inputs: 15 tests)
    - Review tests from Task 4.1 (Template variables: 17 tests)
    - Review tests from Task 5.1 (Polling: 9 tests)
    - Review tests from Task 6.1 (Integration: 11 tests)
    - Review tests from Task 7.1 (Notifications: 9 tests)
    - Total existing tests: 88 tests
  - [x] 8.2 Analyze test coverage gaps for solar forecast feature only
    - Identified critical end-to-end workflows lacking coverage
    - Focused ONLY on solar forecast feature requirements
    - Did NOT assess entire application test coverage
    - Prioritized: API -> calculation -> integration workflow
  - [x] 8.3 Write up to 10 additional strategic tests maximum
    - End-to-end test: fetch forecast -> calculate SOC -> update charging target (3 tests)
    - Edge case: very high solar forecast results in minimum SOC floor (covered in end-to-end)
    - Edge case: zero solar forecast results in default night target (covered in end-to-end)
    - Error recovery: API failure -> retry -> fallback behavior (2 tests)
    - Negative offset behavior test (1 test)
    - API response parsing edge cases (2 tests)
    - Notification integration test (1 test)
    - Added 9 new tests to fill critical gaps
    - Skipped exhaustive edge case and performance testing
  - [x] 8.4 Run feature-specific tests only
    - Ran ONLY tests related to solar forecast feature
    - Total: 97 tests (88 existing + 9 new)
    - Did NOT run entire application test suite
    - All critical workflows pass

**Acceptance Criteria:**
- All feature-specific tests pass (97 tests total)
- Critical end-to-end workflows for solar forecast are covered
- 9 additional tests added (within 10 max limit)
- Testing focused exclusively on solar forecast feature

---

## Execution Order

Recommended implementation sequence:

1. **Task Group 1: Forecast.Solar API Client** - Core API integration (no dependencies)
2. **Task Group 3: Blueprint Input Configuration** - Can run in parallel with Group 1
3. **Task Group 2: Optimal SOC Calculator** - Depends on Group 1 patterns
4. **Task Group 4: Template Variables and Sensor** - Depends on Groups 1, 2, 3
5. **Task Group 5: Hourly Polling Automation** - Depends on Group 4
6. **Task Group 6: Night Charging Integration** - Depends on Groups 2, 4, 5
7. **Task Group 7: Notifications and Logging** - Depends on Group 6
8. **Task Group 8: Test Review and Gap Analysis** - Final validation

## Technical Notes

### API Rate Limits
- Forecast.Solar free tier: 12 requests per hour
- Implement rate limit awareness in polling logic
- Consider caching forecast for 1 hour between refreshes

### Existing Patterns to Follow
- `tibber_price_service.py` - External API integration pattern
- `duration_calculator.py` - Calculation and validation pattern
- `notifications.py` - Notification message building pattern
- `night_charging.py` - Automation orchestration pattern
- Blueprint input selectors - Consistent naming and grouping

### Backward Compatibility
- Feature disabled by default (`solar_forecast_enabled: false`)
- All existing functionality unchanged when feature is off
- Static `night_target_soc` used when solar forecast unavailable

### Home Assistant Integration Points
- Solar system sensors for lat/lon/azimuth/tilt/kwp (existing HA entities)
- Template sensor for exposing calculated optimal SOC
- Persistent notification service for logging output
- Input helpers for storing forecast results between automations
