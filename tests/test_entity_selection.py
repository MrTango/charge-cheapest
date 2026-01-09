"""
Entity Selection Input Tests

Tests for Task Group 5: Price Sensor and Battery Control Entity Inputs
Validates entity selectors for price sensor, charging switch, and power input.
"""


class TestEntitySelectionInputs:
    def test_price_sensor_input_uses_entity_selector_with_sensor_domain(self, blueprint_inputs):
        """price_sensor input uses entity selector with domain filter for sensor."""
        inputs = blueprint_inputs
        assert "price_sensor" in inputs
        assert "selector" in inputs["price_sensor"]
        assert "entity" in inputs["price_sensor"]["selector"]
        assert inputs["price_sensor"]["selector"]["entity"]["domain"] == "sensor"
        assert inputs["price_sensor"]["selector"]["entity"]["multiple"] is False
        assert inputs["price_sensor"]["name"] == "Price Sensor"

    def test_battery_charging_switch_input_uses_entity_selector_with_switch_domain(self, blueprint_inputs):
        """battery_charging_switch input uses entity selector with domain filter for switch."""
        inputs = blueprint_inputs
        assert "battery_charging_switch" in inputs
        assert "selector" in inputs["battery_charging_switch"]
        assert "entity" in inputs["battery_charging_switch"]["selector"]
        assert inputs["battery_charging_switch"]["selector"]["entity"]["domain"] == "switch"
        assert inputs["battery_charging_switch"]["name"] == "Battery Charging Switch"

    def test_battery_charging_power_input_uses_entity_selector_with_input_number_domain(self, blueprint_inputs):
        """battery_charging_power input uses entity selector with domain filter for input_number."""
        inputs = blueprint_inputs
        assert "battery_charging_power" in inputs
        assert "selector" in inputs["battery_charging_power"]
        assert "entity" in inputs["battery_charging_power"]["selector"]
        assert inputs["battery_charging_power"]["selector"]["entity"]["domain"] == "input_number"
        assert inputs["battery_charging_power"]["name"] == "Charging Power Setting"

    def test_all_entity_inputs_are_required_no_defaults(self, blueprint_inputs):
        """All entity inputs are required (no defaults)."""
        inputs = blueprint_inputs
        # Entity inputs should not have defaults since they are required
        assert inputs["price_sensor"].get("default") is None
        assert inputs["battery_charging_switch"].get("default") is None
        assert inputs["battery_charging_power"].get("default") is None
