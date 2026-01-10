# Charge Cheapest

A Home Assistant custom integration that automatically charges your battery during the cheapest electricity hours based on Tibber price data.

## Features

- **One-Click Installation** - Install via HACS with automatic setup wizard
- **Night Charging Schedule** - Charge battery during overnight hours (default 23:00-06:00) at the cheapest prices
- **Optional Day Schedule** - Secondary charging window for winter months (default 09:00-16:00)
- **Cross-Midnight Support** - Properly handles overnight windows spanning two calendar days
- **Evening Peak Protection** - Ensure minimum battery level before expensive peak hours
- **Independent SOC Targets** - Configure separate charge targets for night and day schedules
- **Dynamic Duration Calculation** - Automatically calculates charging time based on battery capacity and charging power
- **Failure Handling** - Configurable behavior when price data is unavailable
- **Flexible Notifications** - Toggle notifications for scheduled, started, completed, skipped, and error events
- **Auto-Generated Dashboard** - Dashboard created automatically, fully customizable after setup
- **Config Flow UI** - Easy setup wizard with entity selection and schedule configuration
- **YAML Support** - Optional YAML configuration for advanced users

## Prerequisites

1. **[Tibber Integration](https://www.home-assistant.io/integrations/tibber/)** - Must be configured with a price sensor that provides `today` and `tomorrow` price attributes
2. **[cheapest-energy-hours Macro](https://github.com/TheFes/cheapest-energy-hours)** - Jinja macro by TheFes (install via HACS)
3. **Battery Entities** - Your inverter/battery integration must expose a charging switch and SOC sensor in Home Assistant

## Installation

### Option 1: HACS Installation (Recommended)

The easiest way to install Charge Cheapest is via HACS:

#### Step 1: Install Charge Cheapest Integration

1. Ensure prerequisites are installed (see links above)
2. In HACS, go to **Integrations**
3. Click the three-dot menu and select **Custom repositories**
4. Add this repository URL as an **Integration** category
5. Search for "Tibber Cheapest Charging" and install it
6. Restart Home Assistant

#### Step 2: Configure the Integration

1. Go to **Settings** > **Devices & Services**
2. Click **Add Integration**
3. Search for "Tibber Cheapest Charging"
4. Follow the setup wizard:
   - **Step 1**: Select your battery SOC sensor, charging switch, and Tibber price sensor
   - **Step 2**: Optionally select solar forecast sensor and battery capacity sensor
   - **Step 3**: Configure schedule times and SOC targets
5. Click **Submit** to complete setup

The integration will automatically:
- Create all required helper entities
- Register internal automations
- Create a dashboard in your sidebar

#### Step 3: Customize (Optional)

- **Dashboard**: The auto-generated dashboard is fully yours to customize or delete
- **Options**: Go to the integration settings to modify schedules, targets, or recreate the dashboard
- **YAML**: Advanced users can also configure via `configuration.yaml` (see YAML Configuration below)

### Option 2: Manual Installation (Legacy)

For users who prefer the traditional blueprint approach:

<details>
<summary>Click to expand manual installation steps</summary>

#### Step 1: Copy Packages Folder

Ensure prerequisites are installed first (see links above).

1. Download this repository or clone it
2. Copy the entire `packages/` folder to your Home Assistant `config/` directory
3. Your structure should look like:
   ```
   config/
   ├── packages/
   │   └── cheapest_battery_charging/
   │       └── cheapest_battery_charging.yaml
   ├── configuration.yaml
   └── ...
   ```

#### Step 2: Add Packages Include

Add the following to your `configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

If you already have a `homeassistant:` section, just add the `packages:` line under it.

#### Step 3: Restart Home Assistant

1. Go to **Settings** > **System** > **Restart**
2. Click **Restart** and wait for Home Assistant to reload
3. All helper entities will be created automatically

#### Step 4: Import Dashboard

1. Go to **Settings** > **Dashboards**
2. Click **Add Dashboard** and create a new dashboard (e.g., "Battery Charging")
3. Open the new dashboard
4. Click the three-dot menu in the top right
5. Select **Edit Dashboard**
6. Click the three-dot menu again and select **Raw configuration editor**
7. Delete any existing content
8. Copy and paste the contents of `dashboards/charge_cheapest.yaml`
9. Click **Save** and then **Done**

#### Step 5: Configure Entity IDs

1. Open your new Battery Charging dashboard
2. Navigate to the **Configuration** tab
3. Enter your entity IDs in the configuration section:
   - **Tibber Price Sensor**: e.g., `sensor.electricity_price`
   - **Battery SOC Sensor**: e.g., `sensor.battery_soc`
   - **Battery Charging Switch**: e.g., `switch.battery_charging`
4. The validation indicators will turn green when entities are correctly configured

#### Step 6: Import Blueprint

1. Go to **Settings** > **Automations & Scenes** > **Blueprints**
2. Click **Import Blueprint**
3. Paste this URL:
   ```
   https://github.com/your-username/charge-cheapest/blob/main/blueprints/automation/charge_cheapest.yaml
   ```
4. Click **Preview** and then **Import Blueprint**

#### Step 7: Create Automation from Blueprint

1. Go to **Settings** > **Automations & Scenes** > **Automations**
2. Click **Create Automation** > **Use Blueprint**
3. Select **Charge Cheapest**
4. Configure the automation:
   - Select your **Tibber Price Sensor**
   - Select your **Battery Charging Switch**
   - Select your **Battery SOC Sensor**
   - Select your **Battery Capacity Sensor**
   - Select `input_number.battery_charging_power` for **Charging Power Setting**
   - Adjust schedule times and targets as needed
5. Click **Save**

</details>

## Configuration

### Required Inputs

| Input                   | Description                                 |
| ----------------------- | ------------------------------------------- |
| Tibber Price Sensor     | Sensor with today/tomorrow price attributes |
| Battery Charging Switch | Switch to enable/disable charging           |
| Battery SOC Sensor      | Current state of charge sensor              |
| Battery Capacity Sensor | Maximum capacity sensor                     |
| Charging Power Setting  | Input number for charger wattage            |

### Schedule Inputs

| Input                | Default | Description                           |
| -------------------- | ------- | ------------------------------------- |
| Night Schedule Start | 23:00   | When overnight charging window begins |
| Night Schedule End   | 06:00   | When overnight window ends            |
| Night Target SOC     | 60%     | Target charge level for night         |
| Enable Day Schedule  | false   | Enable secondary daytime window       |
| Day Schedule Start   | 09:00   | When day window begins                |
| Day Schedule End     | 16:00   | When day window ends                  |
| Day Target SOC       | 50%     | Target charge level for day           |
| Evening Peak Start   | 17:00   | When peak period begins               |
| Evening Peak End     | 21:00   | When peak period ends                 |

### Failure Behavior

When tomorrow's prices are unavailable (typically before ~13:00), the blueprint offers three behaviors:

| Option               | Behavior                                       |
| -------------------- | ---------------------------------------------- |
| `skip_charging`      | Do not charge, send notification (default)     |
| `use_default_window` | Use configured default start time and duration |
| `charge_immediately` | Start charging immediately at trigger time     |

### Notification Toggles

All notifications default to enabled:

- Charging scheduled
- Charging started
- Charging completed
- Charging skipped (SOC above threshold)
- Error conditions
- Emergency charging before peak

### YAML Configuration

Advanced users can configure the integration via `configuration.yaml` instead of the UI:

```yaml
tibber_cheapest_charging:
  # Required entities
  battery_soc_sensor: sensor.battery_soc
  battery_charging_switch: switch.battery_charging
  price_sensor: sensor.electricity_price

  # Optional entities
  solar_forecast_sensor: sensor.solar_forecast  # Optional
  battery_capacity_sensor: sensor.battery_capacity  # Optional
  battery_charging_power: input_number.charging_power  # Optional

  # Night schedule
  night_start_time: "23:00"
  night_end_time: "06:00"
  night_target_soc: 60

  # Day schedule (optional)
  day_schedule_enabled: false
  day_start_time: "09:00"
  day_end_time: "16:00"
  day_target_soc: 50

  # Evening peak
  evening_peak_start: "17:00"
  evening_peak_end: "21:00"
  evening_peak_target_soc: 50
```

## Dashboard Features

### Overview Tab

- Real-time charging status
- Current electricity price
- Next charging window
- Battery gauge (when entity configured)
- Control buttons (enable, force charge, skip next)
- Price chart (ApexCharts with fallback to history graph)

### Statistics Tab

- Estimated daily savings
- Charging hours and session counts
- SOC history graph
- Price trend history
- Cost tracking with utility meters

### Configuration Tab

- Entity ID configuration fields
- Validation status indicators
- Solar panel configuration
- Charging power settings
- Manual schedule times

## How It Works

1. **Trigger** - Automation runs at configured trigger time (default 22:30)
2. **Price Check** - Queries Tibber sensor for available price data
3. **Optimal Window** - Uses cheapest-energy-hours macro to find lowest-cost hours
4. **Schedule** - Turns on charging switch during optimal window
5. **Complete** - Turns off charging when target SOC reached or window ends

### Cross-Midnight Handling

For overnight windows (e.g., 23:00-06:00), the macro:

- Detects start time > end time
- Combines today's evening prices with tomorrow's morning prices
- Selects the cheapest consecutive hours across midnight

## Troubleshooting

### Entity Not Found Errors

**Problem:** Dashboard shows "unavailable" or "Error" status.

**Solution:**

1. Navigate to the Configuration tab in the dashboard
2. Verify all entity IDs are entered correctly
3. Check that the entities exist in **Settings** > **Devices & Services** > **Entities**
4. Entity IDs are case-sensitive and must match exactly

### Price Data Unavailable

**Problem:** Prices show as unavailable or charging doesn't schedule.

**Solution:**

1. Verify the Tibber integration is working correctly
2. Tomorrow's prices are typically available after 13:00 CET
3. Check the `binary_sensor.charge_cheapest_prices_available` entity
4. Consider using `use_default_window` failure behavior as a fallback

### Dashboard Import Issues

**Problem:** Dashboard fails to import or shows errors.

**Solution:**

1. Ensure you're using the Raw configuration editor (not the UI editor)
2. Delete all existing content before pasting
3. Check for YAML syntax errors (proper indentation)
4. Verify all required custom cards are installed (ApexCharts is optional)

### Helpers Not Created

**Problem:** Input helpers don't appear after restart.

**Solution:**

1. Verify the packages folder is in the correct location (`config/packages/`)
2. Check that `configuration.yaml` has the packages include
3. Check Home Assistant logs for YAML parsing errors
4. Ensure the YAML file doesn't have syntax errors

### ApexCharts Not Displaying

**Problem:** Price chart shows as empty or with errors.

**Solution:**

1. ApexCharts is optional - the dashboard includes a fallback history graph
2. To install ApexCharts: HACS > Frontend > Search "ApexCharts" > Install
3. Clear browser cache after installing custom cards

### Charging Not Starting

**Problem:** Automation triggers but charging doesn't start.

**Solution:**

1. Check that `input_boolean.charge_cheapest_enabled` is on
2. Verify the battery switch entity is correct and responsive
3. Check if current SOC is already at or above target
4. Review automation trace in **Settings** > **Automations** > (your automation) > **Traces**

## Project Structure

```
charge-cheapest/
├── .github/
│   └── workflows/
│       └── hacs.yaml                       # HACS validation workflow
├── custom_components/
│   └── tibber_cheapest_charging/           # Custom integration
│       ├── __init__.py                     # Integration setup
│       ├── manifest.json                   # HACS metadata
│       ├── config_flow.py                  # Config and options flows
│       ├── coordinator.py                  # DataUpdateCoordinator
│       ├── const.py                        # Constants and defaults
│       ├── sensor.py                       # Sensor platform
│       ├── binary_sensor.py                # Binary sensor platform
│       ├── dashboard.py                    # Dashboard configuration
│       ├── services.yaml                   # Service definitions
│       └── translations/
│           └── en.json                     # English translations
├── blueprints/
│   └── automation/
│       └── charge_cheapest.yaml            # Legacy blueprint
├── dashboards/
│   └── charge_cheapest.yaml                # Lovelace dashboard template
├── packages/
│   └── cheapest_battery_charging/
│       └── cheapest_battery_charging.yaml  # Legacy package with helpers
├── tests/                                  # Test suite
├── hacs.json                               # HACS repository config
├── info.md                                 # HACS store description
├── package.json
└── README.md
```

## Development

### Running Tests

```bash
# Install dependencies
npm install

# Run all tests
npm test

# Run specific test suite
npm run test:night
npm run test:day
npm run test:entity
```

### Test Coverage

The test suite validates:

- YAML syntax and parsing
- Blueprint metadata structure
- Input configurations and defaults
- Entity selector domains
- Number selector ranges
- Boolean defaults
- Select dropdown options

## Entities Reference

The following entities are created automatically when using the custom integration (HACS install) or the legacy package installation.

### Input Helpers Created (Legacy Package Only)

| Entity                                        | Type     | Description                  |
| --------------------------------------------- | -------- | ---------------------------- |
| `input_text.charge_cheapest_price_sensor_id`  | text     | Price sensor entity ID       |
| `input_text.charge_cheapest_soc_sensor_id`    | text     | Battery SOC sensor entity ID |
| `input_text.charge_cheapest_switch_id`        | text     | Battery switch entity ID     |
| `input_text.solar_forecast_storage`           | text     | Solar forecast data storage  |
| `input_number.battery_charging_power`         | number   | Charging power in watts      |
| `input_number.user_soc_target`                | number   | Target SOC percentage        |
| `input_number.solar_panel_azimuth`            | number   | Solar panel azimuth          |
| `input_number.solar_panel_tilt`               | number   | Solar panel tilt             |
| `input_number.solar_peak_power_kwp`           | number   | Solar system peak power      |
| `input_boolean.charge_cheapest_enabled`       | boolean  | Master enable toggle         |
| `input_boolean.charge_cheapest_force_now`     | boolean  | Force charge override        |
| `input_boolean.charge_cheapest_skip_next`     | boolean  | Skip next charge             |
| `input_select.charge_cheapest_mode`           | select   | Charging mode selection      |
| `input_datetime.charge_cheapest_manual_start` | datetime | Manual start time            |
| `input_datetime.charge_cheapest_manual_end`   | datetime | Manual end time              |

### Sensors (Integration and Legacy Package)

| Entity                                   | Description               |
| ---------------------------------------- | ------------------------- |
| `sensor.charge_cheapest_status`          | Current charging state    |
| `sensor.charge_cheapest_next_window`     | Next scheduled window     |
| `sensor.charge_cheapest_current_price`   | Current electricity price |
| `sensor.charge_cheapest_price_range`     | Today's price range       |
| `sensor.charge_cheapest_recommended_soc` | Recommended SOC target    |
| `sensor.charge_cheapest_savings_today`   | Estimated daily savings   |
| `sensor.charge_cheapest_hours_today`     | Hours charged today       |
| `sensor.charge_cheapest_count_today`     | Charge sessions today     |

### Binary Sensors (Integration and Legacy Package)

| Entity                                           | Description             |
| ------------------------------------------------ | ----------------------- |
| `binary_sensor.charge_cheapest_is_charging`      | Currently charging      |
| `binary_sensor.charge_cheapest_is_cheap_hour`    | Current hour is cheap   |
| `binary_sensor.charge_cheapest_prices_available` | Tomorrow data available |
| `binary_sensor.charge_cheapest_ready`            | All entities configured |

### Utility Meters (Legacy Package Only)

| Entity                                       | Description           |
| -------------------------------------------- | --------------------- |
| `utility_meter.charge_cheapest_cost_daily`   | Daily cost tracking   |
| `utility_meter.charge_cheapest_cost_monthly` | Monthly cost tracking |

## License

ISC

## Credits

- [cheapest-energy-hours macro](https://github.com/TheFes/cheapest-energy-hours) by TheFes
- [Tibber integration](https://www.home-assistant.io/integrations/tibber/) for Home Assistant
