"""
Test suite for platform factory functions.
Tests service container creation, dependency injection, and factory configuration.
"""

import os
from unittest.mock import patch
import pytest

from platform_py.factory import (
    PlatformServices, create_platform_services, create_test_platform_services
)
from platform_py.implementations.logger import ConsoleLogger
from platform_py.implementations.config import EnvironmentConfig
from platform_py.implementations.stubs import (
    StubSecrets, StubDatabase, StubPubSub, StubObjectStorage,
    StubCache, StubFeatureFlags, StubTracer
)


class TestPlatformServices:
    """Test PlatformServices container class"""

    def test_platform_services__should_store_all_services(self):
        """PlatformServices should store all injected services"""
        logger = ConsoleLogger()
        config = EnvironmentConfig()
        secrets = StubSecrets()
        db = StubDatabase()
        pubsub = StubPubSub()
        object_storage = StubObjectStorage()
        cache = StubCache()
        feature_flags = StubFeatureFlags()
        tracer = StubTracer()
        
        services = PlatformServices(
            logger=logger,
            config=config,
            secrets=secrets,
            db=db,
            pubsub=pubsub,
            object_storage=object_storage,
            cache=cache,
            feature_flags=feature_flags,
            tracer=tracer
        )
        
        # Verify all services are stored
        assert services.logger is logger
        assert services.config is config
        assert services.secrets is secrets
        assert services.db is db
        assert services.pubsub is pubsub
        assert services.object_storage is object_storage
        assert services.cache is cache
        assert services.feature_flags is feature_flags
        assert services.tracer is tracer


class TestCreatePlatformServices:
    """Test create_platform_services factory function"""

    def test_create_platform_services__with_defaults__should_create_all_services(self):
        """Factory should create all services with default configuration"""
        with patch.dict(os.environ, {}, clear=True):
            services = create_platform_services()
            
            # Verify all services are created
            assert isinstance(services.logger, ConsoleLogger)
            assert isinstance(services.config, EnvironmentConfig)
            assert isinstance(services.secrets, StubSecrets)
            assert isinstance(services.db, StubDatabase)
            assert isinstance(services.pubsub, StubPubSub)
            assert isinstance(services.object_storage, StubObjectStorage)
            assert isinstance(services.cache, StubCache)
            assert isinstance(services.feature_flags, StubFeatureFlags)
            assert isinstance(services.tracer, StubTracer)

    def test_create_platform_services__with_service_name__should_configure_logger(self):
        """Factory should configure logger with provided service name"""
        services = create_platform_services(service_name="test-service")
        
        assert services.logger.base_fields["service"] == "test-service"

    def test_create_platform_services__with_environment__should_configure_logger(self):
        """Factory should configure logger with provided environment"""
        services = create_platform_services(environment="production")
        
        assert services.logger.base_fields["environment"] == "production"

    def test_create_platform_services__with_logger_context__should_add_context_fields(self):
        """Factory should add logger context fields"""
        context = {
            "version": "2.0.0",
            "region": "us-west-2",
            "custom_field": "custom_value"
        }
        
        services = create_platform_services(logger_context=context)
        
        assert services.logger.base_fields["version"] == "2.0.0"
        assert services.logger.base_fields["region"] == "us-west-2"
        assert services.logger.base_fields["custom_field"] == "custom_value"

    def test_create_platform_services__environment_detection__should_use_environment_vars(self):
        """Factory should detect environment from environment variables"""
        # Test ENVIRONMENT variable
        with patch.dict(os.environ, {"ENVIRONMENT": "staging"}):
            services = create_platform_services()
            assert services.logger.base_fields["environment"] == "staging"
        
        # Test NODE_ENV fallback
        with patch.dict(os.environ, {"NODE_ENV": "test"}, clear=True):
            services = create_platform_services()
            assert services.logger.base_fields["environment"] == "test"
        
        # Test ENVIRONMENT precedence over NODE_ENV
        with patch.dict(os.environ, {"ENVIRONMENT": "production", "NODE_ENV": "development"}):
            services = create_platform_services()
            assert services.logger.base_fields["environment"] == "production"

    def test_create_platform_services__should_inject_logger_into_stubs(self):
        """Factory should inject logger into all stub services"""
        services = create_platform_services(service_name="test-service")
        
        # All stub services should have the same logger instance
        assert services.secrets.logger is services.logger
        assert services.db.logger is services.logger
        assert services.pubsub.logger is services.logger
        assert services.object_storage.logger is services.logger
        assert services.cache.logger is services.logger
        assert services.feature_flags.logger is services.logger
        assert services.tracer.logger is services.logger

    def test_create_platform_services__should_log_initialization(self):
        """Factory should log successful service initialization"""
        from io import StringIO
        import sys
        import json
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            services = create_platform_services(service_name="test-service")
            
            output = mock_stdout.getvalue()
            
            # Should contain initialization log
            assert "Platform services initialized" in output
            
            # Parse the JSON log entry
            log_lines = [line for line in output.strip().split('\n') if line]
            log_data = json.loads(log_lines[-1])  # Get last log entry
            
            assert log_data["msg"] == "Platform services initialized"
            assert log_data["service_name"] == "test-service"
            assert log_data["use_stubs"] is True
            assert "services_created" in log_data

    def test_create_platform_services__use_stubs_parameter__should_be_passed_to_logger(self):
        """Factory should pass use_stubs parameter to initialization log"""
        from io import StringIO
        import sys
        import json
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            services = create_platform_services(use_stubs=False)
            
            output = mock_stdout.getvalue()
            log_lines = [line for line in output.strip().split('\n') if line]
            log_data = json.loads(log_lines[-1])
            
            assert log_data["use_stubs"] is False

    def test_create_platform_services__with_complex_configuration__should_handle_all_options(self):
        """Factory should handle complex configuration scenarios"""
        context = {
            "version": "1.2.3",
            "build": "abc123",
            "feature_set": "premium"
        }
        
        services = create_platform_services(
            service_name="complex-service",
            environment="staging",
            logger_context=context,
            use_stubs=True
        )
        
        # Verify logger configuration
        logger_fields = services.logger.base_fields
        assert logger_fields["service"] == "complex-service"
        assert logger_fields["environment"] == "staging"
        assert logger_fields["version"] == "1.2.3"
        assert logger_fields["build"] == "abc123"
        assert logger_fields["feature_set"] == "premium"
        
        # Verify all services are properly created
        assert isinstance(services.config, EnvironmentConfig)
        assert isinstance(services.secrets, StubSecrets)


