# ADR-005: Dependency Injection Pattern for Platform Services

**Status:** Accepted  
**Date:** 2025-09-02  
**Deciders:** David Schwarzer, Claude  

## Context

During Phase 0 implementation, stub services needed logging capabilities for debugging and development visibility. The initial approach had stub services calling `console.log` directly, creating a circular dependency problem when the stub services were used by the logger itself.

Three approaches were considered:
1. **Dependency Injection**: Pass logger instance to stub constructors
2. **Service Locator**: Global registry for platform services
3. **Direct Console Usage**: Keep simple console.log calls throughout

The circular dependency issue arose because:
- Logger implementation might use other platform services (e.g., config, secrets)
- Those services used console.log directly 
- This created inconsistent logging approaches and potential circular references

## Decision

We decided to implement a **clean dependency injection pattern** for platform services with these characteristics:

1. **Constructor Injection**: All stub services accept optional logger parameter
   ```typescript
   constructor(logger?: Logger) {
     this.logger = logger || createConsoleLogger();
   }
   ```

2. **Fallback Pattern**: When no logger provided, create console-based fallback
   ```typescript
   const createConsoleLogger = (): Logger => ({
     info: (msg, meta) => console.log(JSON.stringify({...})),
     // ... other methods
   });
   ```

3. **Consistent Interface**: Always call `this.logger.debug()` instead of conditional logic
4. **No Conditional Checks**: Remove all `if (logger) ... else console.log()` patterns
5. **Structured Logging**: All log messages include relevant metadata

## Consequences

### Positive
- **Clean Architecture**: Clear dependency relationships, no circular dependencies
- **Consistent Logging**: All services log in same structured format
- **Testability**: Easy to inject mock loggers for testing
- **Flexibility**: Services work with or without logger dependency
- **Maintainability**: Single logging approach throughout codebase

### Negative
- **Slight Complexity**: Requires constructor parameter handling
- **Memory Overhead**: Each service creates its own console logger fallback
- **Interface Coupling**: Services depend on Logger interface

### Risks
- **Performance**: Multiple logger instances (mitigated by lightweight fallback)
- **Configuration Complexity**: Services need logger wired correctly (mitigated by factory pattern)

## Alternatives Considered

### Alternative 1: Service Locator Pattern
```typescript
class ServiceRegistry {
  static logger: Logger = new ConsoleLogger();
}
```
- **Pros**: Global access, no constructor parameters
- **Cons**: Hidden dependencies, harder to test, global state issues

### Alternative 2: Direct Console Usage
```typescript
console.log(`[STUB] Operation: ${operation}`);
```
- **Pros**: Simple, no dependencies
- **Cons**: Inconsistent logging format, no structured data, hard to filter/parse

### Alternative 3: Event-Based Logging
```typescript
this.emit('log', { level: 'debug', msg: 'operation', meta });
```
- **Pros**: Decoupled, flexible
- **Cons**: Complex setup, harder to follow execution flow

## Implementation Details

### Before (Problematic Pattern)
```typescript
async someMethod() {
  if (this.logger) {
    this.logger.debug('Operation started');
  } else {
    console.log('[STUB] Operation started');
  }
}
```

### After (Clean Pattern)
```typescript
constructor(logger?: Logger) {
  this.logger = logger || createConsoleLogger();
}

async someMethod() {
  this.logger.debug('Operation started', { operation: 'someMethod' });
}
```

### Factory Integration
```typescript
export function createPlatformServices(options = {}) {
  const logger = new ConsoleLogger(baseFields);
  
  return {
    logger,
    config: new EnvironmentConfig(),
    db: new StubDatabase(logger),        // Logger injected
    cache: new StubCache(logger),        // Logger injected
    // ... all services get logger
  };
}
```

## Testing Strategy

- Mock loggers injected for testing isolated behavior
- Console logger tested separately to ensure fallback works
- Integration tests verify logger propagation through factory

## Review Criteria

This pattern should be reconsidered if:
- Performance profiling shows logger creation overhead is significant
- Dependency injection becomes too complex to manage
- Alternative patterns prove simpler while maintaining benefits
- Circular dependency issues reappear despite this pattern

## Related ADRs

- ADR-004: Platform Wrapper Interface Enhancement
- ADR-006: Factory Pattern for Service Container Creation
- ADR-007: Error Handling Strategy for Platform Services