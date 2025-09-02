"""
Test suite for platform interfaces and interface validation.
Ensures all interfaces are properly defined and can be imported.
"""

import pytest
from abc import ABC
from typing import get_origin, get_args
import inspect

from platform_py.interfaces import (
    Logger, Config, Secrets, Db, EventEnvelope, PubSub, 
    ObjectStorage, Cache, FeatureFlags, Tracer
)


class TestInterfaceDefinitions:
    """Test that all platform interfaces are properly defined"""

    def test_logger_interface__should_be_abstract_base_class(self):
        """Logger should be an abstract base class"""
        assert issubclass(Logger, ABC)
        assert hasattr(Logger, '__abstractmethods__')
        
        # Check required abstract methods
        abstract_methods = Logger.__abstractmethods__
        expected_methods = {'info', 'error', 'warn', 'debug', 'with_fields'}
        assert expected_methods.issubset(abstract_methods)

    def test_config_interface__should_be_abstract_base_class(self):
        """Config should be an abstract base class with required methods"""
        assert issubclass(Config, ABC)
        
        abstract_methods = Config.__abstractmethods__
        expected_methods = {'get', 'get_int', 'get_bool', 'get_float'}
        assert expected_methods.issubset(abstract_methods)

    def test_secrets_interface__should_be_abstract_base_class(self):
        """Secrets should be an abstract base class"""
        assert issubclass(Secrets, ABC)
        assert 'get' in Secrets.__abstractmethods__

    def test_db_interface__should_be_abstract_base_class(self):
        """Database should be an abstract base class"""
        assert issubclass(Db, ABC)
        
        abstract_methods = Db.__abstractmethods__
        expected_methods = {'query', 'execute', 'with_tx'}
        assert expected_methods.issubset(abstract_methods)

    def test_pubsub_interface__should_be_abstract_base_class(self):
        """PubSub should be an abstract base class"""
        assert issubclass(PubSub, ABC)
        
        abstract_methods = PubSub.__abstractmethods__
        expected_methods = {'publish', 'subscribe'}
        assert expected_methods.issubset(abstract_methods)

    def test_object_storage_interface__should_be_abstract_base_class(self):
        """ObjectStorage should be an abstract base class"""
        assert issubclass(ObjectStorage, ABC)
        
        abstract_methods = ObjectStorage.__abstractmethods__
        expected_methods = {'put', 'get', 'presign_put', 'presign_get', 'delete'}
        assert expected_methods.issubset(abstract_methods)

    def test_cache_interface__should_be_abstract_base_class(self):
        """Cache should be an abstract base class"""
        assert issubclass(Cache, ABC)
        
        abstract_methods = Cache.__abstractmethods__
        expected_methods = {'get', 'set', 'delete', 'exists'}
        assert expected_methods.issubset(abstract_methods)

    def test_feature_flags_interface__should_be_abstract_base_class(self):
        """FeatureFlags should be an abstract base class"""
        assert issubclass(FeatureFlags, ABC)
        
        abstract_methods = FeatureFlags.__abstractmethods__
        expected_methods = {'is_enabled', 'get_value'}
        assert expected_methods.issubset(abstract_methods)

    def test_tracer_interface__should_be_abstract_base_class(self):
        """Tracer should be an abstract base class"""
        assert issubclass(Tracer, ABC)
        
        abstract_methods = Tracer.__abstractmethods__
        expected_methods = {'start_span', 'get_current_trace_id', 'with_span'}
        assert expected_methods.issubset(abstract_methods)


class TestEventEnvelope:
    """Test EventEnvelope data class"""

    def test_event_envelope__should_have_required_attributes(self):
        """EventEnvelope should have all required attributes"""
        envelope = EventEnvelope(
            id="test-id",
            type="test-event",
            occurred_at="2023-01-01T00:00:00Z",
            payload={"test": "data"},
            idempotency_key="test-key",
            trace={"traceparent": "test-trace"}
        )
        
        assert envelope.id == "test-id"
        assert envelope.type == "test-event"
        assert envelope.occurred_at == "2023-01-01T00:00:00Z"
        assert envelope.payload == {"test": "data"}
        assert envelope.idempotency_key == "test-key"
        assert envelope.trace == {"traceparent": "test-trace"}

    def test_event_envelope__should_support_any_payload_type(self):
        """EventEnvelope should accept any type as payload"""
        # Test with different payload types
        test_cases = [
            {"dict": "payload"},
            ["list", "payload"],
            "string_payload",
            123,
            True,
            None
        ]
        
        for payload in test_cases:
            envelope = EventEnvelope(
                id="test",
                type="test",
                occurred_at="2023-01-01T00:00:00Z",
                payload=payload,
                idempotency_key="test",
                trace={}
            )
            assert envelope.payload == payload


class TestInterfaceMethodSignatures:
    """Test that interface methods have correct signatures"""

    def test_logger_methods__should_have_correct_signatures(self):
        """Logger methods should have expected signatures"""
        # Check info method
        info_sig = inspect.signature(Logger.info)
        assert len(info_sig.parameters) == 3  # self, msg, meta
        
        # Check with_fields method  
        with_fields_sig = inspect.signature(Logger.with_fields)
        assert len(with_fields_sig.parameters) == 2  # self, fields

    def test_config_methods__should_have_correct_signatures(self):
        """Config methods should have expected signatures"""
        get_sig = inspect.signature(Config.get)
        assert len(get_sig.parameters) == 4  # self, key, required, default
        
        get_int_sig = inspect.signature(Config.get_int)
        assert len(get_int_sig.parameters) == 4  # self, key, required, default

    def test_db_methods__should_have_correct_signatures(self):
        """Database methods should have expected signatures"""
        query_sig = inspect.signature(Db.query)
        assert len(query_sig.parameters) == 3  # self, sql, params
        
        execute_sig = inspect.signature(Db.execute)
        assert len(execute_sig.parameters) == 3  # self, sql, params
        
        with_tx_sig = inspect.signature(Db.with_tx)
        assert len(with_tx_sig.parameters) == 2  # self, fn

    def test_pubsub_methods__should_have_correct_signatures(self):
        """PubSub methods should have expected signatures"""
        publish_sig = inspect.signature(PubSub.publish)
        assert len(publish_sig.parameters) == 4  # self, topic, event, idempotency_key
        
        subscribe_sig = inspect.signature(PubSub.subscribe)
        assert len(subscribe_sig.parameters) == 3  # self, topic, handler