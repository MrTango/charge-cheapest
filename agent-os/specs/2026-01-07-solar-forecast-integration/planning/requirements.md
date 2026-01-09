# Solar Forecast Integration - Requirements

## Overview

Integrate solar production forecasts into the battery charging optimization system to calculate optimal morning SOC targets based on expected solar production.

## Gathered Requirements

### Data Source
- **Primary integration:** Forecast.Solar (free API)
- **Future expansion:** Other providers (Solcast, Open-Meteo, Tibber solar) can be added later

### Polling Frequency
- **Frequency:** Every hour
- **Rationale:** Catch updated forecasts throughout the day for more accurate predictions

### SOC Calculation Inputs
1. **Expected solar production (kWh)** - from Forecast.Solar API
2. **Morning consumption pattern (kWh)** - manual input for now (between wake time and solar production start)
3. **Battery capacity headroom** - needed to capture incoming solar

### Configuration Approach
- **Solar system parameters:** Rely on existing Home Assistant sensors (not additional blueprint inputs)
- **Offset adjustment:** Simple +/- kWh offset, configurable in blueprint inputs

### Fallback Behavior
- When solar forecast is unavailable or returns an error: fall back to user's default target SOC configured for night charging

### Sensor Exposure
- **Expose:** Optimal morning SOC as a Home Assistant sensor value
- **Logging levels:** Both basic and detailed, with a switch to toggle between them
  - Basic: "Target SOC: 45% (expected solar: 12 kWh, morning consumption: 5 kWh)"
  - Detailed: Include battery headroom calculation, forecast source, timestamp, etc.

### Calculation Formula
- Simple formula relating expected solar production to battery headroom
- User-configurable +/- kWh offset to tune the calculation

## Out of Scope (v1)

- Automatic adjustment based on weather uncertainty/cloud cover
- Multiple solar array support (east/west facing panels with different forecasts)
- Integration with other forecast providers (Solcast, Open-Meteo) - deferred to later version
- Historical accuracy tracking of forecasts vs actual production

## Technical Context

### Existing Codebase Patterns
- Blueprint location: `/workspace/blueprints/automation/charge_cheapest.yaml`
- Follow existing patterns for: night charging, SOC targets, Tibber price fetching logic

### Integration Points
- Forecast.Solar API for solar production forecasts
- Existing HA sensors for solar system configuration
- Existing battery SOC target mechanisms

## Visual Assets

- Location: `/workspace/agent-os/specs/2026-01-07-solar-forecast-integration/planning/visuals/`
- Status: No visual assets provided

---

*Requirements gathered: 2026-01-07*
