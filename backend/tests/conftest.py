import os
os.environ["GROQ_API_KEY"] = "mock_test_key"

from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_emission_factors():
    return {
        "flight_km": 0.15,
        "diet_meat_heavy": 3.0,
        "diet_vegetarian": 1.5,
        "electricity_kwh": 0.4
    }

@pytest.fixture
def mock_calculator():
    calculator = Mock()
    calculator.calculate_flight.return_value = 150.0
    return calculator
