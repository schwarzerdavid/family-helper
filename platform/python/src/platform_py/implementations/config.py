"""
Environment-based configuration implementation.
Reads configuration values from environment variables with type safety and validation.
"""

import json
import os
from typing import Any, Dict, Optional, Union, TypeVar

from ..interfaces import Config

T = TypeVar('T')


class ConfigError(Exception):
    """Custom error class for configuration-related errors"""
    
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class EnvironmentConfig(Config):
    """
    Environment-based configuration implementation.
    Reads configuration values from environment variables with type safety and validation.
    """
    
    def __init__(self):
        """Initialize configuration with caching"""
        self._cache: Dict[str, Any] = {}
    
    def get(self, key: str, required: bool = False, default: Optional[T] = None) -> Union[str, T]:
        """
        Get configuration value with type safety and default values.
        Supports type conversion for common types (string, number, boolean).
        
        Args:
            key: Environment variable name
            required: Whether the configuration is required
            default: Default value if not found
            
        Returns:
            Configuration value with appropriate type
            
        Raises:
            ConfigError: If required configuration is missing or invalid
        """
        # Check cache first for performance
        if key in self._cache:
            return self._cache[key]
        
        raw_value = os.environ.get(key)
        
        # Handle missing values
        if raw_value is None or raw_value == "":
            if required:
                raise ConfigError(f"Required configuration key '{key}' is missing or empty")
            
            if default is not None:
                self._cache[key] = default
                return default
            
            # Return empty string as fallback
            fallback = ""
            self._cache[key] = fallback
            return fallback
        
        # Convert string value to appropriate type
        converted_value = self._convert_value(raw_value, default)
        self._cache[key] = converted_value
        
        return converted_value
    
    def get_int(self, key: str, required: bool = False, default: Optional[int] = None) -> Optional[int]:
        """Get configuration value as integer"""
        value = self.get(key, required, default)
        if value is None or value == "":
            return None
        
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ConfigError(f"Configuration value '{value}' for key '{key}' cannot be converted to integer")
    
    def get_bool(self, key: str, required: bool = False, default: Optional[bool] = None) -> Optional[bool]:
        """Get configuration value as boolean"""
        value = self.get(key, required, default)
        if value is None or value == "":
            return None
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            lower_value = value.lower()
            if lower_value in ("true", "1", "yes", "on"):
                return True
            elif lower_value in ("false", "0", "no", "off"):
                return False
            else:
                raise ConfigError(f"Configuration value '{value}' for key '{key}' cannot be converted to boolean")
        
        return bool(value)
    
    def get_float(self, key: str, required: bool = False, default: Optional[float] = None) -> Optional[float]:
        """Get configuration value as float"""
        value = self.get(key, required, default)
        if value is None or value == "":
            return None
        
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ConfigError(f"Configuration value '{value}' for key '{key}' cannot be converted to float")
    
    def clear_cache(self) -> None:
        """Clear the internal cache (useful for testing)"""
        self._cache.clear()
    
    def get_keys_with_prefix(self, prefix: str) -> Dict[str, str]:
        """Get all configuration keys that start with a prefix"""
        result = {}
        for key, value in os.environ.items():
            if key.startswith(prefix) and value is not None:
                result[key] = value
        return result
    
    def _convert_value(self, raw_value: str, default_value: Optional[Any] = None) -> Any:
        """
        Convert string environment variable to appropriate type based on default value or common patterns.
        
        Args:
            raw_value: Raw string value from environment
            default_value: Default value to hint at desired type
            
        Returns:
            Converted value with appropriate type
        """
        # If we have a default value, use its type as a hint
        if default_value is not None:
            default_type = type(default_value)
            
            if default_type == int:
                try:
                    return int(raw_value)
                except ValueError:
                    raise ConfigError(f"Configuration value '{raw_value}' cannot be converted to integer")
            
            elif default_type == float:
                try:
                    return float(raw_value)
                except ValueError:
                    raise ConfigError(f"Configuration value '{raw_value}' cannot be converted to float")
            
            elif default_type == bool:
                lower_value = raw_value.lower()
                if lower_value in ("true", "1", "yes", "on"):
                    return True
                elif lower_value in ("false", "0", "no", "off"):
                    return False
                else:
                    raise ConfigError(f"Configuration value '{raw_value}' cannot be converted to boolean")
            
            elif isinstance(default_value, (dict, list)):
                # Assume JSON for complex objects
                try:
                    return json.loads(raw_value)
                except json.JSONDecodeError:
                    raise ConfigError(f"Configuration value '{raw_value}' is not valid JSON")
        
        # Auto-detect common patterns
        
        # Numbers (integers)
        if raw_value.isdigit():
            return int(raw_value)
        
        # Numbers (floats) 
        if raw_value.replace(".", "").replace("-", "").isdigit() and raw_value.count(".") == 1:
            return float(raw_value)
        
        # Booleans
        lower_value = raw_value.lower()
        if lower_value in ("true", "false", "1", "0", "yes", "no", "on", "off"):
            return lower_value in ("true", "1", "yes", "on")
        
        # JSON objects/arrays
        if (raw_value.startswith("{") and raw_value.endswith("}")) or \
           (raw_value.startswith("[") and raw_value.endswith("]")):
            try:
                return json.loads(raw_value)
            except json.JSONDecodeError:
                # If JSON parsing fails, treat as string
                pass
        
        # Default to string
        return raw_value