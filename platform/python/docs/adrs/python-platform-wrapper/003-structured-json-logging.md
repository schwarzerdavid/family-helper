# ADR-003: Structured JSON Logging with UTC Timestamps

## Status
Accepted

## Context
The ConsoleLogger implementation needs to output logs that are easily parseable by log aggregation systems (ELK stack, CloudWatch, etc.). Several logging approaches were considered:

1. **Plain text logging**: Human-readable but hard to parse programmatically
2. **Structured JSON logging**: Machine-readable with consistent schema
3. **Key-value pairs**: Semi-structured but inconsistent format
4. **Binary logging**: Efficient but requires special tools

The choice affects log analysis, monitoring, and debugging capabilities.

## Decision
We will implement **structured JSON logging** with UTC timestamps and consistent field schemas.

## Rationale

### Advantages of Structured JSON:
1. **Machine Readable**: Easy parsing by log aggregation systems
2. **Consistent Schema**: Predictable field names and types
3. **Rich Metadata**: Support for arbitrary metadata fields
4. **Query Friendly**: Easy to search and filter in log systems
5. **Tool Integration**: Works well with modern observability tools

### Technical Implementation:
```python
{
    "timestamp": "2023-01-01T12:00:00+00:00",
    "level": "info",
    "msg": "User authenticated",
    "service": "auth-service",
    "environment": "production",
    "user_id": 12345,
    "request_id": "req-abc-123"
}
```

### Key Design Decisions:

#### UTC Timestamps:
- All timestamps in UTC using ISO 8601 format
- Avoids timezone confusion in distributed systems
- Compatible with log aggregation systems

#### Compact JSON Format:
- No spaces after separators for efficiency
- Reduces log volume and storage costs
- Still maintains readability

#### Hierarchical Context:
- Base fields (service, environment) in every log
- Child loggers inherit and extend context
- Request-specific context through `with_fields()`

## Consequences

### Positive:
- **Better Monitoring**: Easy to create dashboards and alerts
- **Efficient Searching**: Fast log queries in aggregation systems
- **Consistent Format**: All services produce similar log structure
- **Rich Context**: Detailed metadata for debugging
- **Tool Integration**: Works with ELK, Splunk, CloudWatch, etc.

### Negative:
- **Storage Overhead**: JSON is more verbose than plain text
- **Human Readability**: Less readable than formatted text logs
- **Parsing Dependency**: Requires JSON parsing for human consumption

### Mitigation:
- Use compact JSON format to minimize overhead
- Provide development tools for log formatting
- Include clear message fields for human readability

## Design Patterns

### Child Logger Pattern:
```python
# Base logger with service context
base_logger = ConsoleLogger({
    "service": "user-service",
    "environment": "production"
})

# Request-specific logger
request_logger = base_logger.with_fields({
    "request_id": "req-123",
    "user_id": 456
})

# All logs from request_logger include both base and request context
```

### Debug Filtering:
- Debug logs filtered by environment (production vs development)
- Override with LOG_LEVEL environment variable
- Reduces noise in production logs

### Error Stream Separation:
- Error logs to stderr, others to stdout
- Enables separate log stream processing
- Compatible with container logging

## Alternatives Considered

### Python's Built-in Logging Module
- **Pros**: Standard library, extensive configuration options
- **Cons**: Complex configuration, inconsistent JSON formatting
- **Rejected**: Too complex for simple structured logging needs

### Third-party Logging Libraries (loguru, structlog)
- **Pros**: Rich features, good JSON support
- **Cons**: Additional dependencies, potential conflicts
- **Rejected**: Adds complexity and dependencies for simple needs

### Plain Text with Structured Fields
- **Pros**: Human readable, smaller size
- **Cons**: Harder to parse, inconsistent formatting
- **Rejected**: Poor machine readability

## Implementation Details

### Field Standards:
- **timestamp**: ISO 8601 UTC format
- **level**: info, error, warn, debug
- **msg**: Human-readable message
- **service**: Service name from factory
- **environment**: Environment (development, staging, production)

### Environment-based Configuration:
- Debug logs only in development or when LOG_LEVEL=debug
- UTC timestamps for consistency across timezones
- Compact JSON for production efficiency

### Context Inheritance:
- Base fields set at logger creation
- Child loggers inherit and extend fields
- No field conflicts through proper merging

## Performance Considerations
- JSON serialization overhead acceptable for logging
- Compact format reduces I/O overhead
- Structured format enables efficient log processing
- UTC timestamps avoid timezone calculation overhead

## Review Date
This decision should be reviewed if:
- Log storage costs become prohibitive
- Performance issues arise from JSON serialization
- Team feedback indicates poor developer experience
- New logging requirements emerge from observability needs