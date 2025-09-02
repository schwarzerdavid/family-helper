"""
Test suite for ConsoleLogger implementation.
Tests structured logging, child loggers, and environment-based filtering.
"""

import json
import os
import sys
from io import StringIO
from unittest.mock import patch
import pytest

from platform_py.implementations.logger import ConsoleLogger


class TestConsoleLogger:
    """Test ConsoleLogger implementation"""

    def test_console_logger_initialization__with_no_base_fields__should_use_defaults(self):
        """Logger should initialize with default base fields"""
        with patch.dict(os.environ, {}, clear=True):
            logger = ConsoleLogger()
            
            assert logger.base_fields["service"] == "unknown"
            assert logger.base_fields["environment"] == "development"

    def test_console_logger_initialization__with_environment_vars__should_use_environment_values(self):
        """Logger should use environment variables for defaults"""
        with patch.dict(os.environ, {"ENVIRONMENT": "production", "NODE_ENV": "staging"}):
            logger = ConsoleLogger()
            
            # ENVIRONMENT takes precedence over NODE_ENV
            assert logger.base_fields["environment"] == "production"

    def test_console_logger_initialization__with_node_env_only__should_use_node_env(self):
        """Logger should use NODE_ENV when ENVIRONMENT is not set"""
        with patch.dict(os.environ, {"NODE_ENV": "staging"}, clear=True):
            logger = ConsoleLogger()
            
            assert logger.base_fields["environment"] == "staging"

    def test_console_logger_initialization__with_custom_base_fields__should_merge_fields(self):
        """Logger should merge custom base fields with defaults"""
        custom_fields = {
            "service": "test-service",
            "version": "1.0.0",
            "custom_field": "custom_value"
        }
        
        logger = ConsoleLogger(custom_fields)
        
        assert logger.base_fields["service"] == "test-service"
        assert logger.base_fields["version"] == "1.0.0"
        assert logger.base_fields["custom_field"] == "custom_value"
        assert "environment" in logger.base_fields

    def test_info_logging__should_output_structured_json_to_stdout(self):
        """Info logs should output structured JSON to stdout"""
        logger = ConsoleLogger({"service": "test-service"})
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            logger.info("Test message", {"user_id": 123})
            
            output = mock_stdout.getvalue().strip()
            log_data = json.loads(output)
            
            assert log_data["level"] == "info"
            assert log_data["msg"] == "Test message"
            assert log_data["service"] == "test-service"
            assert log_data["user_id"] == 123
            assert "timestamp" in log_data

    def test_error_logging__should_output_structured_json_to_stderr(self):
        """Error logs should output structured JSON to stderr"""
        logger = ConsoleLogger({"service": "test-service"})
        
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            logger.error("Error message", {"error_code": 500})
            
            output = mock_stderr.getvalue().strip()
            log_data = json.loads(output)
            
            assert log_data["level"] == "error"
            assert log_data["msg"] == "Error message"
            assert log_data["service"] == "test-service"
            assert log_data["error_code"] == 500

    def test_warn_logging__should_output_structured_json_to_stdout(self):
        """Warning logs should output structured JSON to stdout"""
        logger = ConsoleLogger({"service": "test-service"})
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            logger.warn("Warning message", {"warning_type": "deprecation"})
            
            output = mock_stdout.getvalue().strip()
            log_data = json.loads(output)
            
            assert log_data["level"] == "warn"
            assert log_data["msg"] == "Warning message"
            assert log_data["warning_type"] == "deprecation"

    def test_debug_logging__in_development__should_output_logs(self):
        """Debug logs should output in development environment"""
        logger = ConsoleLogger({"environment": "development"})
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            logger.debug("Debug message", {"debug_info": "test"})
            
            output = mock_stdout.getvalue().strip()
            log_data = json.loads(output)
            
            assert log_data["level"] == "debug"
            assert log_data["msg"] == "Debug message"
            assert log_data["debug_info"] == "test"

    def test_debug_logging__in_production__should_not_output_logs(self):
        """Debug logs should not output in production environment"""
        logger = ConsoleLogger({"environment": "production"})
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            logger.debug("Debug message")
            
            output = mock_stdout.getvalue().strip()
            assert output == ""

    def test_debug_logging__with_debug_log_level__should_output_logs(self):
        """Debug logs should output when LOG_LEVEL=debug regardless of environment"""
        logger = ConsoleLogger({"environment": "production"})
        
        with patch.dict(os.environ, {"LOG_LEVEL": "debug"}):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                logger.debug("Debug message")
                
                output = mock_stdout.getvalue().strip()
                log_data = json.loads(output)
                
                assert log_data["level"] == "debug"
                assert log_data["msg"] == "Debug message"

    def test_with_fields__should_create_child_logger_with_combined_fields(self):
        """with_fields should create child logger with additional context"""
        parent_logger = ConsoleLogger({
            "service": "test-service",
            "version": "1.0.0"
        })
        
        child_logger = parent_logger.with_fields({
            "request_id": "req-123",
            "user_id": 456
        })
        
        # Child should have combined fields
        expected_fields = {
            "service": "test-service",
            "version": "1.0.0",
            "request_id": "req-123", 
            "user_id": 456
        }
        
        for key, value in expected_fields.items():
            assert child_logger.base_fields[key] == value
        
        assert "environment" in child_logger.base_fields

    def test_with_fields__should_override_parent_fields(self):
        """Child logger fields should override parent fields"""
        parent_logger = ConsoleLogger({
            "service": "parent-service",
            "environment": "development"
        })
        
        child_logger = parent_logger.with_fields({
            "service": "child-service",  # Override parent
            "component": "auth"  # New field
        })
        
        assert child_logger.base_fields["service"] == "child-service"
        assert child_logger.base_fields["environment"] == "development"
        assert child_logger.base_fields["component"] == "auth"

    def test_logging__without_metadata__should_work_correctly(self):
        """Logging without metadata should work correctly"""
        logger = ConsoleLogger({"service": "test-service"})
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            logger.info("Simple message")
            
            output = mock_stdout.getvalue().strip()
            log_data = json.loads(output)
            
            assert log_data["level"] == "info"
            assert log_data["msg"] == "Simple message"
            assert log_data["service"] == "test-service"

    def test_logging__with_complex_metadata__should_serialize_correctly(self):
        """Logging with complex metadata should serialize correctly"""
        logger = ConsoleLogger()
        
        complex_meta = {
            "nested": {"key": "value"},
            "list": [1, 2, 3],
            "number": 42,
            "boolean": True,
            "null": None
        }
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            logger.info("Complex message", complex_meta)
            
            output = mock_stdout.getvalue().strip()
            log_data = json.loads(output)
            
            assert log_data["nested"] == {"key": "value"}
            assert log_data["list"] == [1, 2, 3]
            assert log_data["number"] == 42
            assert log_data["boolean"] is True
            assert log_data["null"] is None

    def test_timestamp_format__should_be_iso_utc(self):
        """Timestamps should be in ISO UTC format"""
        logger = ConsoleLogger()
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            logger.info("Test message")
            
            output = mock_stdout.getvalue().strip()
            log_data = json.loads(output)
            
            timestamp = log_data["timestamp"]
            
            # Should end with +00:00 for UTC (Python's isoformat style)
            assert timestamp.endswith("+00:00")
            
            # Should be parseable as ISO format
            from datetime import datetime
            parsed_timestamp = datetime.fromisoformat(timestamp)
            assert parsed_timestamp is not None

    def test_json_output__should_be_compact_format(self):
        """JSON output should use compact format (no spaces)"""
        logger = ConsoleLogger({"service": "test"})
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            logger.info("Test", {"key": "value"})
            
            output = mock_stdout.getvalue().strip()
            
            # Compact JSON should not contain spaces after separators
            assert ", " not in output
            assert ": " not in output
            
            # Should still be valid JSON
            log_data = json.loads(output)
            assert log_data["msg"] == "Test"