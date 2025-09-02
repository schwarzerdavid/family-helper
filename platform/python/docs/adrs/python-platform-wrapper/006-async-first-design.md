# ADR-006: Async-First Design for Platform Services

## Status
Accepted

## Context
The platform services need to handle I/O operations (database queries, HTTP requests, file operations) that benefit from asynchronous execution. Several approaches were considered:

1. **Synchronous Only**: All operations blocking/synchronous
2. **Async Only**: All I/O operations use async/await
3. **Mixed Approach**: Some sync, some async methods
4. **Sync Wrapper**: Async core with synchronous wrapper methods

Modern Python applications increasingly use async frameworks (FastAPI, aiohttp) and async database drivers.

## Decision
We will implement **async-first design** with async/await for all I/O operations across platform services.

## Rationale

### Advantages of Async-First:
1. **Performance**: Non-blocking I/O operations
2. **Modern Python**: Aligns with current Python ecosystem trends
3. **Scalability**: Better resource utilization under concurrent load
4. **Framework Compatibility**: Works with async web frameworks
5. **Database Drivers**: Modern drivers are async-first (asyncpg, aioredis)

### Services Using Async:
- **Database**: Query and execute operations
- **Secrets**: Secret retrieval operations
- **PubSub**: Publish and subscribe operations
- **Object Storage**: Upload, download, and delete operations
- **Cache**: Get, set, delete operations
- **Feature Flags**: Flag evaluation operations
- **Tracing**: Span creation and management

### Synchronous Services:
- **Logger**: Immediate operations, no I/O blocking
- **Config**: Environment variable access (immediate)

## Technical Implementation

### Async Method Signatures:
```python
class Db(ABC):
    @abstractmethod
    async def query(self, sql: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """Execute query and return results"""
        pass
    
    @abstractmethod
    async def execute(self, sql: str, params: Optional[List[Any]] = None) -> int:
        """Execute statement and return affected row count"""
        pass
```

### Async Context Managers:
```python
class Tracer(ABC):
    @abstractmethod
    async def with_span(self, name: str):
        """Context manager for manual span management"""
        pass

# Usage:
async with tracer.with_span("database_operation"):
    result = await db.query("SELECT * FROM users")
```

### Callback Functions:
```python
class Db(ABC):
    @abstractmethod
    async def with_tx(self, fn: Callable[["Db"], Any]) -> Any:
        """Execute function within transaction context"""
        pass

# Usage:
async def update_user(tx_db: Db):
    await tx_db.execute("UPDATE users SET name = $1 WHERE id = $2", ["John", 123])

result = await db.with_tx(update_user)
```

## Consequences

### Positive:
- **Better Performance**: Non-blocking I/O operations
- **Resource Efficiency**: Better CPU and memory utilization
- **Modern Ecosystem**: Compatible with async frameworks and libraries
- **Scalability**: Handles many concurrent operations efficiently
- **Future-Proof**: Aligns with Python ecosystem direction

### Negative:
- **Complexity**: Async code can be more complex to reason about
- **Learning Curve**: Developers need async/await knowledge
- **Debugging**: Async debugging can be more challenging
- **Library Compatibility**: Need async-compatible dependencies

### Mitigation:
- **Comprehensive Testing**: Extensive async testing with pytest-asyncio
- **Clear Documentation**: Examples and patterns for async usage
- **Error Handling**: Proper exception handling in async contexts
- **Development Tools**: Use async-aware debugging tools

## Design Patterns

### Async Service Interface:
```python
# All I/O operations are async
class StubDatabase(Db):
    async def query(self, sql: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        self.logger.debug("Executing query", {"sql": sql})
        await asyncio.sleep(0.01)  # Simulate I/O delay
        return []
```

### Transaction Context:
```python
async def update_user_profile(db: Db, user_id: int, profile: dict):
    async def transaction_logic(tx_db: Db):
        await tx_db.execute("UPDATE users SET updated_at = NOW() WHERE id = $1", [user_id])
        await tx_db.execute("INSERT INTO audit_log (...) VALUES (...)", [...])
        return {"updated": True}
    
    return await db.with_tx(transaction_logic)
```

### Async Event Handling:
```python
async def handle_user_created(event: EventEnvelope):
    user_data = event.payload
    await send_welcome_email(user_data["email"])
    await create_user_preferences(user_data["id"])

pubsub.subscribe("user.created", handle_user_created)
```

## Testing Approach

### Async Test Methods:
```python
@pytest.mark.asyncio
async def test_database_query():
    db = StubDatabase()
    result = await db.query("SELECT * FROM users")
    assert result == []
```

### Async Fixtures:
```python
@pytest.fixture
async def database_service():
    db = StubDatabase()
    yield db
    # Cleanup if needed
```

### Event Loop Management:
```python
# conftest.py configures event loop for test session
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
```

## Alternatives Considered

### Synchronous Only
- **Pros**: Simpler code, easier debugging, broader compatibility
- **Cons**: Blocking I/O, poor scalability, outdated approach
- **Rejected**: Poor performance for I/O-heavy operations

### Mixed Sync/Async
- **Pros**: Flexibility, gradual adoption, compatibility
- **Cons**: Inconsistent API, confusion about when to use which
- **Rejected**: API inconsistency reduces developer experience

### Sync Wrapper Around Async Core
- **Pros**: Support both patterns, maximum compatibility
- **Cons**: Complex implementation, potential performance issues
- **Rejected**: Over-engineering for platform services

## Migration Strategy

### From Sync to Async:
1. **Interface First**: Define async interfaces
2. **Stub Implementation**: Implement async stubs
3. **Testing**: Comprehensive async testing
4. **Documentation**: Update examples and patterns
5. **Real Implementations**: Migrate to async drivers when building production services

### Compatibility:
- Factory functions remain synchronous (service creation)
- Configuration and logging remain synchronous (immediate operations)
- Clear separation between sync setup and async operations

## Performance Considerations
- Async overhead minimal for I/O-bound operations
- Stub implementations simulate realistic async behavior
- Event loop efficiency for concurrent operations
- Memory usage similar to synchronous implementations

## Review Date
This decision should be reviewed if:
- Async complexity becomes problematic for the team
- Performance issues arise from async overhead
- Synchronous compatibility requirements emerge
- Alternative concurrency models become standard