"""
Shared pytest fixtures for Home Assistant blueprint testing.

Provides YAML loading with Home Assistant custom tag support (!input).
"""

from pathlib import Path

import pytest
import yaml


class InputTag:
    """Represents a Home Assistant !input tag reference."""

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"!input {self.name}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, InputTag):
            return self.name == other.name
        return False


def input_constructor(loader: yaml.SafeLoader, node: yaml.Node) -> InputTag:
    """Construct an InputTag from a YAML !input node."""
    value = loader.construct_scalar(node)
    return InputTag(value)


class HAYamlLoader(yaml.SafeLoader):
    """YAML loader with Home Assistant custom tag support."""

    pass


# Register the !input tag handler
HAYamlLoader.add_constructor("!input", input_constructor)


def load_yaml_file(path: Path) -> dict:
    """Load a YAML file with Home Assistant tag support."""
    with open(path) as f:
        return yaml.load(f, Loader=HAYamlLoader)


# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
BLUEPRINT_PATH = PROJECT_ROOT / "blueprints" / "automation" / "charge_cheapest.yaml"
PACKAGE_PATH = PROJECT_ROOT / "packages" / "cheapest_battery_charging" / "cheapest_battery_charging.yaml"
DASHBOARD_PATH = PROJECT_ROOT / "dashboards" / "charge_cheapest.yaml"


@pytest.fixture(scope="session")
def blueprint() -> dict:
    """Load the main blueprint YAML file."""
    return load_yaml_file(BLUEPRINT_PATH)


@pytest.fixture(scope="session")
def blueprint_raw() -> str:
    """Get the raw blueprint YAML content."""
    return BLUEPRINT_PATH.read_text()


@pytest.fixture(scope="session")
def blueprint_inputs(blueprint: dict) -> dict:
    """Get the blueprint inputs section."""
    return blueprint["blueprint"]["input"]


@pytest.fixture(scope="session")
def package() -> dict:
    """Load the package YAML file."""
    return load_yaml_file(PACKAGE_PATH)


@pytest.fixture(scope="session")
def dashboard() -> dict:
    """Load the dashboard YAML file."""
    return load_yaml_file(DASHBOARD_PATH)
