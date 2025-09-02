# ADR-004: Automatic Type Conversion for Environment Configuration

## Status
Accepted

## Context
The EnvironmentConfig implementation needs to handle environment variables, which are always strings, but applications need typed values (integers, booleans, JSON objects). Several approaches were considered:

1. **Manual conversion**: Application code handles all type conversion
2. **Explicit typed methods**: Separate methods for each type (get_int, get_bool)
3. **Automatic type detection**: Smart conversion based on value patterns
4. **Type hints with conversion**: Use type annotations to drive conversion

The choice affects developer experience, type safety, and configuration complexity.

## Decision
We will implement **automatic type conversion** with pattern detection, supplemented by explicit typed methods and default value type hints.

## Rationale

### Multi-layered Approach:
1. **Default Type Hints**: Use default value types to guide conversion
2. **Pattern Detection**: Automatic detection for common patterns
3. **Explicit Methods**: Typed methods (get_int, get_bool) for explicit needs
4. **Fallback to String**: String fallback when conversion fails

### Conversion Hierarchy:
```python
# 1. Default value type guides conversion
config.get("PORT", default=3000)  # Returns int(3000)
config.get("DEBUG", default=False)  # Returns bool

# 2. Pattern detection for auto-conversion
config.get("PORT")  # "3000" -> 3000 (int)
config.get("RATE")  # "3.14" -> 3.14 (float) 
config.get("ENABLED")  # "true" -> True (bool)
config.get("CONFIG")  # '{"key": "value"}' -> dict

# 3. Explicit typed methods
config.get_int("PORT")  # Guaranteed int or error
config.get_bool("DEBUG")  # Guaranteed bool or error
```

## Technical Implementation

### Pattern Detection Rules:
- **Integers**: Digits only (including negative)
- **Floats**: Digits with single decimal point
- **Booleans**: true/false/yes/no/on/off/1/0 (case insensitive)
- **JSON**: Strings starting with { or [ and valid JSON

### Type Conversion Priorities:
1. **Default Value Type**: If default provided, use its type
2. **Auto-Detection**: Pattern-based conversion
3. **String Fallback**: Return as string if no conversion matches

### Error Handling:
- **Explicit Methods**: Raise ConfigError on conversion failure
- **Auto-Detection**: Fall back to string on conversion failure
- **Required Values**: Raise ConfigError if missing and required

## Consequences

### Positive:
- **Developer Convenience**: Minimal code for type conversion
- **Type Safety**: Explicit methods provide guaranteed types
- **Flexibility**: Multiple conversion strategies for different needs
- **Intuitive Behavior**: Values look like what they convert to
- **JSON Support**: Native support for complex configuration objects

### Negative:
- **Implicit Behavior**: Auto-conversion may surprise developers
- **Ambiguous Cases**: Some strings might convert unexpectedly
- **Performance Overhead**: Pattern matching for every value

### Mitigation:
- **Comprehensive Tests**: Cover all conversion scenarios
- **Clear Documentation**: Explain conversion rules clearly
- **Explicit Methods**: Provide typed methods for critical config
- **Caching**: Cache converted values to avoid repeated conversion

## Design Patterns

### Configuration with Defaults:
```python
# Type-guided conversion
port = config.get("PORT", default=8080)  # int
debug = config.get("DEBUG", default=False)  # bool
timeout = config.get("TIMEOUT", default=30.0)  # float
```

### Explicit Type Conversion:
```python
# Guaranteed types with error handling
try:
    port = config.get_int("PORT", required=True)
    debug = config.get_bool("DEBUG", default=False)
except ConfigError as e:
    logger.error(f"Configuration error: {e}")
```

### Complex Configuration:
```python
# JSON configuration objects
database_config = config.get("DATABASE_CONFIG", default={
    "host": "localhost",
    "port": 5432,
    "ssl": True
})
# Environment: DATABASE_CONFIG='{"host":"prod.db","port":5432,"ssl":true}'
```

## Alternatives Considered

### Manual Conversion Only
- **Pros**: Explicit, no surprises, full control
- **Cons**: Verbose, repetitive code, error-prone
- **Rejected**: Poor developer experience

### Type Hints with Generic Get
- **Pros**: Modern Python typing approach
- **Cons**: Complex implementation, limited Python version support
- **Rejected**: Too complex for configuration needs

### Strict Typing with Schema
- **Pros**: Full validation, schema documentation
- **Cons**: Over-engineering for environment variables
- **Rejected**: Too heavy for simple configuration

### External Configuration Library
- **Pros**: Battle-tested, feature-rich
- **Cons**: Additional dependency, learning curve
- **Rejected**: Keeps implementation simple and self-contained

## Implementation Details

### Caching Strategy:
- Cache converted values to avoid repeated pattern matching
- Clear cache with `clear_cache()` method for testing
- Memory-efficient with reasonable cache limits

### Error Messages:
- Clear error messages indicating what conversion failed
- Include original value and expected type
- Suggest alternative configuration approaches

### Boolean Conversion:
- Case-insensitive matching
- Multiple representations: true/false, yes/no, on/off, 1/0
- Comprehensive coverage of common boolean representations

### JSON Handling:
- Graceful fallback to string if JSON parsing fails
- Support for both objects {} and arrays []
- Proper error handling for malformed JSON

## Performance Considerations
- Pattern matching overhead acceptable for configuration loading
- Caching prevents repeated conversion costs
- Auto-detection only runs once per configuration key
- Explicit methods bypass pattern detection for performance-critical paths

## Review Date
This decision should be reviewed if:
- Performance issues arise from pattern matching
- Unexpected type conversions cause bugs
- Team feedback indicates confusion about conversion rules
- New configuration requirements don't fit the conversion model