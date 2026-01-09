# Task Breakdown: Tibber Price Data Integration

## Overview
Total Tasks: 24

This feature implements a custom `tibber.get_prices` service wrapper with cross-midnight price fetching capability and internal cheapest hours calculation logic, replacing dependency on external blueprints.

## Task List

### Core Price Data Layer

#### Task Group 1: Tibber Service Wrapper & Response Parsing
**Dependencies:** None

- [x] 1.0 Complete Tibber service wrapper implementation
  - [x] 1.1 Write 4-6 focused tests for service response parsing
    - Test parsing `prices.null` key structure from service response
    - Test extraction of `start_time` and `price` fields from entries
    - Test handling of ISO 8601 timestamps with timezone offset
    - Test handling of empty or malformed responses
    - Use fixture data from `planning/prices.yaml`
  - [x] 1.2 Create `tibber_price_service.py` module with wrapper function
    - Function signature: `get_prices(start_datetime, end_datetime) -> list[dict]`
    - Call `tibber.get_prices` Home Assistant service
    - Accept datetime objects for start and end parameters
    - Return normalized list of price entries
  - [x] 1.3 Implement response parser for `prices.null` structure
    - Extract price array from nested `prices.null` key
    - Handle missing or null keys gracefully
    - Validate response structure before parsing
  - [x] 1.4 Implement entry field extraction
    - Extract `start_time` as ISO 8601 string with timezone
    - Extract `price` as numeric value
    - Validate each entry has required fields
  - [x] 1.5 Ensure service wrapper tests pass
    - Run ONLY the 4-6 tests written in 1.1
    - Verify parsing logic handles sample data correctly

**Acceptance Criteria:**
- The 4-6 tests written in 1.1 pass
- Service wrapper correctly parses `prices.null` response structure
- ISO 8601 timestamps with timezone offsets are preserved
- Invalid responses return empty list with logged warning

---

#### Task Group 2: Data Normalization & Conversion
**Dependencies:** Task Group 1

- [x] 2.0 Complete data normalization layer
  - [x] 2.1 Write 4-6 focused tests for data normalization
    - Test standardization to `{ timestamp: ISO8601, price: number }` format
    - Test chronological sorting of price entries
    - Test 15-minute to hourly conversion (average of 4 intervals)
    - Test handling of partial hours at boundaries
    - Test validation of numeric and non-negative prices
  - [x] 2.2 Create `price_normalizer.py` module
    - Function: `normalize_price_entries(entries) -> list[dict]`
    - Standardize to format: `{ timestamp: str, price: float }`
    - Sort entries chronologically by timestamp
  - [x] 2.3 Implement ISO 8601 timestamp parsing
    - Parse timestamps like "2026-01-08T00:15:00.000+01:00"
    - Preserve timezone information
    - Use Python datetime for parsing
  - [x] 2.4 Implement 15-minute to hourly conversion
    - Function: `convert_to_hourly(entries) -> list[dict]`
    - Group intervals by hour based on `start_time`
    - Calculate hourly price as average of constituent intervals
    - Handle partial hours using available intervals only
  - [x] 2.5 Implement price validation
    - Validate prices are numeric
    - Validate prices are non-negative
    - Handle null/missing prices gracefully (skip or warn)
  - [x] 2.6 Ensure normalization tests pass
    - Run ONLY the 4-6 tests written in 2.1
    - Verify conversion accuracy with known inputs

**Acceptance Criteria:**
- The 4-6 tests written in 2.1 pass
- Price entries normalized to consistent format
- 15-minute intervals correctly averaged to hourly
- Invalid price entries handled gracefully

---

### Cross-Midnight Logic Layer

#### Task Group 3: Cross-Midnight Detection & Request Splitting
**Dependencies:** Task Groups 1-2

