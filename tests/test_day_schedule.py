"""
Day/Winter Schedule Input Tests

Tests for Task Group 3: Day/Winter Schedule Inputs
Validates day schedule toggle, time inputs, and independent SOC target.
"""


class TestDayWinterScheduleInputs:
    def test_day_schedule_enabled_input_exists_with_boolean_selector(self, blueprint_inputs):
        """day_schedule_enabled input exists with boolean selector and default false."""
        inputs = blueprint_inputs
        assert "day_schedule_enabled" in inputs
        assert "selector" in inputs["day_schedule_enabled"]
        assert "boolean" in inputs["day_schedule_enabled"]["selector"]
        assert inputs["day_schedule_enabled"]["default"] is False
        assert inputs["day_schedule_enabled"]["name"] == "Enable Day Schedule"

    def test_day_start_time_and_day_end_time_inputs_exist_with_correct_defaults(self, blueprint_inputs):
        """day_start_time and day_end_time inputs exist with correct defaults."""
        inputs = blueprint_inputs
        assert "day_start_time" in inputs
        assert "selector" in inputs["day_start_time"]
        assert "time" in inputs["day_start_time"]["selector"]
        assert inputs["day_start_time"]["default"] == "09:00:00"
        assert inputs["day_start_time"]["name"] == "Day Schedule Start Time"

        assert "day_end_time" in inputs
        assert "selector" in inputs["day_end_time"]
        assert "time" in inputs["day_end_time"]["selector"]
        assert inputs["day_end_time"]["default"] == "16:00:00"
        assert inputs["day_end_time"]["name"] == "Day Schedule End Time"

    def test_day_target_soc_input_is_independent_from_night_target_soc(self, blueprint_inputs):
        """day_target_soc input is independent from night_target_soc."""
        inputs = blueprint_inputs
        assert "day_target_soc" in inputs
        assert "selector" in inputs["day_target_soc"]
        assert "number" in inputs["day_target_soc"]["selector"]

        number_selector = inputs["day_target_soc"]["selector"]["number"]
        assert number_selector["min"] == 0
        assert number_selector["max"] == 100
        assert number_selector["step"] == 5
        assert number_selector["unit_of_measurement"] == "%"
        assert number_selector["mode"] == "slider"

        # Default is 50% for day, which is different from night's 60%
        assert inputs["day_target_soc"]["default"] == 50
        assert inputs["day_target_soc"]["name"] == "Day Target SOC"

        # Verify it's a separate input from night_target_soc
        assert "night_target_soc" in inputs
        assert inputs["day_target_soc"]["default"] != inputs["night_target_soc"]["default"]
