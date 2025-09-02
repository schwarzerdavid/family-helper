# ADR-002: Use Abstract Base Classes for Platform Interfaces

## Status
Accepted

## Context
The Python Platform Wrapper needs to define clear contracts for platform services (Logger, Config, Database, PubSub, etc.). Several approaches were considered for defining these interfaces:

1. **Protocol classes** (typing.Protocol): Structural typing approach
2. **Abstract Base Classes** (abc.ABC): Inheritance-based interfaces
3. **Regular classes with NotImplementedError**: Manual interface enforcement
4. **TypedDict or dataclasses**: Data structure approaches

The choice affects type checking, runtime behavior, and developer experience.

## Decision
We will use **Abstract Base Classes (ABC)** with the `@abstractmethod` decorator for all platform service interfaces.

## Rationale

### Advantages of ABC:
1. **Runtime Enforcement**: Prevents instantiation of incomplete implementations
2. **Clear Intent**: Explicit declaration of abstract methods
3. **Type Safety**: Full type checker support (mypy, pylance)
4. **Documentation**: Clear contract definition for implementers
5. **Python Idioms**: Follows established Python patterns for interfaces

### Technical Benefits:
- **Early Error Detection**: Runtime errors if abstract methods not implemented
- **IDE Support**: Better autocomplete and error detection
- **Inheritance Hierarchy**: Clean inheritance relationships
- **Method Signature Enforcement**: Ensures implementing classes match signatures

### Implementation Pattern:
```python
from abc import ABC, abstractmethod

class Logger(ABC):
    @abstractmethod
    def info(self, msg: str, meta: Optional[Dict[str, Any]] = None) -> None:
        """Log info level message"""
        pass
    
    @abstractmethod
    def with_fields(self, fields: Dict[str, Any]) -> "Logger":
        """Create child logger with additional context"""
        pass
```

## Consequences

### Positive:
- **Compile-time Safety**: Type checkers can verify interface compliance
- **Runtime Safety**: Cannot instantiate incomplete implementations
- **Clear Documentation**: Abstract methods serve as interface documentation
- **Better IDE Support**: Enhanced autocomplete and refactoring
- **Consistent Patterns**: All platform services follow same interface pattern

### Negative:
- **Inheritance Requirement**: Implementations must inherit from ABC classes
- **Python Version**: Requires Python 3.4+ (already met)
- **Slightly More Verbose**: More code than Protocol-based approaches

### Mitigation:
- Use type hints extensively for better documentation
- Provide comprehensive docstrings for all abstract methods
- Create base implementations where appropriate

## Alternatives Considered

### Protocol Classes (typing.Protocol)
- **Pros**: Structural typing, no inheritance required, duck typing support
- **Cons**: No runtime enforcement, newer Python feature, less explicit
- **Rejected**: Lack of runtime enforcement reduces safety

### Regular Classes with NotImplementedError
- **Pros**: Simple, explicit, works in all Python versions
- **Cons**: Manual enforcement, easy to forget, poor type checker support
- **Rejected**: Too error-prone and lacks type safety

### TypedDict for Data Interfaces
- **Pros**: Good for data structures, type checker support
- **Cons**: Only for data, no behavior definition, no inheritance
- **Rejected**: Platform services need behavior contracts, not just data

## Implementation Details

### Interface Definition:
- All platform service interfaces inherit from `abc.ABC`
- All public methods marked with `@abstractmethod`
- Comprehensive type hints for all parameters and return types
- Detailed docstrings explaining method contracts

### Naming Conventions:
- Interface names are nouns (Logger, Config, Db, PubSub)
- Method names are verbs or verb phrases (get, set, query, publish)
- Async methods clearly marked with async/await

### Type Safety:
- Generic types used where appropriate (EventEnvelope[T])
- Optional types used for nullable parameters
- Union types for multiple acceptable types

## Verification
Interface compliance is verified through:
- Static type checking with mypy
- Runtime instantiation attempts in tests
- Comprehensive test suite covering all abstract methods
- IDE type checking during development

## Review Date
This decision should be reviewed if:
- Python Protocol classes mature significantly
- Team feedback indicates inheritance is too restrictive
- Performance issues arise from ABC overhead
- Alternative interface patterns prove more effective