- [x] 3.0 Complete cross-midnight price fetching
  - [x] 3.1 Write 4-6 focused tests for cross-midnight logic
    - Test detection when end time < start time (e.g., 23:00-06:00)
    - Test detection when end date > start date
    - Test request splitting into two service calls
    - Test result merging into continuous sorted array
    - Test no gaps or duplicate timestamps in merged result
  - [x] 3.2 Implement cross-midnight detection
    - Function: `spans_midnight(start_dt, end_dt) -> bool`
    - Detect when end time is earlier than start time
    - Detect when end date is on a different day
    - Handle timezone considerations correctly
  - [x] 3.3 Implement request splitting logic
    - Function: `split_cross_midnight_range(start_dt, end_dt) -> tuple`
    - First range: start datetime until 23:59:59 on start date
    - Second range: 00:00:00 until end datetime on following day
    - Return tuple of two datetime ranges
  - [x] 3.4 Implement result merging
    - Function: `merge_price_results(results_day1, results_day2) -> list`
    - Concatenate both result sets
    - Sort by timestamp chronologically
    - Validate no gaps in the merged sequence
    - Remove any duplicate timestamps (prefer later data)
  - [x] 3.5 Create unified fetch function
    - Function: `fetch_prices_range(start_dt, end_dt) -> list`
    - Detect if range spans midnight
    - Make single call or split calls as needed
    - Return merged and normalized result
  - [x] 3.6 Ensure cross-midnight tests pass
    - Run ONLY the 4-6 tests written in 3.1
    - Verify 23:00-06:00 overnight window handled correctly

**Acceptance Criteria:**
- The 4-6 tests written in 3.1 pass
- Cross-midnight ranges correctly detected
- Service calls properly split at midnight boundary
- Merged results are continuous and sorted

---

### Cheapest Hours Calculation Layer

#### Task Group 4: Cheapest Hours Algorithm
**Dependencies:** Task Groups 1-3

- [x] 4.0 Complete cheapest hours calculation logic
  - [x] 4.1 Write 4-6 focused tests for cheapest hours algorithm
    - Test sliding window finds correct minimum cost window
    - Test with known price arrays and expected results
    - Test optional time window constraints
    - Test edge case where requested hours exceed available data
    - Test result object contains start datetime, hours list, total cost
  - [x] 4.2 Create `cheapest_hours.py` module
    - Function signature: `find_cheapest_hours(prices, hours_needed, time_window=None) -> dict`
    - Accept normalized price array
    - Accept integer for hours needed
    - Accept optional tuple for time window constraints (start, end)
  - [x] 4.3 Implement sliding window algorithm
    - Initialize window at start of price array
    - Calculate total cost for each window position
    - Track minimum cost window and its start position
    - Slide window by one hour and recalculate
  - [x] 4.4 Implement result object construction
    - Return dict with `start_datetime` (ISO 8601)
    - Return list of hours in cheapest window
    - Return `total_cost` as sum of prices in window
    - Handle edge cases with informative error responses
  - [x] 4.5 Implement time window constraints
    - Filter price array to specified time window before calculation
    - Validate constraint times are within available data
    - Return error if constraint leaves insufficient data
  - [x] 4.6 Ensure cheapest hours tests pass
    - Run ONLY the 4-6 tests written in 4.1
    - Verify algorithm matches expected results for known inputs

**Acceptance Criteria:**
- The 4-6 tests written in 4.1 pass
- Sliding window correctly identifies minimum cost period
- Result object contains all required fields
- Edge cases handled gracefully with clear errors

---

### Integration Layer

#### Task Group 5: Module Integration & Public API
**Dependencies:** Task Groups 1-4

- [x] 5.0 Complete integration and public API
  - [x] 5.1 Write 3-5 focused tests for integrated workflow
    - Test end-to-end: fetch prices -> normalize -> find cheapest hours
    - Test overnight window (23:00-06:00) scenario
    - Test integration with sample data from `planning/prices.yaml`
    - Mock `tibber.get_prices` service calls
  - [x] 5.2 Create `tibber_prices/__init__.py` with public API
    - Export: `get_prices(start_dt, end_dt) -> list`
    - Export: `find_cheapest_hours(prices, hours, window=None) -> dict`
    - Export: `get_cheapest_charging_window(start_dt, end_dt, hours) -> dict`
  - [x] 5.3 Implement convenience function for charging use case
    - Function: `get_cheapest_charging_window(start_dt, end_dt, hours_needed)`
    - Combines fetch, normalize, and calculate steps
    - Returns ready-to-use result for automation
  - [x] 5.4 Add module-level error handling
    - Catch service call failures gracefully
    - Return informative error states
    - Log warnings for partial data scenarios
  - [x] 5.5 Ensure integration tests pass
    - Run ONLY the 3-5 tests written in 5.1
    - Verify end-to-end workflow produces correct results

