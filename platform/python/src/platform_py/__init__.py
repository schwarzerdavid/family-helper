"""
Python Platform Wrapper

Provides comprehensive platform services for Python applications including:
- Structured logging with ConsoleLogger
- Environment-based configuration with type conversion
- Database, PubSub, Object Storage, Cache, Secrets, FeatureFlags, and Tracing interfaces
- Complete stub implementations for development and testing
- Factory pattern for easy service container creation

Example usage:
    ```python
    from platform_py import create_platform_services
    
    # Create platform services with stubs for development
    platform = create_platform_services(
        service_name="my-service",
        environment="development"
    )
    
    # Use the services
    platform.logger.info("Service starting")
    database_url = platform.config.get("DATABASE_URL", required=True)
    users = await platform.db.query("SELECT * FROM users")
    await platform.pubsub.publish("user.created", {"user_id": 123})
    ```
"""

# Export all interfaces
from .interfaces import (
    Logger,
    Config, 
    Secrets,
    Db,
    EventEnvelope,
    PubSub,
    ObjectStorage,
    Cache,
    FeatureFlags,
    Tracer,
)

# Export implementations
from .implementations.logger import ConsoleLogger
from .implementations.config import EnvironmentConfig, ConfigError
from .implementations.stubs import (
    StubSecrets,
    StubDatabase,
    StubPubSub,
    StubObjectStorage,
    StubCache,
    StubFeatureFlags,
    StubTracer,
)

# Export factory
from .factory import create_platform_services, create_test_platform_services, PlatformServices

__version__ = "1.0.0"
__author__ = "David Schwarzer"
__email__ = "schwarzerdavid@gmail.com"

__all__ = [
    # Interfaces
    "Logger",
    "Config", 
    "Secrets",
    "Db",
    "EventEnvelope",
    "PubSub",
    "ObjectStorage",
    "Cache",
    "FeatureFlags",
    "Tracer",
    # Implementations
    "ConsoleLogger",
    "EnvironmentConfig",
    "ConfigError",
    # Stubs
    "StubSecrets",
    "StubDatabase", 
    "StubPubSub",
    "StubObjectStorage",
    "StubCache",
    "StubFeatureFlags",
    "StubTracer",
    # Factory
    "create_platform_services",
    "create_test_platform_services", 
    "PlatformServices",
]