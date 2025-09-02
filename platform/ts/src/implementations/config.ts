import { Config } from '../interfaces';

/**
 * Environment-based configuration implementation.
 * Reads configuration values from environment variables with type safety and validation.
 */
export class EnvironmentConfig implements Config {
  private cache = new Map<string, unknown>();

  /**
   * Get configuration value with type safety and default values.
   * Supports type conversion for common types (string, number, boolean).
   */
  get<T = string>(key: string, opts: { required?: boolean; default?: T } = {}): T {
    // Check cache first for performance
    if (this.cache.has(key)) {
      return this.cache.get(key) as T;
    }

    const rawValue = process.env[key];
    
    // Handle missing values
    if (rawValue === undefined || rawValue === '') {
      if (opts.required === true) {
        throw new ConfigError(`Required configuration key '${key}' is missing or empty`);
      }
      
      if (opts.default !== undefined) {
        this.cache.set(key, opts.default);
        return opts.default;
      }
      
      // Return empty string as fallback for string type
      const fallback = '' as T;
      this.cache.set(key, fallback);
      return fallback;
    }

    // Convert string value to appropriate type
    const convertedValue = this.convertValue<T>(rawValue, opts.default);
    this.cache.set(key, convertedValue);
    
    return convertedValue;
  }

  /**
   * Clear the internal cache (useful for testing)
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Get all configuration keys that start with a prefix
   */
  getKeysWithPrefix(prefix: string): Record<string, string> {
    const result: Record<string, string> = {};
    
    for (const [key, value] of Object.entries(process.env)) {
      if (key.startsWith(prefix) && value !== undefined) {
        result[key] = value;
      }
    }
    
    return result;
  }

  /**
   * Convert string environment variable to appropriate type based on default value or common patterns
   */
  private convertValue<T>(rawValue: string, defaultValue?: T): T {
    // If we have a default value, use its type as a hint
    if (defaultValue !== undefined) {
      const defaultType = typeof defaultValue;
      
      switch (defaultType) {
        case 'number':
          const numValue = Number(rawValue);
          if (isNaN(numValue)) {
            throw new ConfigError(`Configuration value '${rawValue}' cannot be converted to number`);
          }
          return numValue as T;
          
        case 'boolean':
          const lowerValue = rawValue.toLowerCase();
          if (lowerValue === 'true' || lowerValue === '1' || lowerValue === 'yes') {
            return true as T;
          } else if (lowerValue === 'false' || lowerValue === '0' || lowerValue === 'no') {
            return false as T;
          } else {
            throw new ConfigError(`Configuration value '${rawValue}' cannot be converted to boolean`);
          }
          
        case 'object':
          // Assume JSON for objects
          try {
            return JSON.parse(rawValue) as T;
          } catch (error) {
            throw new ConfigError(`Configuration value '${rawValue}' is not valid JSON`);
          }
      }
    }

    // Auto-detect common patterns
    
    // Numbers (integers and floats)
    if (/^\d+$/.test(rawValue)) {
      return parseInt(rawValue, 10) as T;
    }
    
    if (/^\d+\.\d+$/.test(rawValue)) {
      return parseFloat(rawValue) as T;
    }
    
    // Booleans
    const lowerValue = rawValue.toLowerCase();
    if (['true', 'false', '1', '0', 'yes', 'no'].includes(lowerValue)) {
      return (lowerValue === 'true' || lowerValue === '1' || lowerValue === 'yes') as T;
    }
    
    // JSON objects/arrays
    if ((rawValue.startsWith('{') && rawValue.endsWith('}')) || 
        (rawValue.startsWith('[') && rawValue.endsWith(']'))) {
      try {
        return JSON.parse(rawValue) as T;
      } catch {
        // If JSON parsing fails, treat as string
      }
    }
    
    // Default to string
    return rawValue as T;
  }
}

/**
 * Custom error class for configuration-related errors
 */
export class ConfigError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ConfigError';
    
    // Maintain proper stack trace for where our error was thrown (only available on V8)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ConfigError);
    }
  }
}