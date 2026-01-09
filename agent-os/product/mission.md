# Product Mission

## Pitch

**Tibber Cheapest Hours Battery Blueprint** is a Home Assistant Blueprint that helps homeowners with battery storage systems optimize their energy costs by automatically charging house batteries during the cheapest electricity hours, with intelligent scheduling that adapts to seasonal solar production patterns.

## Users

### Primary Customers

- **Home Assistant Users with Battery Storage**: Homeowners who have invested in home battery systems (e.g., Tesla Powerwall, Sonnen, Huawei Luna) and want to maximize ROI through smart charging
- **Dynamic Energy Tariff Subscribers**: Users of Tibber, Nordpool, or similar dynamic pricing providers who want to leverage price fluctuations
- **Solar Panel Owners**: Users with PV systems who need coordinated battery management between solar harvesting and grid charging

### User Personas

**Energy-Conscious Homeowner** (35-55)

- **Role:** Homeowner with solar panels and battery storage
- **Context:** Has invested significantly in home energy infrastructure and wants to minimize electricity bills while maximizing self-consumption
- **Pain Points:** Manual monitoring of energy prices is tedious; missing cheap charging windows; battery full before solar production peaks; high evening electricity costs in winter
- **Goals:** Automated, intelligent battery charging; minimal manual intervention; measurable cost savings

**Smart Home Enthusiast** (25-45)

- **Role:** Tech-savvy Home Assistant power user
- **Context:** Enjoys optimizing home automation and has advanced HA setup with multiple integrations
- **Pain Points:** Existing solutions are fragmented; hard to combine price data with solar forecasts; complex YAML configurations
- **Goals:** Clean, maintainable blueprint; easy configuration through UI; integration with existing energy monitoring

## The Problem

### Expensive Evening Energy in Winter

Homeowners with battery storage face a recurring challenge: during winter months, solar production is insufficient to cover evening peak consumption (typically 17:00-21:00), which coincides with the highest electricity prices. Without intelligent charging, batteries either:

1. Remain empty after depleting daytime solar reserves
2. Charge at expensive peak rates
3. Charge overnight but deplete before evening peaks

**Our Solution:** A dual-schedule charging strategy that:

- Charges overnight during the absolute cheapest hours to ensure morning coverage
- Optionally charges during daytime lulls (winter mode) when prices drop, specifically targeting evening peak coverage
- Considers solar forecasts to avoid over-charging before peak production hours

### Suboptimal Morning Battery Levels

Charging to 100% overnight wastes potential solar energy that could be harvested the next morning. Conversely, charging too little leaves the household exposed to morning peak prices.

**Our Solution:** Configurable target SOC (State of Charge) with time-of-completion targets, allowing users to specify "reach 60% by 07:00" rather than blindly charging to full capacity.

### Tibber Price Data Limitation Across Midnight

The existing `cheapest_energy_hours` blueprint has a critical limitation when used with Tibber price data. The Tibber sensor (e.g., `sensor.electricity_price_prognose_laaver_weg_2`) only returns today's prices and cuts off everything after midnight. When the charging window spans midnight (e.g., 23:00-06:00), the blueprint cannot find the cheapest hours in the next day's time range.

**Our Solution:** Rather than using the `cheapest_energy_hours` blueprint directly, we recreate its functionality with a fix for the `tibber.get_prices` service call. When a time range extends beyond midnight:

1. Call `tibber.get_prices` from start datetime until midnight (23:59:59)
2. Call `tibber.get_prices` from midnight (00:00:00) until end datetime the next day
3. Merge both result sets into a single continuous price array
4. Calculate cheapest hours from the merged data

This ensures accurate cheapest-hour detection for overnight charging windows.

## Differentiators

### Cross-Midnight Price Support

Unlike the standard `cheapest_energy_hours` blueprint which fails when time ranges span midnight, our implementation correctly handles overnight windows by making multiple `tibber.get_prices` calls and merging results. This is essential for overnight battery charging scenarios (e.g., 23:00-06:00) where the cheapest hours often fall after midnight.

This results in reliable overnight charging automation that actually works for typical battery charging scenarios.

### Seasonal Awareness

Unlike simple "charge at cheapest hours" solutions, this blueprint understands that winter and summer have fundamentally different charging requirements. The dual-schedule approach (night + optional day) addresses the winter evening peak problem that single-schedule solutions ignore.

This results in 15-30% additional savings during winter months compared to night-only charging strategies.

### Solar Production Integration

By incorporating solar forecast data, the blueprint calculates optimal morning SOC targets. This prevents the common mistake of fully charging batteries overnight only to have excess solar production go to waste (or export at low feed-in rates).

This results in maximized self-consumption ratios and reduced grid dependency.

### Custom Implementation with Bug Fix

By recreating the `cheapest_energy_hours` functionality rather than depending on the external blueprint, we have full control over the implementation and can fix the midnight cutoff issue. This approach provides the same price calculation logic while ensuring reliable operation for all time windows.

This results in reliable, maintainable automation that works correctly for overnight charging scenarios.

## Key Features

### Core Features

- **Night Charging Schedule**: Configure a time window (e.g., 23:00-06:00) during which the blueprint identifies the cheapest consecutive hours to charge the battery to a target SOC by a specified time
- **Cross-Midnight Price Fetching**: Automatically detect when time ranges span midnight and make multiple `tibber.get_prices` calls, merging results for accurate cheapest-hour calculation
- **Configurable SOC Targets**: Set desired battery charge levels with completion deadlines rather than duration-based charging
- **Tibber Price Integration**: Direct integration with Tibber's `tibber.get_prices` service for reliable price data retrieval across day boundaries

### Seasonal Features

- **Winter Day Charging Mode**: Enable a secondary charging window during daytime hours to accumulate charge for expensive evening peaks when solar production is insufficient
- **Schedule Toggle**: Easily enable/disable day charging based on season or manual preference
- **Evening Peak Protection**: Configurable evening hours definition to ensure battery reserves cover the most expensive consumption period

### Advanced Features

- **Solar Forecast Integration**: Use Tibber or third-party solar forecasts to calculate optimal morning SOC (leaving headroom for solar harvesting)
- **Dynamic Charge Calculation**: Estimate required charging duration based on current SOC, target SOC, and charger capacity
- **Price Data Merging**: Intelligent handling of price data from multiple API calls to create seamless price arrays spanning multiple days
