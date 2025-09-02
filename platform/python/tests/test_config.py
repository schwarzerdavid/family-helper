"""
Test suite for EnvironmentConfig implementation.
Tests configuration loading, type conversion, validation, and caching.
"""

import json
import os
from unittest.mock import patch
import pytest

from platform_py.implementations.config import EnvironmentConfig, ConfigError


class TestEnvironmentConfigBasicOperations:
    """Test basic configuration operations"""

    def test_get__with_existing_string_value__should_return_value(self):
        """Get should return string values from environment"""
        with patch.dict(os.environ, {"TEST_KEY": "test_value"}):
            config = EnvironmentConfig()
            
            result = config.get("TEST_KEY")
            
            assert result == "test_value"

    def test_get__with_missing_key_not_required__should_return_empty_string(self):
        """Get should return empty string for missing non-required keys"""
        with patch.dict(os.environ, {}, clear=True):
            config = EnvironmentConfig()
            
            result = config.get("MISSING_KEY", required=False)
            
            assert result == ""

    def test_get__with_missing_key_required__should_raise_config_error(self):
        """Get should raise ConfigError for missing required keys"""
        with patch.dict(os.environ, {}, clear=True):
            config = EnvironmentConfig()
            
            with pytest.raises(ConfigError) as exc_info:
                config.get("MISSING_KEY", required=True)
            
            assert "Required configuration key 'MISSING_KEY' is missing or empty" in str(exc_info.value)

    def test_get__with_empty_string_required__should_raise_config_error(self):
        """Get should raise ConfigError for empty required values"""
        with patch.dict(os.environ, {"EMPTY_KEY": ""}):
            config = EnvironmentConfig()
            
            with pytest.raises(ConfigError) as exc_info:
                config.get("EMPTY_KEY", required=True)
            
            assert "Required configuration key 'EMPTY_KEY' is missing or empty" in str(exc_info.value)

    def test_get__with_default_value__should_return_default_when_missing(self):
        """Get should return default value when key is missing"""
        with patch.dict(os.environ, {}, clear=True):
            config = EnvironmentConfig()
            
            result = config.get("MISSING_KEY", default="default_value")
            
            assert result == "default_value"

    def test_get__with_default_value_and_existing_key__should_return_env_value(self):
        """Get should return environment value even when default is provided"""
        with patch.dict(os.environ, {"TEST_KEY": "env_value"}):
            config = EnvironmentConfig()
            
            result = config.get("TEST_KEY", default="default_value")
            
            assert result == "env_value"


class TestEnvironmentConfigTypedGetters:
    """Test typed getter methods"""

    def test_get_int__with_valid_integer__should_return_int(self):
        """get_int should convert valid integer strings"""
        with patch.dict(os.environ, {"INT_KEY": "42"}):
            config = EnvironmentConfig()
            
            result = config.get_int("INT_KEY")
            
            assert result == 42
            assert isinstance(result, int)

    def test_get_int__with_invalid_integer__should_raise_config_error(self):
        """get_int should raise ConfigError for invalid integers"""
        with patch.dict(os.environ, {"INVALID_INT": "not_a_number"}):
            config = EnvironmentConfig()
            
            with pytest.raises(ConfigError) as exc_info:
                config.get_int("INVALID_INT")
            
            assert "cannot be converted to integer" in str(exc_info.value)

    def test_get_int__with_missing_key__should_return_none(self):
        """get_int should return None for missing keys"""
        with patch.dict(os.environ, {}, clear=True):
            config = EnvironmentConfig()
            
            result = config.get_int("MISSING_INT")
            
            assert result is None

    def test_get_int__with_default_value__should_return_default_when_missing(self):
        """get_int should return default value when key is missing"""
        with patch.dict(os.environ, {}, clear=True):
            config = EnvironmentConfig()
            
            result = config.get_int("MISSING_INT", default=100)
            
            assert result == 100

    def test_get_bool__with_true_values__should_return_true(self):
        """get_bool should return True for various true representations"""
        true_values = ["true", "True", "TRUE", "1", "yes", "YES", "on", "ON"]
        
        for true_val in true_values:
            with patch.dict(os.environ, {"BOOL_KEY": true_val}):
                config = EnvironmentConfig()
                
                result = config.get_bool("BOOL_KEY")
                
                assert result is True, f"Failed for value: {true_val}"

    def test_get_bool__with_false_values__should_return_false(self):
        """get_bool should return False for various false representations"""
        false_values = ["false", "False", "FALSE", "0", "no", "NO", "off", "OFF"]
        
        for false_val in false_values:
            with patch.dict(os.environ, {"BOOL_KEY": false_val}):
                config = EnvironmentConfig()
                
                result = config.get_bool("BOOL_KEY")
                
                assert result is False, f"Failed for value: {false_val}"

    def test_get_bool__with_invalid_boolean__should_raise_config_error(self):
        """get_bool should raise ConfigError for invalid boolean values"""
        with patch.dict(os.environ, {"INVALID_BOOL": "maybe"}):
            config = EnvironmentConfig()
            
            with pytest.raises(ConfigError) as exc_info:
                config.get_bool("INVALID_BOOL")
            
            assert "cannot be converted to boolean" in str(exc_info.value)

    def test_get_bool__with_boolean_default__should_work_correctly(self):
        """get_bool should handle boolean default values correctly"""
        with patch.dict(os.environ, {}, clear=True):
            config = EnvironmentConfig()
            
            result_true = config.get_bool("MISSING_BOOL_TRUE", default=True)
            result_false = config.get_bool("MISSING_BOOL_FALSE", default=False)
            
            assert result_true is True
            assert result_false is False

    def test_get_float__with_valid_float__should_return_float(self):
        """get_float should convert valid float strings"""
        with patch.dict(os.environ, {"FLOAT_KEY": "3.14"}):
            config = EnvironmentConfig()
            
            result = config.get_float("FLOAT_KEY")
            
            assert result == 3.14
            assert isinstance(result, float)

    def test_get_float__with_integer_string__should_return_float(self):
        """get_float should convert integer strings to float"""
        with patch.dict(os.environ, {"INT_AS_FLOAT": "42"}):
            config = EnvironmentConfig()
            
            result = config.get_float("INT_AS_FLOAT")
            
            assert result == 42.0
            assert isinstance(result, float)

    def test_get_float__with_invalid_float__should_raise_config_error(self):
        """get_float should raise ConfigError for invalid floats"""
        with patch.dict(os.environ, {"INVALID_FLOAT": "not_a_number"}):
            config = EnvironmentConfig()
            
            with pytest.raises(ConfigError) as exc_info:
                config.get_float("INVALID_FLOAT")
            
            assert "cannot be converted to float" in str(exc_info.value)


