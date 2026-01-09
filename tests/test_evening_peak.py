"""
Evening Peak Schedule Input Tests

Tests for Task Group 4: Evening Peak Schedule Inputs
Validates evening peak time inputs for defining expensive periods.
"""


class TestEveningPeakScheduleInputs:
    def test_evening_peak_start_and_end_inputs_exist_with_time_selectors(self, blueprint_inputs):
        """evening_peak_start and evening_peak_end inputs exist with time selectors."""
        inputs = blueprint_inputs
        assert "evening_peak_start" in inputs
        assert "selector" in inputs["evening_peak_start"]
        assert "time" in inputs["evening_peak_start"]["selector"]
        assert inputs["evening_peak_start"]["name"] == "Evening Peak Start Time"

        assert "evening_peak_end" in inputs
        assert "selector" in inputs["evening_peak_end"]
        assert "time" in inputs["evening_peak_end"]["selector"]
        assert inputs["evening_peak_end"]["name"] == "Evening Peak End Time"

    def test_defaults_are_17_00_and_21_00_respectively(self, blueprint_inputs):
        """Defaults are 17:00 and 21:00 respectively."""
        inputs = blueprint_inputs
        assert inputs["evening_peak_start"]["default"] == "17:00:00"
        assert inputs["evening_peak_end"]["default"] == "21:00:00"
