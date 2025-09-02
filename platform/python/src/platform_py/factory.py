"""
Factory functions for creating platform service containers.
Provides easy dependency injection and service wiring.
"""

import os
from typing import Any, Dict, Optional

from .interfaces import (
    Cache,
    Config,
    Db,
    FeatureFlags,
    Logger,
    ObjectStorage,
    PubSub,
    Secrets,
    Tracer,
)
from .implementations.config import EnvironmentConfig
from .implementations.logger import ConsoleLogger
from .implementations.stubs import (
    StubCache,
    StubDatabase,
    StubFeatureFlags,
    StubObjectStorage,
    StubPubSub,
    StubSecrets,
    StubTracer,
)


class PlatformServices:
    """
    Platform services container that provides all infrastructure dependencies.
    All services are properly wired with dependency injection.
    """
    
    def __init__(
        self,
        logger: Logger,
        config: Config,
        secrets: Secrets,
        db: Db,
        pubsub: PubSub,
        object_storage: ObjectStorage,
        cache: Cache,
        feature_flags: FeatureFlags,
        tracer: Tracer,
    ):
        self.logger = logger
        self.config = config
        self.secrets = secrets
        self.db = db
        self.pubsub = pubsub
        self.object_storage = object_storage
        self.cache = cache
        self.feature_flags = feature_flags
        self.tracer = tracer


def create_platform_services(
    service_name: str = "unknown-service",
    environment: Optional[str] = None,
    logger_context: Optional[Dict[str, Any]] = None,
    use_stubs: bool = True,
) -> PlatformServices:
    """
    Factory function to create a complete set of platform services.
    Uses stub implementations by default for easy development setup.
    
    Args:
        service_name: Service name for logging context
        environment: Environment (development, staging, production)
        logger_context: Additional logger context fields
        use_stubs: Use stub implementations for development/testing
        
    Returns:
        Complete platform services container
        
    Example:
        ```python
        from platform_py import create_platform_services
        
        # Development setup with stubs
        platform = create_platform_services(
            service_name="my-service",
            use_stubs=True
        )
        
        # Use the services
        platform.logger.info("Service starting")
        users = await platform.db.query("SELECT * FROM users")
        await platform.pubsub.publish("user.created", {"user_id": 123})
        ```
    """
    # Determine environment
    if environment is None:
        environment = os.environ.get("ENVIRONMENT", os.environ.get("NODE_ENV", "development"))
    
    # Create logger first as other services may need it
    base_context = {
        "service": service_name,
        "environment": environment,
        **(logger_context or {})
    }
    logger = ConsoleLogger(base_context)
    
    # Create config service
    config = EnvironmentConfig()
    
    # Create other services - use stubs by default for easy development
    services = PlatformServices(
        logger=logger,
        config=config,
        secrets=StubSecrets(logger),
        db=StubDatabase(logger),
        pubsub=StubPubSub(logger),
        object_storage=StubObjectStorage(logger),
        cache=StubCache(logger),
        feature_flags=StubFeatureFlags(logger),
        tracer=StubTracer(logger),
    )
    
    logger.info("Platform services initialized", {
        "service_name": service_name,
        "environment": environment,
        "use_stubs": use_stubs,
        "services_created": [
            "logger", "config", "secrets", "db", "pubsub",
            "object_storage", "cache", "feature_flags", "tracer"
        ]
    })
    
    return services


def create_test_platform_services(service_name: str = "test-service") -> PlatformServices:
    """
    Creates platform services specifically configured for testing.
    Always uses stub implementations with minimal logging.
    
    Args:
        service_name: Service name for test context
        
    Returns:
        Platform services configured for testing
    """
    return create_platform_services(
        service_name=service_name,
        environment="test",
        use_stubs=True,
        logger_context={"test_run": True}
    )