class TestEnvironmentConfigTypeConversion:
    """Test automatic type conversion functionality"""

    def test_auto_conversion__with_integer_string__should_convert_to_int(self):
        """Strings that look like integers should be auto-converted"""
        with patch.dict(os.environ, {"AUTO_INT": "123"}):
            config = EnvironmentConfig()
            
            result = config.get("AUTO_INT")
            
            assert result == 123
            assert isinstance(result, int)

    def test_auto_conversion__with_float_string__should_convert_to_float(self):
        """Strings that look like floats should be auto-converted"""
        with patch.dict(os.environ, {"AUTO_FLOAT": "123.456"}):
            config = EnvironmentConfig()
            
            result = config.get("AUTO_FLOAT")
            
            assert result == 123.456
            assert isinstance(result, float)

    def test_auto_conversion__with_boolean_string__should_convert_to_bool(self):
        """Strings that look like booleans should be auto-converted"""
        with patch.dict(os.environ, {"AUTO_BOOL_TRUE": "true", "AUTO_BOOL_FALSE": "false"}):
            config = EnvironmentConfig()
            
            result_true = config.get("AUTO_BOOL_TRUE")
            result_false = config.get("AUTO_BOOL_FALSE")
            
            assert result_true is True
            assert result_false is False

    def test_auto_conversion__with_json_object__should_convert_to_dict(self):
        """JSON object strings should be auto-converted to dict"""
        json_obj = '{"key": "value", "number": 42}'
        with patch.dict(os.environ, {"AUTO_JSON": json_obj}):
            config = EnvironmentConfig()
            
            result = config.get("AUTO_JSON")
            
            assert result == {"key": "value", "number": 42}
            assert isinstance(result, dict)

    def test_auto_conversion__with_json_array__should_convert_to_list(self):
        """JSON array strings should be auto-converted to list"""
        json_array = '[1, 2, "three", true]'
        with patch.dict(os.environ, {"AUTO_JSON_ARRAY": json_array}):
            config = EnvironmentConfig()
            
            result = config.get("AUTO_JSON_ARRAY")
            
            assert result == [1, 2, "three", True]
            assert isinstance(result, list)

    def test_auto_conversion__with_invalid_json__should_remain_string(self):
        """Invalid JSON should remain as string"""
        invalid_json = '{"invalid": json}'
        with patch.dict(os.environ, {"INVALID_JSON": invalid_json}):
            config = EnvironmentConfig()
            
            result = config.get("INVALID_JSON")
            
            assert result == invalid_json
            assert isinstance(result, str)

    def test_type_conversion_with_defaults__should_respect_default_type(self):
        """Type conversion should be guided by default value type"""
        with patch.dict(os.environ, {"TYPED_INT": "42", "TYPED_FLOAT": "42.0"}):
            config = EnvironmentConfig()
            
            # Default type should guide conversion
            result_int = config.get("TYPED_INT", default=0)
            result_float = config.get("TYPED_FLOAT", default=0.0)
            result_str = config.get("TYPED_INT", default="")
            
            assert isinstance(result_int, int)
            assert isinstance(result_float, float) 
            assert isinstance(result_str, int)  # Auto-detected as int despite string default


