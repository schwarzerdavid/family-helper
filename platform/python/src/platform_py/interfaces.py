"""
Core platform interfaces that define the contracts for all infrastructure services.
These interfaces abstract away cloud provider specifics and enable testability.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union, TypeVar, Generic, AsyncContextManager
from datetime import datetime
import asyncio

T = TypeVar('T')

class Logger(ABC):
    """Structured logging interface with contextual metadata support"""
    
    @abstractmethod
    def info(self, msg: str, meta: Optional[Dict[str, Any]] = None) -> None:
        """Log info level message with optional metadata"""
        pass
    
    @abstractmethod
    def error(self, msg: str, meta: Optional[Dict[str, Any]] = None) -> None:
        """Log error level message with optional metadata"""
        pass
    
    @abstractmethod
    def warn(self, msg: str, meta: Optional[Dict[str, Any]] = None) -> None:
        """Log warning level message with optional metadata"""
        pass
    
    @abstractmethod
    def debug(self, msg: str, meta: Optional[Dict[str, Any]] = None) -> None:
        """Log debug level message with optional metadata"""
        pass
    
    @abstractmethod
    def with_fields(self, fields: Dict[str, Any]) -> "Logger":
        """Create child logger with additional context fields"""
        pass


class Config(ABC):
    """Configuration management interface for environment variables and settings"""
    
    @abstractmethod
    def get(self, key: str, required: bool = False, default: Optional[T] = None) -> Union[str, T]:
        """Get configuration value with optional type conversion and default"""
        pass
    
    @abstractmethod
    def get_int(self, key: str, required: bool = False, default: Optional[int] = None) -> Optional[int]:
        """Get configuration value as integer"""
        pass
    
    @abstractmethod
    def get_bool(self, key: str, required: bool = False, default: Optional[bool] = None) -> Optional[bool]:
        """Get configuration value as boolean"""
        pass
    
    @abstractmethod
    def get_float(self, key: str, required: bool = False, default: Optional[float] = None) -> Optional[float]:
        """Get configuration value as float"""
        pass


class Secrets(ABC):
    """Secure secrets management interface"""
    
    @abstractmethod
    async def get(self, name: str) -> str:
        """Retrieve secret value by name"""
        pass


class Db(ABC):
    """Database interface with connection pooling and transaction support"""
    
    @abstractmethod
    async def query(self, sql: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """Execute query and return results"""
        pass
    
    @abstractmethod
    async def execute(self, sql: str, params: Optional[List[Any]] = None) -> int:
        """Execute statement and return affected row count"""
        pass
    
    @abstractmethod
    async def with_tx(self, fn: Callable[["Db"], Any]) -> Any:
        """Execute function within transaction context"""
        pass


class EventEnvelope:
    """Event envelope for all published events"""
    
    def __init__(
        self,
        id: str,
        type: str,
        occurred_at: str,
        payload: Any,
        idempotency_key: str,
        trace: Optional[Dict[str, str]] = None
    ):
        self.id = id
        self.type = type
        self.occurred_at = occurred_at
        self.payload = payload
        self.idempotency_key = idempotency_key
        self.trace = trace or {}


class PubSub(ABC):
    """Pub/Sub interface for event-driven communication"""
    
    @abstractmethod
    async def publish(
        self, 
        topic: str, 
        event: Any, 
        idempotency_key: Optional[str] = None
    ) -> None:
        """Publish event to topic"""
        pass
    
    @abstractmethod
    def subscribe(
        self, 
        topic: str, 
        handler: Callable[[EventEnvelope], Any]
    ) -> Callable[[], None]:
        """Subscribe to topic with handler, returns unsubscribe function"""
        pass


class ObjectStorage(ABC):
    """Object storage interface for file operations (S3-like)"""
    
    @abstractmethod
    async def put(self, key: str, data: bytes, content_type: str) -> Dict[str, str]:
        """Store object and return metadata (etag, etc.)"""
        pass
    
    @abstractmethod
    async def get(self, key: str) -> bytes:
        """Retrieve object data"""
        pass
    
    @abstractmethod
    async def presign_put(self, key: str, expires_in_seconds: int) -> str:
        """Generate presigned PUT URL"""
        pass
    
    @abstractmethod
    async def presign_get(self, key: str, expires_in_seconds: int) -> str:
        """Generate presigned GET URL"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete object, return True if existed"""
        pass


class Cache(ABC):
    """Cache interface for high-performance data storage (Redis-like)"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Set cached value with optional TTL"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete cached value, return True if existed"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass


class FeatureFlags(ABC):
    """Feature flags interface for runtime configuration"""
    
    @abstractmethod
    async def is_enabled(
        self, 
        flag: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Check if feature flag is enabled"""
        pass
    
    @abstractmethod
    async def get_value(
        self, 
        flag: str, 
        default_value: T, 
        context: Optional[Dict[str, Any]] = None
    ) -> T:
        """Get feature flag value with type safety"""
        pass


class Tracer(ABC):
    """Distributed tracing interface"""
    
    @abstractmethod
    async def start_span(self, name: str, fn: Callable[[], Any]) -> Any:
        """Execute function within tracing span"""
        pass
    
    @abstractmethod
    def get_current_trace_id(self) -> Optional[str]:
        """Get current trace ID if available"""
        pass
    
    @abstractmethod
    def with_span(self, name: str) -> AsyncContextManager[None]:
        """Context manager for manual span management"""
        pass