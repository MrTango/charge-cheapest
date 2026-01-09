"""
Night Schedule Input Tests

Tests for Task Group 2: Night Schedule Inputs
Validates night schedule time inputs and SOC target configuration.
"""


class TestNightScheduleInputs:
    def test_night_start_time_input_exists_with_time_selector_and_default(self, blueprint_inputs):
        """night_start_time input exists with time selector and default 23:00."""
        inputs = blueprint_inputs
        assert "night_start_time" in inputs
        assert "selector" in inputs["night_start_time"]
        assert "time" in inputs["night_start_time"]["selector"]
        assert inputs["night_start_time"]["default"] == "23:00:00"
        assert inputs["night_start_time"]["name"] == "Night Schedule Start Time"

    def test_night_end_time_input_exists_with_time_selector_and_default(self, blueprint_inputs):
        """night_end_time input exists with time selector and default 06:00."""
        inputs = blueprint_inputs
        assert "night_end_time" in inputs
        assert "selector" in inputs["night_end_time"]
        assert "time" in inputs["night_end_time"]["selector"]
        assert inputs["night_end_time"]["default"] == "06:00:00"
        assert inputs["night_end_time"]["name"] == "Night Schedule End Time"

    def test_night_target_soc_input_with_number_selector(self, blueprint_inputs):
        """night_target_soc input exists with number selector (0-100, default 60, step 5)."""
        inputs = blueprint_inputs
        assert "night_target_soc" in inputs
        assert "selector" in inputs["night_target_soc"]
        assert "number" in inputs["night_target_soc"]["selector"]

        number_selector = inputs["night_target_soc"]["selector"]["number"]
        assert number_selector["min"] == 0
        assert number_selector["max"] == 100
        assert number_selector["step"] == 5
        assert number_selector["unit_of_measurement"] == "%"
        assert number_selector["mode"] == "slider"

        assert inputs["night_target_soc"]["default"] == 60
        assert inputs["night_target_soc"]["name"] == "Night Target SOC"
