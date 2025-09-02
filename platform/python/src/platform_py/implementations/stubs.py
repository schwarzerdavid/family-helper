"""
Stub implementations of platform services for development and testing.
All stub services provide comprehensive logging and realistic behavior simulation.
"""

import asyncio
import json
import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import quote

from ..interfaces import (
    Cache,
    Db,
    EventEnvelope,
    FeatureFlags,
    Logger,
    ObjectStorage,
    PubSub,
    Secrets,
    Tracer,
)
from .logger import ConsoleLogger


def _create_console_logger() -> Logger:
    """Simple console-based logger fallback for when no logger is provided"""
    return ConsoleLogger({"component": "stub"})


class StubSecrets(Secrets):
    """
    Stub implementation of the Secrets interface.
    Falls back to environment variables for development.
    """
    
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or _create_console_logger()
        self._secret_cache: Dict[str, str] = {}
    
    async def get(self, name: str) -> str:
        """Retrieve secret, falling back to environment variables"""
        self.logger.debug("Retrieving secret", {"secret_name": name})
        
        # Check cache first
        if name in self._secret_cache:
            self.logger.debug("Secret found in cache", {"secret_name": name})
            return self._secret_cache[name]
        
        # Fallback to environment variable
        env_value = os.environ.get(name)
        if env_value:
            self.logger.debug("Secret found in environment variables", {"secret_name": name})
            self._secret_cache[name] = env_value
            return env_value
        
        # In real implementation, this would throw an error
        # For stub, we'll return a placeholder
        placeholder = f"stub-secret-{name}"
        
        self.logger.warn("Secret not found, returning placeholder", {
            "secret_name": name,
            "placeholder": placeholder
        })
        
        self._secret_cache[name] = placeholder
        return placeholder