**Acceptance Criteria:**
- The 3-5 tests written in 5.1 pass
- Public API is clean and well-documented
- End-to-end workflow handles overnight windows correctly
- External service failures handled gracefully

---

### Testing & Quality Assurance

#### Task Group 6: Test Review & Gap Analysis
**Dependencies:** Task Groups 1-5

- [x] 6.0 Review existing tests and fill critical gaps only
  - [x] 6.1 Review tests from Task Groups 1-5
    - Review the 4-6 tests from service wrapper (Task 1.1)
    - Review the 4-6 tests from normalization (Task 2.1)
    - Review the 4-6 tests from cross-midnight (Task 3.1)
    - Review the 4-6 tests from cheapest hours (Task 4.1)
    - Review the 3-5 tests from integration (Task 5.1)
    - Total existing tests: approximately 19-29 tests
  - [x] 6.2 Analyze test coverage gaps for THIS feature only
    - Identify critical user workflows lacking coverage
    - Focus ONLY on gaps related to this spec's requirements
    - Prioritize overnight charging window scenario
    - Do NOT assess entire application test coverage
  - [x] 6.3 Write up to 10 additional strategic tests maximum
    - Focus on integration points between modules
    - Test realistic overnight charging scenarios (23:00-06:00)
    - Test timezone edge cases if not covered
    - Skip exhaustive edge case testing
  - [x] 6.4 Run feature-specific tests only
    - Run ONLY tests related to Tibber price data integration
    - Expected total: approximately 20-39 tests maximum
    - Do NOT run tests from other features
    - Verify critical workflows pass
  - [x] 6.5 Run linting with Ruff
    - Ensure all Python code passes Ruff checks
    - Fix any style or formatting issues

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 20-39 tests total)
- Critical overnight charging workflow is covered
- No more than 10 additional tests added when filling gaps
- Code passes Ruff linting checks

---

## Execution Order

Recommended implementation sequence:

1. **Task Group 1: Tibber Service Wrapper** - Foundation for all price data access
2. **Task Group 2: Data Normalization** - Transforms raw data to usable format
3. **Task Group 3: Cross-Midnight Logic** - Solves the core midnight cutoff problem
4. **Task Group 4: Cheapest Hours Algorithm** - Core business logic for price optimization
5. **Task Group 5: Module Integration** - Combines components into usable API
6. **Task Group 6: Test Review** - Ensures quality and fills critical test gaps

## File Structure

Expected output structure:
```
/workspace/
  tibber_prices/
    __init__.py              # Public API exports
    tibber_price_service.py  # Service wrapper (Task Group 1)
    price_normalizer.py      # Data normalization (Task Group 2)
    cross_midnight.py        # Cross-midnight logic (Task Group 3)
    cheapest_hours.py        # Calculation algorithm (Task Group 4)
  tests/
    test_tibber_service.py   # Task 1.1 tests
    test_price_normalizer.py # Task 2.1 tests
    test_cross_midnight.py   # Task 3.1 tests
    test_cheapest_hours.py   # Task 4.1 tests
    test_integration.py      # Task 5.1 tests
    test_gap_analysis.py     # Task 6.3 strategic tests
```

## Test Fixture Reference

Use sample data from `/workspace/agent-os/specs/2026-01-07-tibber-price-data-integration/planning/prices.yaml` for testing:
- 15-minute interval data from 00:15 to 14:45
- ISO 8601 timestamps with +01:00 timezone
- Price range from ~0.25 to ~0.50
- Contains morning price spike pattern (useful for cheapest hours testing)

## Notes

- Tech stack: Python, pytest, Ruff
- Follow TDD approach: write tests before implementation
- Mock `tibber.get_prices` service calls in tests
- Preserve timezone information throughout processing
- Handle partial data gracefully with warnings