class TestEnvironmentConfigCaching:
    """Test configuration value caching functionality"""

    def test_caching__should_cache_converted_values(self):
        """Configuration should cache converted values"""
        with patch.dict(os.environ, {"CACHED_KEY": "42"}):
            config = EnvironmentConfig()
            
            # First call should convert and cache
            result1 = config.get("CACHED_KEY")
            
            # Verify it's cached
            assert "CACHED_KEY" in config._cache
            assert config._cache["CACHED_KEY"] == 42
            
            # Second call should return cached value
            result2 = config.get("CACHED_KEY")
            
            assert result1 == result2
            assert result1 == 42

    def test_clear_cache__should_clear_internal_cache(self):
        """clear_cache should remove all cached values"""
        with patch.dict(os.environ, {"CACHE_TEST": "value"}):
            config = EnvironmentConfig()
            
            # Populate cache
            config.get("CACHE_TEST")
            assert "CACHE_TEST" in config._cache
            
            # Clear cache
            config.clear_cache()
            
            assert len(config._cache) == 0
            assert "CACHE_TEST" not in config._cache


class TestEnvironmentConfigAdvancedFeatures:
    """Test advanced configuration features"""

    def test_get_keys_with_prefix__should_return_matching_keys(self):
        """get_keys_with_prefix should return all keys with specified prefix"""
        env_vars = {
            "APP_NAME": "my-app",
            "APP_VERSION": "1.0.0", 
            "APP_DEBUG": "true",
            "DATABASE_URL": "postgres://...",
            "OTHER_KEY": "value"
        }
        
        with patch.dict(os.environ, env_vars):
            config = EnvironmentConfig()
            
            app_keys = config.get_keys_with_prefix("APP_")
            
            expected_keys = {
                "APP_NAME": "my-app",
                "APP_VERSION": "1.0.0",
                "APP_DEBUG": "true"
            }
            
            assert app_keys == expected_keys

    def test_get_keys_with_prefix__with_no_matching_keys__should_return_empty_dict(self):
        """get_keys_with_prefix should return empty dict when no keys match"""
        with patch.dict(os.environ, {"OTHER_KEY": "value"}):
            config = EnvironmentConfig()
            
            result = config.get_keys_with_prefix("NONEXISTENT_")
            
            assert result == {}

    def test_config_error__should_have_message_attribute(self):
        """ConfigError should store error message"""
        error_message = "Test error message"
        error = ConfigError(error_message)
        
        assert error.message == error_message
        assert str(error) == error_message


class TestEnvironmentConfigEdgeCases:
    """Test edge cases and error conditions"""

    def test_type_conversion__with_negative_numbers__should_work_correctly(self):
        """Type conversion should handle negative numbers"""
        with patch.dict(os.environ, {"NEGATIVE_INT": "-42", "NEGATIVE_FLOAT": "-3.14"}):
            config = EnvironmentConfig()
            
            int_result = config.get_int("NEGATIVE_INT")
            float_result = config.get_float("NEGATIVE_FLOAT")
            
            assert int_result == -42
            assert float_result == -3.14

    def test_boolean_conversion__with_mixed_case__should_work_correctly(self):
        """Boolean conversion should be case-insensitive"""
        with patch.dict(os.environ, {"MIXED_CASE_BOOL": "TrUe"}):
            config = EnvironmentConfig()
            
            result = config.get("MIXED_CASE_BOOL")
            
            assert result is True

    def test_json_conversion__with_nested_objects__should_work_correctly(self):
        """JSON conversion should handle nested objects"""
        nested_json = '{"outer": {"inner": {"value": 42, "list": [1, 2, 3]}}}'
        with patch.dict(os.environ, {"NESTED_JSON": nested_json}):
            config = EnvironmentConfig()
            
            result = config.get("NESTED_JSON")
            
            expected = {"outer": {"inner": {"value": 42, "list": [1, 2, 3]}}}
            assert result == expected

    def test_get_with_zero_as_default__should_handle_correctly(self):
        """Get should handle zero as a valid default value"""
        with patch.dict(os.environ, {}, clear=True):
            config = EnvironmentConfig()
            
            result = config.get("MISSING_KEY", default=0)
            
            assert result == 0