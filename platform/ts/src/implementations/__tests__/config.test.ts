import { EnvironmentConfig, ConfigError } from '../config';

describe('EnvironmentConfig', () => {
  let originalEnv: NodeJS.ProcessEnv;
  let config: EnvironmentConfig;

  beforeEach(() => {
    // Save original environment and create clean config instance
    originalEnv = { ...process.env };
    config = new EnvironmentConfig();
    
    // Clear any test-related env vars
    delete process.env.TEST_STRING;
    delete process.env.TEST_NUMBER;
    delete process.env.TEST_BOOLEAN;
    delete process.env.TEST_JSON;
    delete process.env.REQUIRED_CONFIG;
  });

  afterEach(() => {
    // Restore original environment
    process.env = originalEnv;
  });

  describe('test_string_config__when_env_var_exists__should_return_string_value', () => {
    test('returns environment variable as string when it exists', () => {
      process.env.TEST_STRING = 'hello world';
      
      const value = config.get('TEST_STRING');
      
      expect(value).toBe('hello world');
      expect(typeof value).toBe('string');
    });
  });

  describe('test_string_config__when_env_var_missing_no_default__should_return_empty_string', () => {
    test('returns empty string when environment variable is missing and no default provided', () => {
      const value = config.get('NONEXISTENT_VAR');
      
      expect(value).toBe('');
      expect(typeof value).toBe('string');
    });
  });

  describe('test_string_config__when_env_var_missing_with_default__should_return_default_value', () => {
    test('returns default value when environment variable is missing', () => {
      const value = config.get('NONEXISTENT_VAR', { default: 'fallback value' });
      
      expect(value).toBe('fallback value');
    });
  });

  describe('test_required_config__when_env_var_missing__should_throw_config_error', () => {
    test('throws ConfigError when required environment variable is missing', () => {
      expect(() => {
        config.get('REQUIRED_VAR', { required: true });
      }).toThrow(ConfigError);
      
      expect(() => {
        config.get('REQUIRED_VAR', { required: true });
      }).toThrow("Required configuration key 'REQUIRED_VAR' is missing or empty");
    });
  });

  describe('test_required_config__when_env_var_empty_string__should_throw_config_error', () => {
    test('throws ConfigError when required environment variable is empty string', () => {
      process.env.EMPTY_REQUIRED = '';
      
      expect(() => {
        config.get('EMPTY_REQUIRED', { required: true });
      }).toThrow(ConfigError);
    });
  });

  describe('test_required_config__when_env_var_exists__should_return_value', () => {
    test('returns value when required environment variable exists', () => {
      process.env.REQUIRED_CONFIG = 'important-value';
      
      const value = config.get('REQUIRED_CONFIG', { required: true });
      
      expect(value).toBe('important-value');
    });
  });

  describe('test_number_conversion__when_integer_string__should_return_number', () => {
    test('converts integer string to number when default is number', () => {
      process.env.TEST_NUMBER = '42';
      
      const value = config.get('TEST_NUMBER', { default: 0 });
      
      expect(value).toBe(42);
      expect(typeof value).toBe('number');
    });
  });

  describe('test_number_conversion__when_float_string__should_return_float', () => {
    test('converts float string to number when default is number', () => {
      process.env.TEST_NUMBER = '3.14159';
      
      const value = config.get('TEST_NUMBER', { default: 0.0 });
      
      expect(value).toBe(3.14159);
      expect(typeof value).toBe('number');
    });
  });

  describe('test_number_conversion__when_invalid_number_string__should_throw_config_error', () => {
    test('throws ConfigError when string cannot be converted to number', () => {
      process.env.TEST_NUMBER = 'not-a-number';
      
      expect(() => {
        config.get('TEST_NUMBER', { default: 0 });
      }).toThrow(ConfigError);
      
      expect(() => {
        config.get('TEST_NUMBER', { default: 0 });
      }).toThrow("Configuration value 'not-a-number' cannot be converted to number");
    });
  });

  describe('test_boolean_conversion__when_true_values__should_return_true', () => {
    test('converts various true representations to boolean true', () => {
      const trueValues = ['true', 'TRUE', '1', 'yes', 'YES'];
      
      trueValues.forEach((value, index) => {
        const envKey = `TEST_BOOL_${index}`;
        process.env[envKey] = value;
        
        const result = config.get(envKey, { default: false });
        
        expect(result).toBe(true);
        expect(typeof result).toBe('boolean');
      });
    });
  });

  describe('test_boolean_conversion__when_false_values__should_return_false', () => {
    test('converts various false representations to boolean false', () => {
      const falseValues = ['false', 'FALSE', '0', 'no', 'NO'];
      
      falseValues.forEach((value, index) => {
        const envKey = `TEST_BOOL_FALSE_${index}`;
        process.env[envKey] = value;
        
        const result = config.get(envKey, { default: true });
        
        expect(result).toBe(false);
        expect(typeof result).toBe('boolean');
      });
    });
  });

  describe('test_boolean_conversion__when_invalid_boolean_string__should_throw_config_error', () => {
    test('throws ConfigError when string cannot be converted to boolean', () => {
      process.env.TEST_BOOLEAN = 'maybe';
      
      expect(() => {
        config.get('TEST_BOOLEAN', { default: false });
      }).toThrow(ConfigError);
      
      expect(() => {
        config.get('TEST_BOOLEAN', { default: false });
      }).toThrow("Configuration value 'maybe' cannot be converted to boolean");
    });
  });

  describe('test_json_conversion__when_valid_json_object__should_parse_object', () => {
    test('parses valid JSON object when default is object', () => {
      process.env.TEST_JSON = '{"name": "test", "count": 5, "active": true}';
      
      const value = config.get('TEST_JSON', { default: {} });
      
      expect(value).toEqual({
        name: 'test',
        count: 5,
        active: true
      });
      expect(typeof value).toBe('object');
    });
  });

  describe('test_json_conversion__when_valid_json_array__should_parse_array', () => {
    test('parses valid JSON array when default is object', () => {
      process.env.TEST_JSON = '[1, 2, 3, "four"]';
      
      const value = config.get('TEST_JSON', { default: [] });
      
      expect(value).toEqual([1, 2, 3, 'four']);
      expect(Array.isArray(value)).toBe(true);
    });
  });

  describe('test_json_conversion__when_invalid_json__should_throw_config_error', () => {
    test('throws ConfigError when JSON is malformed', () => {
      process.env.TEST_JSON = '{"invalid": json}';
      
      expect(() => {
        config.get('TEST_JSON', { default: {} });
      }).toThrow(ConfigError);
      
      expect(() => {
        config.get('TEST_JSON', { default: {} });
      }).toThrow("Configuration value '{\"invalid\": json}' is not valid JSON");
    });
  });

  describe('test_auto_type_detection__when_integer_string__should_detect_as_number', () => {
    test('automatically detects and converts integer strings to numbers', () => {
      process.env.AUTO_INT = '123';
      
      const value = config.get<number>('AUTO_INT');
      
      expect(value).toBe(123);
      expect(typeof value).toBe('number');
    });
  });

  describe('test_auto_type_detection__when_float_string__should_detect_as_number', () => {
    test('automatically detects and converts float strings to numbers', () => {
      process.env.AUTO_FLOAT = '45.67';
      
      const value = config.get<number>('AUTO_FLOAT');
      
      expect(value).toBe(45.67);
      expect(typeof value).toBe('number');
    });
  });

  describe('test_auto_type_detection__when_boolean_string__should_detect_as_boolean', () => {
    test('automatically detects and converts boolean strings', () => {
      process.env.AUTO_BOOL_TRUE = 'true';
      process.env.AUTO_BOOL_FALSE = 'false';
      
      const trueValue = config.get<boolean>('AUTO_BOOL_TRUE');
      const falseValue = config.get<boolean>('AUTO_BOOL_FALSE');
      
      expect(trueValue).toBe(true);
      expect(falseValue).toBe(false);
      expect(typeof trueValue).toBe('boolean');
      expect(typeof falseValue).toBe('boolean');
    });
  });

  describe('test_auto_type_detection__when_json_object_string__should_detect_as_object', () => {
    test('automatically detects and parses JSON object strings', () => {
      process.env.AUTO_JSON = '{"key": "value", "number": 42}';
      
      const value = config.get('AUTO_JSON');
      
      expect(value).toEqual({ key: 'value', number: 42 });
      expect(typeof value).toBe('object');
    });
  });

  describe('test_auto_type_detection__when_json_array_string__should_detect_as_array', () => {
    test('automatically detects and parses JSON array strings', () => {
      process.env.AUTO_ARRAY = '["item1", "item2", 123]';
      
      const value = config.get('AUTO_ARRAY');
      
      expect(value).toEqual(['item1', 'item2', 123]);
      expect(Array.isArray(value)).toBe(true);
    });
  });

  describe('test_caching__when_same_key_requested_multiple_times__should_use_cached_value', () => {
    test('caches configuration values and returns same instance on subsequent calls', () => {
      process.env.CACHED_VALUE = '{"expensive": "computation"}';
      
      const firstCall = config.get('CACHED_VALUE');
      const secondCall = config.get('CACHED_VALUE');
      
      expect(firstCall).toBe(secondCall); // Same reference for objects
      expect(firstCall).toEqual({ expensive: 'computation' });
    });
  });

  describe('test_cache_clearing__when_clear_cache_called__should_reload_values', () => {
    test('reloads values from environment after cache is cleared', () => {
      process.env.CHANGEABLE_VALUE = 'initial';
      
      const initialValue = config.get('CHANGEABLE_VALUE');
      expect(initialValue).toBe('initial');
      
      // Change environment value
      process.env.CHANGEABLE_VALUE = 'changed';
      
      // Should still return cached value
      const cachedValue = config.get('CHANGEABLE_VALUE');
      expect(cachedValue).toBe('initial');
      
      // Clear cache and get fresh value
      config.clearCache();
      const freshValue = config.get('CHANGEABLE_VALUE');
      expect(freshValue).toBe('changed');
    });
  });

  describe('test_keys_with_prefix__when_multiple_matching_keys__should_return_all_matches', () => {
    test('returns all environment variables that start with given prefix', () => {
      process.env.MYAPP_DATABASE_URL = 'postgres://localhost';
      process.env.MYAPP_DATABASE_POOL_SIZE = '10';
      process.env.MYAPP_CACHE_TTL = '300';
      process.env.OTHERAPP_CONFIG = 'ignored';
      
      const result = config.getKeysWithPrefix('MYAPP_');
      
      expect(result).toEqual({
        'MYAPP_DATABASE_URL': 'postgres://localhost',
        'MYAPP_DATABASE_POOL_SIZE': '10',
        'MYAPP_CACHE_TTL': '300'
      });
      
      expect(result).not.toHaveProperty('OTHERAPP_CONFIG');
    });
  });

  describe('test_keys_with_prefix__when_no_matching_keys__should_return_empty_object', () => {
    test('returns empty object when no environment variables match prefix', () => {
      const result = config.getKeysWithPrefix('NONEXISTENT_PREFIX_');
      
      expect(result).toEqual({});
      expect(Object.keys(result)).toHaveLength(0);
    });
  });

  describe('test_config_error__when_created__should_have_proper_error_properties', () => {
    test('ConfigError has proper error name and maintains stack trace', () => {
      const error = new ConfigError('Test error message');
      
      expect(error.name).toBe('ConfigError');
      expect(error.message).toBe('Test error message');
      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(ConfigError);
      expect(error.stack).toBeDefined();
    });
  });

  describe('test_type_generic__when_explicitly_typed__should_provide_type_safety', () => {
    test('provides proper TypeScript type inference with generics', () => {
      process.env.TYPED_STRING = 'hello';
      process.env.TYPED_NUMBER = '42';
      process.env.TYPED_BOOLEAN = 'true';
      
      // These should provide proper type inference
      const stringValue: string = config.get<string>('TYPED_STRING');
      const numberValue: number = config.get<number>('TYPED_NUMBER', { default: 0 });
      const boolValue: boolean = config.get<boolean>('TYPED_BOOLEAN', { default: false });
      
      expect(typeof stringValue).toBe('string');
      expect(typeof numberValue).toBe('number');
      expect(typeof boolValue).toBe('boolean');
      
      expect(stringValue).toBe('hello');
      expect(numberValue).toBe(42);
      expect(boolValue).toBe(true);
    });
  });
});