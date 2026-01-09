# Raw Idea: Blueprint Configuration Schema

## Feature Name
Blueprint Configuration Schema

## Description
This is for a Home Assistant blueprint that charges house batteries during cheap energy hours. The blueprint needs a configuration schema that allows users to configure:

- Night schedule (start/end times, target SOC, target time)
- Day/winter schedule (start/end times for winter charging)
- Tibber sensor configuration
- Solar forecast integration settings
- Integration with the cheapest-energy-hours macro

## Context
This feature will enable users to configure the blueprint through Home Assistant's UI with proper validation and structure for all the necessary parameters to optimize battery charging based on energy prices and solar forecasting.
