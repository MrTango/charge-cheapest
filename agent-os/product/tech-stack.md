# Tech Stack

## Primary Technology

### Home Assistant Blueprint (YAML)

The product is implemented as a **Home Assistant Blueprint**, which is the preferred approach for this use case because:

- **User-friendly configuration**: Blueprints provide a UI-based setup experience without requiring YAML editing
- **Shareable**: Can be easily distributed via GitHub and imported with a single URL
- **Maintainable**: Updates to the blueprint automatically propagate to users who imported it
- **No custom integration overhead**: Works with standard Home Assistant installations

### Language/Templating

- **YAML**: Blueprint structure and automation definitions
- **Jinja2**: Template logic for price calculations, time comparisons, and dynamic value computation

## Dependencies

### Required

- **Home Assistant Core**: Minimum version TBD based on blueprint features used
- **Tibber Integration**: The official Tibber integration for price data access
  - Provides `tibber.get_prices` service for fetching price data with time ranges
  - Enables cross-midnight price fetching by making multiple service calls

### tibber.get_prices Service

The blueprint uses `tibber.get_prices` service directly instead of relying on sensor attributes. This enables:

- **Flexible time ranges**: Request prices for any start/end datetime
- **Cross-midnight support**: Make separate calls for before and after midnight, then merge
- **Fresh data**: Always get current price data rather than cached sensor values

#### Cross-Midnight Implementation

When a time range spans midnight (e.g., 23:00 today to 06:00 tomorrow):

```yaml
# Call 1: Start datetime until midnight
service: tibber.get_prices
data:
  start: "{{ start_datetime }}"
  end: "{{ today_midnight }}"
target:
  entity_id: sensor.electricity_price_prognose_*

# Call 2: Midnight until end datetime (next day)
service: tibber.get_prices
data:
  start: "{{ tomorrow_midnight }}"
  end: "{{ end_datetime }}"
target:
  entity_id: sensor.electricity_price_prognose_*

# Merge both result sets
# result = call_1_prices + call_2_prices
```

### Optional

- **Solar Forecast Integration**: For advanced SOC optimization
  - Forecast.Solar integration
  - Tibber solar forecast (if available)
  - Solcast integration

## Data Format

### Tibber Price Sensor Structure

The Tibber sensor provides current price and today/tomorrow arrays:

```yaml
sensor.electricity_price_prognose_*:
  state: 0.2866 # Current price EUR/kWh
  attributes:
    today:
      - total: 0.2696 # Hour 0
      - total: 0.2632 # Hour 1
      # ... 24 entries
    tomorrow:
      # Available after ~13:00, same structure
    unit_of_measurement: EUR/kWh
```

**Limitation**: The sensor's `today` attribute only returns prices up to midnight. For overnight windows, we use `tibber.get_prices` service instead.

### tibber.get_prices Response Format

The service returns prices for the requested time range:

```yaml
prices:
  - start_time: "2024-01-15T23:00:00+01:00"
    total: 0.2432
  - start_time: "2024-01-16T00:00:00+01:00"
    total: 0.2156
  - start_time: "2024-01-16T01:00:00+01:00"
    total: 0.1987
  # ... continues for requested range
```

### Cheapest Hours Calculation (Custom Implementation)

Since we recreate the `cheapest_energy_hours` functionality, the calculation logic:

```jinja
{# Calculate cheapest consecutive N hours from merged price data #}
{% set prices = merged_price_array %}
{% set hours_needed = charging_hours %}

{# Find window with lowest total cost #}
{% set ns = namespace(best_start=0, best_cost=999) %}
{% for i in range(prices | length - hours_needed + 1) %}
  {% set window_cost = prices[i:i+hours_needed] | map(attribute='total') | sum %}
  {% if window_cost < ns.best_cost %}
    {% set ns.best_start = i %}
    {% set ns.best_cost = window_cost %}
  {% endif %}
{% endfor %}

{# Return cheapest window start time #}
{{ prices[ns.best_start].start_time }}
```

## Fallback: Python Integration

If blueprint complexity exceeds YAML/Jinja capabilities, the fallback is a **Home Assistant Custom Integration** (Python):

- **Language**: Python 3.11+
- **Framework**: Home Assistant Integration architecture
- **Package Manager**: pip / uv
- **Testing**: pytest
- **Linting**: Ruff

Scenarios that might require Python integration:

- Complex state machine for multi-phase charging
- Integration with battery management systems requiring custom protocols
- Advanced forecasting algorithms
- Complex cross-midnight price merging logic

## Development Tools

### Package Manager

- **UV**: Fast Python package manager (preferred over pip)
  - Install: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Config: `pyproject.toml`

### Testing & Quality

- **Test Framework**: pytest
- **Test Location**: `tests/` directory with `test_*.py` files
- **Fixtures**: `tests/conftest.py` provides shared YAML loading with `!input` tag support
- **Linting/Formatting**: Ruff
- **YAML Linting**: yamllint
- **Blueprint Testing**: Manual testing in Home Assistant Developer Tools > Template
- **Price Fetching Testing**: Verify `tibber.get_prices` responses in Developer Tools > Services

### Development Commands

```bash
# Install dependencies
uv sync --dev

# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_night_schedule.py

# Lint code
uv run ruff check .

# Format code
uv run ruff format .

# Lint YAML files
uv run yamllint packages/ dashboards/
```

### Version Control

- **Git**: Source control
- **GitHub**: Repository hosting and blueprint distribution

### CI/CD

- **GitHub Actions**: Automated testing and linting on push/PR
  - HACS validation
  - pytest test suite
  - Ruff linting and format checking
  - yamllint YAML validation

## File Structure

```
charge-cheapest/
├── pyproject.toml                           # Python project config (UV + Ruff + pytest)
├── blueprints/
│   └── automation/
│       └── cheapest_battery_charging.yaml   # Main blueprint
├── packages/
│   └── cheapest_battery_charging/
│       └── cheapest_battery_charging.yaml   # HA package with helpers
├── dashboards/
│   └── charge_cheapest_dashboard.yaml       # Lovelace dashboard
├── tests/
│   ├── conftest.py                          # Shared pytest fixtures
│   └── test_*.py                            # pytest test files (12 total)
├── .github/
│   └── workflows/
│       └── hacs.yaml                        # CI/CD pipeline
├── .devcontainer/
│   └── Dockerfile                           # Python 3.12 + UV dev environment
├── agent-os/
│   └── product/
│       ├── mission.md
│       ├── roadmap.md
│       └── tech-stack.md
├── ha-sensor-states.md                      # Reference: Tibber sensor format
└── README.md
```
