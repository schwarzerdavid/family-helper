# ADR-006: Factory Pattern for Service Container Creation

**Status:** Accepted  
**Date:** 2025-09-02  
**Deciders:** David Schwarzer, Claude  

## Context

The Phase 0 specification suggested direct exports of service instances:
```typescript
export const logger: Logger = new ConsoleLogger();
export const config: Config = new EnvironmentConfig();
```

However, as the platform wrapper evolved with dependency injection and multiple service types, we needed a way to:
1. **Wire Dependencies**: Logger needs to be passed to stub services
2. **Manage Configuration**: Different environments need different service configurations
3. **Support Testing**: Easy creation of test-specific service containers
4. **Enable Flexibility**: Allow customization of service creation

Two patterns were considered: direct exports vs factory-based service containers.

## Decision

We decided to implement a **Factory Pattern for Service Container Creation** alongside maintaining backward compatibility with direct exports.

### Primary Factory Function
```typescript
export function createPlatformServices(options: PlatformServicesOptions = {}): PlatformServices {
  const logger = new ConsoleLogger(baseFields);
  
  return {
    logger,
    config: new EnvironmentConfig(),
    secrets: new StubSecrets(logger),
    db: new StubDatabase(logger),
    pubsub: new StubPubSub(logger),
    objectStorage: new StubObjectStorage(logger),
    cache: new StubCache(logger),
    featureFlags: new StubFeatureFlags(logger),
    tracer: new StubTracer(logger)
  };
}
```

### Service Container Interface
```typescript
export interface PlatformServices {
  logger: Logger;
  config: Config;
  secrets: Secrets;
  db: Db;
  pubsub: PubSub;
  objectStorage: ObjectStorage;
  cache: Cache;
  featureFlags: FeatureFlags;
  tracer: Tracer;
}
```

### Configuration Options
```typescript
export interface PlatformServicesOptions {
  serviceName?: string;
  environment?: string;
  loggerContext?: Record<string, unknown>;
  useStubs?: boolean;
}
```

## Consequences

### Positive
- **Dependency Management**: All services properly wired with dependencies
- **Testability**: Easy to create isolated test service containers
- **Configurability**: Services can be customized per environment
- **Type Safety**: Complete service container typed with TypeScript
- **Consistency**: Single entry point for all platform services
- **Backward Compatibility**: Direct exports still available for simple usage

### Negative
- **API Surface**: More complex API with both patterns available
- **Documentation**: Need to explain both usage patterns
- **Maintenance**: Two patterns to maintain and keep in sync

### Risks
- **Confusion**: Developers might not know which pattern to use
- **Inconsistency**: Mixed usage patterns across codebase (mitigated by clear documentation)

## Alternatives Considered

### Alternative 1: Direct Exports Only (Original Spec)
```typescript
export const logger = new ConsoleLogger();
export const db = new StubDatabase(logger); // Manual dependency wiring
```
- **Pros**: Simple, matches specification exactly
- **Cons**: Manual dependency management, hard to customize, poor testing experience

### Alternative 2: Class-Based Container
```typescript
class PlatformContainer {
  constructor(options) { /* ... */ }
  get logger() { return this._logger; }
  get db() { return this._db; }
}
```
- **Pros**: OOP approach, encapsulation
- **Cons**: More complex, requires instantiation, less functional approach

### Alternative 3: DI Framework Integration
Using external dependency injection frameworks like InversifyJS
- **Pros**: Full-featured DI capabilities, decorators, advanced features
- **Cons**: External dependency, complexity overkill, learning curve

## Implementation Details

### Usage Patterns

#### Factory Pattern (Recommended)
```typescript
import { createPlatformServices } from '@family-helper/platform-ts';

const platform = createPlatformServices({
  serviceName: 'user-service',
  environment: 'production'
});

await platform.db.query('SELECT * FROM users');
platform.logger.info('Query executed');
```

#### Direct Exports (Simple Cases)
```typescript
import { logger, config } from '@family-helper/platform-ts';

logger.info('Simple logging');
const port = config.get('PORT', { default: '3000' });
```

#### Testing
```typescript
import { createTestPlatformServices } from '@family-helper/platform-ts';

const testPlatform = createTestPlatformServices('test-service');
// All services configured for testing
```

### Service Lifecycle
1. **Factory Called**: `createPlatformServices()` invoked with options
2. **Logger Created**: Base logger with service context configured
3. **Dependencies Injected**: Logger passed to all stub services
4. **Container Returned**: Complete service container with all dependencies wired

## Migration Strategy

- **Phase 0**: Both patterns available, factory recommended for new code
- **Phase 1**: Gradually migrate existing direct exports to factory usage
- **Phase 2**: Consider deprecating direct exports if factory proves superior

## Review Criteria

This pattern should be reconsidered if:
- Direct exports prove sufficient for all use cases
- Factory complexity outweighs benefits
- Alternative DI patterns prove more effective
- Performance overhead becomes significant

## Related ADRs

- ADR-004: Platform Wrapper Interface Enhancement
- ADR-005: Dependency Injection Pattern for Platform Services
- ADR-007: Error Handling Strategy for Platform Services