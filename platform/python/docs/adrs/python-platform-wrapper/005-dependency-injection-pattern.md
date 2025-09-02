# ADR-005: Dependency Injection Pattern for Stub Services

## Status
Accepted

## Context
The stub implementations need access to logging functionality, but circular dependency issues arise when stub services depend on the main logger that might depend on other services. Several approaches were considered:

1. **Circular Dependencies**: Allow stubs to depend on main services
2. **No Logging in Stubs**: Stubs operate without logging
3. **Internal Logger Creation**: Each stub creates its own logger
4. **Dependency Injection**: Inject logger dependencies with fallbacks

The choice affects testability, debugging, and architectural cleanliness.

## Decision
We will use **dependency injection** with fallback logger creation for all stub services.

## Rationale

### Dependency Injection Benefits:
1. **Testability**: Easy to inject mock loggers for testing
2. **Flexibility**: Can inject different logger implementations
3. **No Circular Dependencies**: Clean dependency graph
4. **Consistent Logging**: All services can share the same logger instance
5. **Optional Dependencies**: Fallback ensures services always work

### Implementation Pattern:
```python
def _create_console_logger() -> Logger:
    """Fallback logger creation for when no logger is injected"""
    return ConsoleLogger({"component": "stub"})

class StubDatabase(Db):
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or _create_console_logger()
        
    async def query(self, sql: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        self.logger.debug("Stub database query executed", {"sql": sql, "params": params})
        return []
```

### Factory Integration:
```python
def create_platform_services():
    logger = ConsoleLogger(base_context)
    
    return PlatformServices(
        logger=logger,
        db=StubDatabase(logger),  # Inject same logger instance
        secrets=StubSecrets(logger),
        # ... other services
    )
```

## Consequences

### Positive:
- **Clean Architecture**: No circular dependencies
- **Testable**: Easy to inject mock dependencies
- **Consistent Logging**: All services can share logger context
- **Optional Injection**: Services work with or without injection
- **Debugging Friendly**: All stub operations are logged with context

### Negative:
- **Slightly More Complex**: Requires dependency injection setup
- **Parameter Overhead**: Each stub constructor needs logger parameter
- **Fallback Management**: Need to maintain fallback logger creation

### Mitigation:
- **Factory Pattern**: Hide injection complexity in factory functions
- **Consistent Interface**: All stubs follow same injection pattern
- **Clear Defaults**: Fallback logger provides sensible defaults

## Design Patterns

### Constructor Injection:
```python
class StubPubSub(PubSub):
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or _create_console_logger()
        self._subscribers: Dict[str, List[Callable]] = {}
```

### Fallback Logger Factory:
```python
def _create_console_logger() -> Logger:
    """Simple console-based logger fallback for when no logger is provided"""
    return ConsoleLogger({"component": "stub"})
```

### Shared Logger Instance:
```python
# Factory ensures all services share the same logger instance
platform = create_platform_services(service_name="my-service")

# All these are the same logger instance:
assert platform.logger is platform.db.logger
assert platform.logger is platform.secrets.logger
assert platform.logger is platform.pubsub.logger
```

## Testing Benefits

### Mock Injection:
```python
def test_stub_database_logs_operations():
    mock_logger = MagicMock()
    db = StubDatabase(logger=mock_logger)
    
    await db.query("SELECT * FROM users")
    
    mock_logger.debug.assert_called_with(
        "Stub database query executed",
        {"sql": "SELECT * FROM users", "params": []}
    )
```

### Independent Testing:
```python
def test_stub_works_without_logger():
    # Should work fine with fallback logger
    db = StubDatabase()  # No logger injected
    result = await db.query("SELECT 1")
    assert result == []
```

## Alternatives Considered

### Circular Dependencies
- **Pros**: Simple, direct dependencies
- **Cons**: Complex dependency resolution, harder testing
- **Rejected**: Creates architectural problems

### No Logging in Stubs
- **Pros**: Simple, no dependencies
- **Cons**: Poor debugging experience, no operation visibility
- **Rejected**: Reduces development and debugging capabilities

### Global Logger Instance
- **Pros**: Simple access, no injection needed
- **Cons**: Global state, harder testing, coupling issues
- **Rejected**: Creates global state dependencies

### Service Locator Pattern
- **Pros**: Flexible service resolution
- **Cons**: Hidden dependencies, harder testing, more complex
- **Rejected**: Over-engineering for simple needs

## Implementation Details

### Fallback Logger Configuration:
- Component field set to "stub" for easy filtering
- Uses same base logger implementation (ConsoleLogger)
- Inherits environment-based debug filtering

### Logger Context Inheritance:
- Injected loggers keep their existing context
- Fallback logger gets basic stub identification
- No context conflicts or overrides

### Memory Management:
- No logger instance caching in stubs
- Factory manages logger lifecycle
- Clean separation of concerns

### Error Handling:
- Logger injection never fails (fallback always available)
- Logger operations are fire-and-forget (no error propagation)
- Stub operations continue even if logging fails

## Performance Considerations
- Minimal overhead from optional parameter checking
- Fallback logger creation only happens when needed
- Shared logger instances reduce memory usage
- Logging operations don't impact stub performance

## Review Date
This decision should be reviewed if:
- Dependency injection becomes too complex
- Performance issues arise from logger injection
- Alternative dependency patterns prove more effective
- Testing requirements change significantly