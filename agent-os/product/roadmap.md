# Product Roadmap

1. [x] **Blueprint Configuration Schema** - Define all input variables for the blueprint including night schedule times, SOC targets, Tibber sensor entity, and battery control entities. Create the basic blueprint YAML structure with input selectors. `S`

2. [x] **Tibber Get Prices Service Integration** - Implement the `tibber.get_prices` service call to fetch hourly price data for a given time range. Handle authentication and response parsing to extract price arrays with timestamps. `S`

3. [x] **Cross-Midnight Price Fetching** - Detect when a requested time range spans midnight and automatically split into two `tibber.get_prices` calls: one from start datetime until midnight, and one from midnight until end datetime the next day. Merge both result sets into a single continuous price array. `M`

4. [x] **Cheapest Hours Calculation Logic** - Recreate the core logic from `cheapest_energy_hours` to find the optimal charging window within a price array. Calculate the consecutive hours with lowest total cost based on required charging duration and price data. `M`

5. [x] **Night Charging Automation** - Create the core automation that triggers battery charging during the calculated cheapest night hours. Implement start/stop actions using configurable battery control entities (switch, script, or service call). `M`

6. [x] **SOC-Based Charge Duration** - Add logic to calculate required charging hours based on current battery SOC, target SOC, and battery capacity/charge rate. Dynamically adjust the hours parameter passed to the cheapest hours calculation. `S`

7. [x] **Winter Day Charging Mode** - Implement secondary daytime charging schedule with separate time window configuration. Add enable/disable toggle for seasonal activation. Target evening peak coverage by charging during daytime price dips. `M`

8. [x] **Evening Peak Configuration** - Add configurable evening peak hours definition (e.g., 17:00-21:00). Calculate required afternoon SOC to cover evening consumption without grid dependency during expensive hours. `S`

9. [x] **Solar Forecast Integration** - Integrate solar production forecast data (from Tibber or Forecast.Solar) to calculate optimal morning SOC target. Reduce overnight charging when significant solar production is expected. `L`

10. [x] **Dynamic Morning SOC Target** - Implement logic that adjusts the night charging target based on expected solar production. Ensure battery has headroom to store harvested solar energy while maintaining minimum coverage for morning consumption. `M`

11. [ ] **Multi-Battery Support** - Extend blueprint to support households with multiple battery systems. Allow configuration of multiple battery entities with individual or coordinated charging schedules. `L`

12. [x] **Two options to use forcast calculation**: Extend the forcast calculation usage to two option, first beeing it used to set the actual target SOC's the second it only being used to recommend the setting for the user, but the user will set the desired value. `M`

> Notes
>
> - Order reflects technical dependencies: configuration first, then price fetching with midnight fix, then calculation logic, then automation
> - Items 1-6 constitute the MVP (night charging with cross-midnight support and basic SOC targeting)
> - Items 7-8 complete the winter mode functionality
> - Items 9-10 add solar intelligence
> - Item 11 is an enhancement for complex setups
> - Each item is independently testable: verify price fetching spans midnight correctly, charging triggers at correct times with expected duration
> - The cross-midnight fix (item 3) is critical and must be implemented before cheapest hours calculation
