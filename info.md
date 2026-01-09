# Charge Cheapest

A complete Home Assistant blueprint and package for automated battery charging during the cheapest electricity hours based on Tibber price data.

## Features

- **Automatic Charging Optimization** - Charges your battery during the cheapest hours
- **Solar-Optimized Mode** - Adjusts charging targets based on solar forecast
- **Comprehensive Dashboard** - Monitor status, prices, and statistics in one place
- **Easy Configuration** - Set up entity IDs via UI without editing YAML
- **Flexible Control** - Manual override, skip next charge, force charge options

## What's Included

- Pre-configured input helpers for all settings
- Template sensors for real-time status
- Binary sensors for automation conditions
- History statistics and utility meters
- Three-tab Lovelace dashboard

## Prerequisites

1. **Tibber Integration** - With price sensor providing today/tomorrow attributes
2. **cheapest-energy-hours Macro** - Install via HACS from TheFes repository
3. **Battery Control Entities** - Switch and SOC sensor for your battery system

## Quick Start

1. Install this package via HACS
2. Copy packages folder to your config/packages/
3. Restart Home Assistant
4. Import the dashboard
5. Configure entity IDs in the Configuration tab

See README for detailed installation instructions.
