"""
Blueprint Schema Extension Tests

Tests for Task Group 3: Blueprint Schema Extension
Validates new inputs for night charging automation including:
- Battery SOC sensor entity input
- Charging configuration inputs (target_soc, duration, trigger_time)
- Failure behavior configuration
- Notification toggle inputs
"""


class TestBlueprintSchemaExtension:
    def test_yaml_structure_is_valid_and_parseable(self, blueprint):
        """YAML structure is valid and parseable."""
        assert blueprint is not None
        assert "blueprint" in blueprint
        assert "input" in blueprint["blueprint"]
        assert blueprint["blueprint"]["domain"] == "automation"

    def test_entity_selectors_have_correct_domains(self, blueprint_inputs):
        """Entity selectors have correct domains."""
        inputs = blueprint_inputs
        # Price sensor should be sensor domain
        assert "price_sensor" in inputs
        assert inputs["price_sensor"]["selector"]["entity"]["domain"] == "sensor"

        # Battery charging switch should be switch domain
        assert "battery_charging_switch" in inputs
        assert inputs["battery_charging_switch"]["selector"]["entity"]["domain"] == "switch"

        # Battery SOC sensor should be sensor domain
        assert "battery_soc_sensor" in inputs
        assert inputs["battery_soc_sensor"]["selector"]["entity"]["domain"] == "sensor"

    def test_notification_toggle_inputs_are_boolean_with_true_defaults(self, blueprint_inputs):
        """Notification toggle inputs are boolean with true defaults."""
        inputs = blueprint_inputs
        notification_inputs = [
            "notify_charging_scheduled",
            "notify_charging_started",
            "notify_charging_completed",
            "notify_charging_skipped",
            "notify_charging_error",
        ]

        for input_name in notification_inputs:
            assert input_name in inputs
            assert "boolean" in inputs[input_name]["selector"]
            assert inputs[input_name]["default"] is True

    def test_number_selectors_have_valid_ranges(self, blueprint_inputs):
        """Number selectors have valid ranges."""
        inputs = blueprint_inputs
        # target_soc: 0-100% range
        assert "target_soc" in inputs
        assert inputs["target_soc"]["selector"]["number"]["min"] == 0
        assert inputs["target_soc"]["selector"]["number"]["max"] == 100
        assert "step" in inputs["target_soc"]["selector"]["number"]

        # charging_duration_hours: 0.5-8 range
        assert "charging_duration_hours" in inputs
        assert inputs["charging_duration_hours"]["selector"]["number"]["min"] == 0.5
        assert inputs["charging_duration_hours"]["selector"]["number"]["max"] == 8
        assert inputs["charging_duration_hours"]["selector"]["number"]["step"] == 0.5

    def test_failure_behavior_has_valid_dropdown_options(self, blueprint_inputs):
        """Failure behavior has valid dropdown options."""
        inputs = blueprint_inputs
        assert "failure_behavior" in inputs
        assert "select" in inputs["failure_behavior"]["selector"]

        options = inputs["failure_behavior"]["selector"]["select"]["options"]
        assert "skip_charging" in options
        assert "use_default_window" in options
        assert "charge_immediately" in options
        assert inputs["failure_behavior"]["default"] == "skip_charging"