class TestCreateTestPlatformServices:
    """Test create_test_platform_services factory function"""

    def test_create_test_platform_services__should_create_test_configured_services(self):
        """Test factory should create services configured for testing"""
        services = create_test_platform_services()
        
        # Verify all services are created
        assert isinstance(services.logger, ConsoleLogger)
        assert isinstance(services.config, EnvironmentConfig)
        assert isinstance(services.secrets, StubSecrets)
        assert isinstance(services.db, StubDatabase)
        assert isinstance(services.pubsub, StubPubSub)
        assert isinstance(services.object_storage, StubObjectStorage)
        assert isinstance(services.cache, StubCache)
        assert isinstance(services.feature_flags, StubFeatureFlags)
        assert isinstance(services.tracer, StubTracer)

    def test_create_test_platform_services__should_configure_test_environment(self):
        """Test factory should configure test environment"""
        services = create_test_platform_services()
        
        logger_fields = services.logger.base_fields
        assert logger_fields["service"] == "test-service"
        assert logger_fields["environment"] == "test"
        assert logger_fields["test_run"] is True

    def test_create_test_platform_services__with_custom_service_name__should_use_custom_name(self):
        """Test factory should accept custom service name"""
        services = create_test_platform_services("custom-test-service")
        
        assert services.logger.base_fields["service"] == "custom-test-service"

    def test_create_test_platform_services__should_always_use_stubs(self):
        """Test factory should always use stub implementations"""
        from io import StringIO
        import sys
        import json
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            services = create_test_platform_services()
            
            output = mock_stdout.getvalue()
            log_lines = [line for line in output.strip().split('\n') if line]
            log_data = json.loads(log_lines[-1])
            
            assert log_data["use_stubs"] is True


class TestFactoryIntegration:
    """Integration tests for factory functions"""

    @pytest.mark.asyncio
    async def test_factory_services__should_work_together__end_to_end(self):
        """Factory-created services should work together in end-to-end scenario"""
        services = create_platform_services(
            service_name="integration-test",
            environment="test",
            logger_context={"test_scenario": "e2e"}
        )
        
        # Test logger functionality
        from io import StringIO
        import sys
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            services.logger.info("Integration test started", {"step": 1})
            
            output = mock_stdout.getvalue()
            assert "Integration test started" in output
        
        # Test config functionality
        with patch.dict(os.environ, {"TEST_CONFIG": "integration_value"}):
            config_value = services.config.get("TEST_CONFIG")
            assert config_value == "integration_value"
        
        # Test secrets functionality
        secret_value = await services.secrets.get("TEST_SECRET")
        assert secret_value == "stub-secret-TEST_SECRET"
        
        # Test database functionality
        query_result = await services.db.query("SELECT 1")
        assert query_result == []
        
        # Test pub/sub functionality
        await services.pubsub.publish("test.event", {"data": "test"})
        events = services.pubsub.get_event_history()
        assert len(events) == 1
        assert events[0].type == "test.event"
        
        # Test cache functionality
        await services.cache.set("test_key", "test_value")
        cached_value = await services.cache.get("test_key")
        assert cached_value == "test_value"
        
        # Test feature flags functionality
        flag_enabled = await services.feature_flags.is_enabled("test_flag")
        assert flag_enabled is True
        
        # Test tracing functionality
        async def traced_operation():
            return "traced_result"
        
        result = await services.tracer.start_span("test_span", traced_operation)
        assert result == "traced_result"

    def test_factory_dependency_injection__should_create_consistent_logger_instances(self):
        """Factory should inject the same logger instance across all services"""
        services = create_platform_services()
        
        # All services should share the same logger instance
        logger_instances = [
            services.logger,
            services.secrets.logger,
            services.db.logger,
            services.pubsub.logger,
            services.object_storage.logger,
            services.cache.logger,
            services.feature_flags.logger,
            services.tracer.logger
        ]
        
        # All should be the same instance
        for logger_instance in logger_instances[1:]:
            assert logger_instance is services.logger

    def test_multiple_factory_calls__should_create_independent_services(self):
        """Multiple factory calls should create independent service instances"""
        services1 = create_platform_services(service_name="service-1")
        services2 = create_platform_services(service_name="service-2")
        
        # Should be different instances
        assert services1 is not services2
        assert services1.logger is not services2.logger
        assert services1.config is not services2.config
        
        # Should have different service names
        assert services1.logger.base_fields["service"] == "service-1"
        assert services2.logger.base_fields["service"] == "service-2"