# Spec Requirements: Home Assistant Integration Deployment

## Initial Description

Deployment as Home Assistant integration, with as close as possible to one-click installation and configuration, no manual copying of Python files. A combination with built-in blueprint is acceptable.

## Requirements Discussion

### First Round Questions

**Q1:** I assume the integration should be installable via HACS (Home Assistant Community Store) as the primary distribution method, with optional manual installation via GitHub download. Is that correct, or should we also support other installation methods?
**Answer:** Yes, HACS as primary with GitHub manual installation as fallback.

**Q2:** I'm thinking the integration should provide a config flow (UI-based setup) where users select their Tibber entity and battery entity, with all current blueprint inputs available as options. Should we also support YAML-based configuration for power users, or is config flow sufficient?
**Answer:** Both config flow and YAML configuration should be supported.

**Q3:** I assume the integration will register the automation(s) internally rather than creating visible blueprint-based automations. Is that correct, or would you prefer the integration to create user-visible automations that can be customized?
**Answer:** Internal automation registration is preferred - users should not need to manage visible automations.

**Q4:** For the dashboard, I'm thinking we auto-generate a Lovelace card/view that users can optionally add to their dashboards, rather than auto-registering a dashboard. Should the integration provide a dashboard card, a full dashboard view, or both?
**Answer:** Auto-register a complete dashboard that users can then customize or remove.

**Q5:** I assume the existing Python package structure (with blueprints/, packages/, dashboards/) should be converted to a standard Home Assistant custom integration structure (custom_components/). Is there any existing code we should preserve as-is?
**Answer:** Convert to standard custom_components structure. The core logic (cheapest hours calculation, cross-midnight price fetching) should be preserved and refactored into Python modules.

**Q6:** Is there anything specific that should NOT be included in this integration deployment, or any constraints I should be aware of?
**Answer:** Multi-battery support (roadmap item 11) should not be included in the initial integration - keep it as a future enhancement.

### Existing Code to Reference

**Similar Features Identified:**
- Core logic location: `blueprints/automation/cheapest_battery_charging.yaml` - contains the cheapest hours calculation and cross-midnight price fetching logic
- Package helpers: `packages/cheapest_battery_charging/` - contains input helpers and automations
- Dashboard: `dashboards/charge_cheapest_dashboard.yaml` - existing Lovelace dashboard to convert

### Follow-up Questions

**Follow-up 1:** For entity selection in config flow, which entities should be required vs optional? I'm assuming:
- Battery entity (for SOC monitoring and control) - required
- Tibber price sensor entity - required
- Solar forecast entity - optional

Is this correct?
**Answer:** Yes - the list is correct:
- Battery entity (for SOC monitoring and control)
- Tibber price sensor entity
- Optional: Solar forecast entity

**Follow-up 2:** For the auto-registered dashboard, should it be:
- A "managed" dashboard that the integration updates automatically (user cannot edit)
- A standard dashboard that's auto-generated initially but user fully owns after creation
- Both options available via integration settings

Which approach is preferred?
**Answer:** Standard dashboard - initially auto-generated, user fully owns it. User should also have an option to recreate it (e.g., a button in integration options), but no auto-update or managed mode.

**Follow-up 3:** For YAML configuration, should it support the same options as config flow, or should it have additional power-user options not available in the UI?
**Answer:** Just the same options as config flow but in YAML format (no additional power-user options).

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
N/A

## Requirements Summary

### Functional Requirements

**Installation & Distribution:**
- HACS (Home Assistant Community Store) as primary installation method
- Manual GitHub installation as fallback option
- One-click installation experience with no manual file copying

**Configuration:**
- Config flow (UI-based setup wizard) for user-friendly configuration
- YAML configuration support with same options as config flow
- Required entity selection: Battery entity, Tibber price sensor entity
- Optional entity selection: Solar forecast entity

**Automation Management:**
- Internal automation registration (not user-visible)
- Users interact via integration settings, not automation management
- Preserve core logic: cheapest hours calculation, cross-midnight price fetching, SOC-based charging

**Dashboard:**
- Auto-register a complete Lovelace dashboard on installation
- Dashboard is user-owned after creation (not managed/auto-updated)
- Provide "Recreate Dashboard" button in integration options
- Users can customize or remove the dashboard freely

### Reusability Opportunities

**Existing Code to Refactor:**
- `blueprints/automation/cheapest_battery_charging.yaml` - core calculation logic to convert to Python
- `packages/cheapest_battery_charging/` - helper definitions to incorporate
- `dashboards/charge_cheapest_dashboard.yaml` - dashboard to auto-register

**Backend Patterns:**
- Cross-midnight price fetching logic (tibber.get_prices service calls)
- Cheapest consecutive hours calculation algorithm
- SOC-based charge duration calculation

### Scope Boundaries

**In Scope:**
- HACS-compatible custom integration structure (`custom_components/`)
- Config flow with entity selectors
- YAML configuration support (same options as config flow)
- Internal automation management
- Auto-registered, user-owned dashboard
- Dashboard recreation option in integration settings
- Core features: night charging, day charging, SOC targets, solar forecast integration
- Single battery support

**Out of Scope:**
- Multi-battery support (future enhancement per roadmap item 11)
- Managed/auto-updating dashboard
- Additional YAML-only power-user options
- Blueprint-based user-visible automations

### Technical Considerations

**Integration Structure:**
- Standard Home Assistant custom integration format (`custom_components/tibber_cheapest_charging/`)
- Python 3.11+ compatibility
- Config flow and options flow implementation
- Manifest with HACS compatibility

**Dependencies:**
- Tibber integration (for `tibber.get_prices` service)
- Home Assistant Core (minimum version TBD)
- Optional: Solar forecast integrations (Forecast.Solar, Solcast)

**Testing:**
- pytest for Python modules
- Ruff for linting/formatting
- GitHub Actions CI/CD with HACS validation

**Migration Path:**
- Convert Jinja2 template logic to Python modules
- Preserve algorithm accuracy for cheapest hours calculation
- Maintain cross-midnight price fetching reliability