class StubDatabase(Db):
    """
    Stub implementation of the Database interface for development and testing.
    Logs all operations but doesn't perform actual database operations.
    """
    
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or _create_console_logger()
        self._transaction_depth = 0
        self._data_store: Dict[str, List[Dict[str, Any]]] = {}
    
    async def query(self, sql: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """Execute query and return mock results"""
        params = params or []
        prefix = "[TX] " if self._transaction_depth > 0 else ""
        message = f"{prefix}Stub database query executed"
        metadata = {
            "sql": sql,
            "params": params,
            "transaction_depth": self._transaction_depth
        }
        
        self.logger.debug(message, metadata)
        
        # Return empty list - real implementation would return actual data
        return []
    
    async def execute(self, sql: str, params: Optional[List[Any]] = None) -> int:
        """Execute statement and return mock affected row count"""
        params = params or []
        prefix = "[TX] " if self._transaction_depth > 0 else ""
        message = f"{prefix}Stub database execute performed"
        metadata = {
            "sql": sql,
            "params": params,
            "transaction_depth": self._transaction_depth
        }
        
        self.logger.debug(message, metadata)
        
        # Return mock affected row count
        return 1
    
    async def with_tx(self, fn: Callable[["Db"], Any]) -> Any:
        """Execute function within transaction context"""
        self.logger.debug("Starting database transaction", {"transaction_depth": self._transaction_depth})
        
        self._transaction_depth += 1
        
        try:
            # Pass this same stub instance as the transaction database
            # Real implementation would use a transaction-scoped connection
            result = await fn(self)
            
            self.logger.debug("Database transaction committed", {"transaction_depth": self._transaction_depth - 1})
            
            return result
        except Exception as error:
            self.logger.error("Database transaction rolled back", {
                "error": str(error),
                "error_type": type(error).__name__,
                "transaction_depth": self._transaction_depth - 1
            })
            raise
        finally:
            self._transaction_depth -= 1


class StubPubSub(PubSub):
    """
    Stub implementation of the PubSub interface.
    Provides in-memory event handling for development and testing.
    """
    
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or _create_console_logger()
        self._subscribers: Dict[str, List[Callable[[EventEnvelope], Any]]] = {}
        self._event_history: List[EventEnvelope] = []
    
    async def publish(self, topic: str, event: Any, idempotency_key: Optional[str] = None) -> None:
        """Publish event to topic"""
        # Create event envelope
        envelope = EventEnvelope(
            id=self._generate_uuid(),
            type=topic,
            occurred_at=datetime.now(timezone.utc).isoformat(),
            payload=event,
            idempotency_key=idempotency_key or self._generate_uuid(),
            trace={"traceparent": self._get_current_trace_id()}
        )
        
        self.logger.info("Publishing event to stub pub/sub", {
            "topic": topic,
            "event_id": envelope.id,
            "idempotency_key": envelope.idempotency_key,
            "payload_type": type(event).__name__,
            "subscriber_count": len(self._subscribers.get(topic, []))
        })
        
        # Store in history for debugging
        self._event_history.append(envelope)
        
        # Keep only last 100 events to prevent memory leaks
        if len(self._event_history) > 100:
            self._event_history.pop(0)
        
        # Notify subscribers (simulate async processing)
        handlers = self._subscribers.get(topic, [])
        
        if not handlers:
            self.logger.debug("No subscribers found for topic", {"topic": topic})
        else:
            self.logger.debug("Notifying subscribers", {"topic": topic, "subscriber_count": len(handlers)})
            
            # Process handlers asynchronously (don't await to simulate real pub/sub)
            for handler in handlers:
                asyncio.create_task(self._handle_event_safely(handler, envelope, topic))
    
    def subscribe(self, topic: str, handler: Callable[[EventEnvelope], Any]) -> Callable[[], None]:
        """Subscribe to topic with handler, returns unsubscribe function"""
        self.logger.debug("Subscribing to topic", {"topic": topic})
        
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        
        self._subscribers[topic].append(handler)
        
        # Return unsubscribe function
        def unsubscribe():
            self.logger.debug("Unsubscribing from topic", {"topic": topic})
            
            if topic in self._subscribers and handler in self._subscribers[topic]:
                self._subscribers[topic].remove(handler)
                
                # Clean up empty topic lists
                if not self._subscribers[topic]:
                    del self._subscribers[topic]
        
        return unsubscribe
    
    def get_event_history(self) -> List[EventEnvelope]:
        """Debug method to see recent events (useful for development)"""
        return self._event_history.copy()
    
    def get_subscriptions(self) -> Dict[str, int]:
        """Debug method to see current subscriptions"""
        return {topic: len(handlers) for topic, handlers in self._subscribers.items()}
    
    async def _handle_event_safely(self, handler: Callable, envelope: EventEnvelope, topic: str) -> None:
        """Handle event with error protection"""
        try:
            await handler(envelope)
        except Exception as error:
            self.logger.error("Event handler failed", {
                "topic": topic,
                "event_id": envelope.id,
                "error": str(error),
                "error_type": type(error).__name__
            })
    
    def _generate_uuid(self) -> str:
        """Generate UUID for events"""
        return str(uuid.uuid4())
    
    def _get_current_trace_id(self) -> Optional[str]:
        """Get current trace ID from environment (placeholder)"""
        return os.environ.get("TRACE_ID")


class StubObjectStorage(ObjectStorage):
    """Stub implementation of ObjectStorage interface"""
    
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or _create_console_logger()
    
    async def put(self, key: str, data: bytes, content_type: str) -> Dict[str, str]:
        """Store object and return mock metadata"""
        self.logger.debug("Storing object in stub storage", {
            "key": key,
            "size": len(data),
            "content_type": content_type
        })
        
        return {"etag": f"stub-etag-{int(time.time() * 1000)}"}
    
    async def get(self, key: str) -> bytes:
        """Retrieve mock object data"""
        self.logger.debug("Retrieving object from stub storage", {"key": key})
        return f"stub-content-for-{key}".encode("utf-8")
    
    async def presign_put(self, key: str, expires_in_seconds: int) -> str:
        """Generate mock presigned PUT URL"""
        self.logger.debug("Generating presigned PUT URL", {"key": key, "expires_in_seconds": expires_in_seconds})
        return f"https://stub-storage.example.com/upload?key={quote(key)}&expires={expires_in_seconds}"
    
    async def presign_get(self, key: str, expires_in_seconds: int) -> str:
        """Generate mock presigned GET URL"""
        self.logger.debug("Generating presigned GET URL", {"key": key, "expires_in_seconds": expires_in_seconds})
        return f"https://stub-storage.example.com/download?key={quote(key)}&expires={expires_in_seconds}"
    
    async def delete(self, key: str) -> bool:
        """Mock delete operation"""
        self.logger.debug("Deleting object from stub storage", {"key": key})
        return True  # Always return True for stub


class StubCache(Cache):
    """Stub implementation of Cache interface with TTL support"""
    
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or _create_console_logger()
        self._store: Dict[str, Dict[str, Any]] = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value with expiration check"""
        self.logger.debug("Getting value from stub cache", {"key": key})
        
        entry = self._store.get(key)
        if not entry:
            self.logger.debug("Cache miss", {"key": key})
            return None
        
        # Check expiration
        if "expires" in entry and time.time() > entry["expires"]:
            self.logger.debug("Cache entry expired", {"key": key, "expired_at": entry["expires"]})
            del self._store[key]
            return None
        
        self.logger.debug("Cache hit", {"key": key})
        return entry["value"]
    
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Set cached value with optional TTL"""
        metadata = {"key": key, "has_ttl": ttl_seconds is not None}
        if ttl_seconds:
            metadata["ttl_seconds"] = ttl_seconds
        
        self.logger.debug("Setting value in stub cache", metadata)
        
        entry = {"value": value}
        if ttl_seconds:
            entry["expires"] = time.time() + ttl_seconds
        
        self._store[key] = entry
    
    async def delete(self, key: str) -> bool:
        """Delete cached value"""
        self.logger.debug("Deleting value from stub cache", {"key": key})
        existed = key in self._store
        if existed:
            del self._store[key]
        
        self.logger.debug("Cache deletion result", {"key": key, "existed": existed})
        return existed
    
    async def exists(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        entry = self._store.get(key)
        if not entry:
            return False
        
        # Check expiration
        if "expires" in entry and time.time() > entry["expires"]:
            del self._store[key]
            return False
        
        return True


class StubFeatureFlags(FeatureFlags):
    """Stub implementation of FeatureFlags interface"""
    
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or _create_console_logger()
    
    async def is_enabled(self, flag: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Check if feature flag is enabled (default to True in development)"""
        self.logger.debug("Checking feature flag enabled status", {
            "flag": flag,
            "context": context,
            "result": True
        })
        # Default to enabled for development
        return True
    
    async def get_value(self, flag: str, default_value: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """Get feature flag value (return default in stub)"""
        self.logger.debug("Getting feature flag value", {
            "flag": flag,
            "default_value": default_value,
            "context": context,
            "result": default_value
        })
        return default_value


class StubTracer(Tracer):
    """Stub implementation of Tracer interface"""
    
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or _create_console_logger()
    
    async def start_span(self, name: str, fn: Callable[[], Any]) -> Any:
        """Execute function within tracing span"""
        span_id = self._generate_span_id()
        self.logger.debug("Starting tracing span", {"span_name": name, "span_id": span_id})
        
        start_time = time.time()
        try:
            result = await fn()
            duration = int((time.time() - start_time) * 1000)  # Convert to milliseconds
            self.logger.debug("Tracing span completed", {
                "span_name": name,
                "span_id": span_id,
                "duration": duration
            })
            return result
        except Exception as error:
            duration = int((time.time() - start_time) * 1000)
            self.logger.error("Tracing span failed", {
                "span_name": name,
                "span_id": span_id,
                "duration": duration,
                "error": str(error),
                "error_type": type(error).__name__
            })
            raise
    
    def get_current_trace_id(self) -> Optional[str]:
        """Get current trace ID from environment"""
        trace_id = os.environ.get("TRACE_ID")
        self.logger.debug("Getting current trace ID", {"trace_id": trace_id})
        return trace_id
    
    @asynccontextmanager
    async def with_span(self, name: str):
        """Context manager for manual span management"""
        span_id = self._generate_span_id()
        self.logger.debug("Starting manual tracing span", {"span_name": name, "span_id": span_id})
        
        start_time = time.time()
        try:
            yield
            duration = int((time.time() - start_time) * 1000)
            self.logger.debug("Manual tracing span completed", {
                "span_name": name,
                "span_id": span_id,
                "duration": duration
            })
        except Exception as error:
            duration = int((time.time() - start_time) * 1000)
            self.logger.error("Manual tracing span failed", {
                "span_name": name,
                "span_id": span_id,
                "duration": duration,
                "error": str(error),
                "error_type": type(error).__name__
            })
            raise
    
    def _generate_span_id(self) -> str:
        """Generate random span ID"""
        return f"{uuid.uuid4().hex[:8]}"