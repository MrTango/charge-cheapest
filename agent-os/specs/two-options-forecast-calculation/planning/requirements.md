# Spec Requirements: Two Options to Use Forecast Calculation

## Initial Description
Two options to use forecast calculation

From roadmap item #12: "Extend the forecast calculation usage to two options, first being it used to set the actual target SOC's the second it only being used to recommend the setting for the user, but the user will set the desired value."

## Requirements Discussion

### First Round Questions

**Q1:** I assume the two modes are: (1) "Automatic mode" where the forecast directly sets the target SOC values, and (2) "Recommendation mode" where the forecast suggests values but the user manually confirms/adjusts them. Is that correct, or do you envision a different split?
**Answer:** Two modes confirmed: Automatic mode (forecast sets SOC directly) and Recommendation mode (forecast suggests, user decides). Recommendation mode should be the default.

**Q2:** In recommendation mode, how should the user be notified of the suggested SOC value? I'm thinking either: (a) a sensor entity that displays the recommendation, (b) a persistent notification, or (c) a companion dashboard card. Which approach fits your workflow best?
**Answer:** Sensor is sufficient - no need for notifications when recommendation changes.

**Q3:** Should the mode selection be a one-time blueprint configuration, or should users be able to switch between automatic and recommendation modes at runtime (e.g., via an input_select helper)?
**Answer:** Runtime toggle - users should be able to switch between modes without reconfiguring the blueprint.

**Q4:** In recommendation mode, once the user reviews the suggested SOC, how should they "confirm" or "apply" their desired value? Options include: (a) manually updating an input_number helper, (b) calling a script/service, or (c) simply having a separate "user target SOC" entity that overrides the forecast. What feels most natural?
**Answer:** UI element preferred - an input_number pre-populated with the recommendation that the user can adjust and confirm.

**Q5:** Should both the night charging schedule AND the day charging schedule (winter mode) respect this mode setting, or should they have independent mode configurations?
**Answer:** Both schedules respect the mode - night and day charging both follow the same mode setting.

**Q6:** In recommendation mode, if the user hasn't explicitly set a value, should the system: (a) not charge at all until user confirms, (b) fall back to a configured default SOC, or (c) use the recommended value after a timeout?
**Answer:** Charging still executes - in recommendation mode, the blueprint still charges at cheapest hours but uses the user-defined SOC target values.

**Q7:** Is there anything you specifically want to exclude from this feature's scope?
**Answer:** No specific exclusions mentioned.

### Existing Code to Reference

No similar existing features identified for reference.

### Follow-up Questions

None required - the user's answers were comprehensive and addressed all key aspects of the feature.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
N/A

## Requirements Summary

### Functional Requirements
- Two operating modes for forecast-based SOC targeting:
  - **Automatic mode**: Forecast calculation directly sets target SOC values for charging
  - **Recommendation mode** (default): Forecast calculation suggests values via sensor, user sets desired values via input_number
- Runtime mode switching via a toggle (e.g., input_select or input_boolean) without requiring blueprint reconfiguration
- Recommendation sensor that exposes the forecast-calculated SOC value
- User-adjustable input_number entity for manual SOC target entry in recommendation mode
- Input_number should be pre-populated with the recommended value for user convenience
- Both night charging and day charging (winter mode) schedules respect the same mode setting
- In recommendation mode, charging still executes at cheapest hours using user-defined SOC target values
- Default mode should be Recommendation mode

### Reusability Opportunities
- Existing forecast calculation logic (roadmap items 9-10) will be extended
- Current night/day charging automation structure will be adapted to respect mode setting
- Tibber price integration and cheapest hours calculation remain unchanged

### Scope Boundaries
**In Scope:**
- Mode toggle mechanism (input_select or input_boolean)
- Recommendation sensor entity creation
- User SOC input_number entity creation
- Pre-population of input_number with recommended values
- Modification of charging logic to respect mode setting
- Unified mode setting for both night and day schedules

**Out of Scope:**
- Push notifications when recommendation changes
- Separate mode settings for night vs day charging
- Timeout-based automatic confirmation
- Blocking charging until user confirms in recommendation mode

### Technical Considerations
- Mode selection should be a runtime toggle (input_select or input_boolean helper)
- Sensor entity needed to expose forecast recommendation value
- Input_number entity needed for user to set desired SOC target
- Input_number should auto-update to show current recommendation (pre-population)
- Charging automation must check mode before applying SOC target:
  - Automatic mode: use forecast-calculated value
  - Recommendation mode: use user's input_number value
- Blueprint will need to create or reference these helper entities
- Consider whether helpers are created by blueprint or require manual setup
