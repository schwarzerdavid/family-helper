"""
Pytest configuration and shared test fixtures.
Provides common test setup and utilities for all test modules.
"""

import asyncio
import os
import sys
from typing import Any, Dict
import pytest
from unittest.mock import patch

# Add src to Python path so we can import platform_py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def clean_environment():
    """Fixture that provides a clean environment for each test"""
    with patch.dict(os.environ, {}, clear=True):
        yield


@pytest.fixture
def test_environment():
    """Fixture that provides a test environment with common variables"""
    test_env = {
        "ENVIRONMENT": "test",
        "LOG_LEVEL": "debug",
        "TEST_VAR": "test_value"
    }
    
    with patch.dict(os.environ, test_env):
        yield test_env


@pytest.fixture
def mock_logger():
    """Fixture that provides a mock logger for testing"""
    from unittest.mock import MagicMock
    
    mock = MagicMock()
    mock.base_fields = {"service": "test", "environment": "test"}
    return mock


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_event_envelope():
    """Fixture that provides a sample EventEnvelope for testing"""
    from platform_py.interfaces import EventEnvelope
    
    return EventEnvelope(
        id="test-event-123",
        type="test.event",
        occurred_at="2023-01-01T12:00:00Z",
        payload={"test": "data", "value": 42},
        idempotency_key="test-idempotency-key",
        trace={"traceparent": "test-trace-id"}
    )


@pytest.fixture
def sample_config_values():
    """Fixture that provides sample configuration values for testing"""
    return {
        "STRING_VAL": "test_string",
        "INT_VAL": "42",
        "FLOAT_VAL": "3.14",
        "BOOL_TRUE": "true",
        "BOOL_FALSE": "false",
        "JSON_OBJECT": '{"key": "value", "number": 123}',
        "JSON_ARRAY": '[1, 2, "three"]'
    }


# Helper functions for testing

def assert_log_contains(captured_logs: str, expected_message: str, expected_level: str = None):
    """Helper function to assert that logs contain expected message and level"""
    import json
    
    log_lines = [line for line in captured_logs.strip().split('\n') if line]
    
    found = False
    for line in log_lines:
        try:
            log_data = json.loads(line)
            if expected_message in log_data.get("msg", ""):
                if expected_level is None or log_data.get("level") == expected_level:
                    found = True
                    break
        except json.JSONDecodeError:
            continue
    
    assert found, f"Expected log message '{expected_message}' with level '{expected_level}' not found in logs"


def assert_json_log_structure(log_line: str, expected_fields: Dict[str, Any]):
    """Helper function to assert JSON log structure"""
    import json
    
    log_data = json.loads(log_line)
    
    # Check required fields
    required_fields = ["timestamp", "level", "msg"]
    for field in required_fields:
        assert field in log_data, f"Required field '{field}' missing from log"
    
    # Check expected fields
    for field, expected_value in expected_fields.items():
        assert log_data.get(field) == expected_value, f"Field '{field}' has value '{log_data.get(field)}', expected '{expected_value}'"


# Pytest configuration
def pytest_configure(config):
    """Pytest configuration hook"""
    # Add custom markers
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")


def pytest_collection_modifyitems(config, items):
    """Pytest collection hook to add markers automatically"""
    for item in items:
        # Mark async tests appropriately
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)
        
        # Mark integration tests
        if "integration" in item.nodeid or "end_to_end" in item.name:
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)