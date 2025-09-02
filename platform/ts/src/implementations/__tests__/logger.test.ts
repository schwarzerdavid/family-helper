import { ConsoleLogger } from '../logger';

describe('ConsoleLogger', () => {
  let originalConsole: any;
  let mockConsole: any;

  beforeEach(() => {
    // Mock console methods to capture output
    originalConsole = {
      log: console.log,
      error: console.error,
      warn: console.warn,
      debug: console.debug
    };
    
    mockConsole = {
      log: jest.fn(),
      error: jest.fn(),
      warn: jest.fn(),
      debug: jest.fn()
    };

    console.log = mockConsole.log;
    console.error = mockConsole.error;
    console.warn = mockConsole.warn;
    console.debug = mockConsole.debug;
  });

  afterEach(() => {
    // Restore original console
    console.log = originalConsole.log;
    console.error = originalConsole.error;
    console.warn = originalConsole.warn;
    console.debug = originalConsole.debug;
  });

  describe('test_logger_creation__when_no_base_fields__should_use_defaults', () => {
    test('creates logger with default service and environment fields', () => {
      const logger = new ConsoleLogger();
      
      logger.info('test message');
      
      expect(mockConsole.log).toHaveBeenCalledTimes(1);
      const loggedData = JSON.parse(mockConsole.log.mock.calls[0][0]);
      
      expect(loggedData).toMatchObject({
        level: 'info',
        msg: 'test message',
        service: 'unknown',
        environment: 'test' // Jest sets NODE_ENV=test
      });
      expect(loggedData.timestamp).toBeDefined();
    });
  });

  describe('test_logger_creation__when_custom_base_fields__should_include_in_logs', () => {
    test('creates logger with custom base fields that appear in all logs', () => {
      const logger = new ConsoleLogger({
        service: 'user-service',
        version: '1.2.3',
        region: 'us-east-1'
      });
      
      logger.info('user created', { userId: 123 });
      
      expect(mockConsole.log).toHaveBeenCalledTimes(1);
      const loggedData = JSON.parse(mockConsole.log.mock.calls[0][0]);
      
      expect(loggedData).toMatchObject({
        level: 'info',
        msg: 'user created',
        service: 'user-service',
        version: '1.2.3',
        region: 'us-east-1',
        userId: 123
      });
    });
  });

  describe('test_info_logging__when_called_with_message__should_log_to_console_log', () => {
    test('logs info messages to console.log with proper format', () => {
      const logger = new ConsoleLogger({ service: 'test-service' });
      
      logger.info('Operation completed successfully');
      
      expect(mockConsole.log).toHaveBeenCalledTimes(1);
      expect(mockConsole.error).not.toHaveBeenCalled();
      expect(mockConsole.warn).not.toHaveBeenCalled();
      
      const loggedData = JSON.parse(mockConsole.log.mock.calls[0][0]);
      expect(loggedData.level).toBe('info');
      expect(loggedData.msg).toBe('Operation completed successfully');
    });
  });

  describe('test_error_logging__when_called_with_message__should_log_to_console_error', () => {
    test('logs error messages to console.error with proper format', () => {
      const logger = new ConsoleLogger({ service: 'test-service' });
      
      logger.error('Database connection failed', { errorCode: 'DB_CONN_001' });
      
      expect(mockConsole.error).toHaveBeenCalledTimes(1);
      expect(mockConsole.log).not.toHaveBeenCalled();
      
      const loggedData = JSON.parse(mockConsole.error.mock.calls[0][0]);
      expect(loggedData).toMatchObject({
        level: 'error',
        msg: 'Database connection failed',
        errorCode: 'DB_CONN_001'
      });
    });
  });

  describe('test_warn_logging__when_called_with_message__should_log_to_console_warn', () => {
    test('logs warning messages to console.warn with proper format', () => {
      const logger = new ConsoleLogger({ service: 'test-service' });
      
      logger.warn('Rate limit approaching', { currentRequests: 950, limit: 1000 });
      
      expect(mockConsole.warn).toHaveBeenCalledTimes(1);
      const loggedData = JSON.parse(mockConsole.warn.mock.calls[0][0]);
      
      expect(loggedData).toMatchObject({
        level: 'warn',
        msg: 'Rate limit approaching',
        currentRequests: 950,
        limit: 1000
      });
    });
  });

  describe('test_debug_logging__when_development_environment__should_log_messages', () => {
    test('logs debug messages in development environment', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';
      
      const logger = new ConsoleLogger({ service: 'test-service' });
      logger.debug('Cache miss for key', { cacheKey: 'user:123' });
      
      expect(mockConsole.debug).toHaveBeenCalledTimes(1);
      const loggedData = JSON.parse(mockConsole.debug.mock.calls[0][0]);
      
      expect(loggedData).toMatchObject({
        level: 'debug',
        msg: 'Cache miss for key',
        cacheKey: 'user:123'
      });
      
      process.env.NODE_ENV = originalEnv;
    });
  });

  describe('test_debug_logging__when_production_environment__should_not_log_messages', () => {
    test('does not log debug messages in production environment', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'production';
      
      const logger = new ConsoleLogger({ service: 'test-service' });
      logger.debug('This should not appear');
      
      expect(mockConsole.debug).not.toHaveBeenCalled();
      expect(mockConsole.log).not.toHaveBeenCalled();
      
      process.env.NODE_ENV = originalEnv;
    });
  });

  describe('test_debug_logging__when_debug_log_level_set__should_log_messages', () => {
    test('logs debug messages when LOG_LEVEL=debug regardless of NODE_ENV', () => {
      const originalEnv = process.env.NODE_ENV;
      const originalLogLevel = process.env.LOG_LEVEL;
      
      process.env.NODE_ENV = 'production';
      process.env.LOG_LEVEL = 'debug';
      
      const logger = new ConsoleLogger({ service: 'test-service' });
      logger.debug('Debug in production', { reason: 'troubleshooting' });
      
      expect(mockConsole.debug).toHaveBeenCalledTimes(1);
      
      process.env.NODE_ENV = originalEnv;
      process.env.LOG_LEVEL = originalLogLevel;
    });
  });

  describe('test_child_logger__when_created_with_additional_fields__should_include_parent_and_new_fields', () => {
    test('creates child logger that inherits parent context and adds new fields', () => {
      const parentLogger = new ConsoleLogger({ 
        service: 'api-gateway',
        version: '2.1.0'
      });
      
      const childLogger = parentLogger.with({ 
        requestId: 'req-123',
        userId: 'user-456' 
      });
      
      childLogger.info('Processing user request');
      
      expect(mockConsole.log).toHaveBeenCalledTimes(1);
      const loggedData = JSON.parse(mockConsole.log.mock.calls[0][0]);
      
      expect(loggedData).toMatchObject({
        level: 'info',
        msg: 'Processing user request',
        service: 'api-gateway',
        version: '2.1.0',
        requestId: 'req-123',
        userId: 'user-456'
      });
    });
  });

  describe('test_child_logger__when_field_conflicts_with_parent__should_override_parent_field', () => {
    test('child logger overrides parent fields when conflicts occur', () => {
      const parentLogger = new ConsoleLogger({ 
        service: 'parent-service',
        environment: 'staging'
      });
      
      const childLogger = parentLogger.with({ 
        service: 'child-service',  // This should override
        correlationId: 'corr-789'
      });
      
      childLogger.info('Child logger message');
      
      const loggedData = JSON.parse(mockConsole.log.mock.calls[0][0]);
      
      expect(loggedData.service).toBe('child-service'); // Overridden
      expect(loggedData.environment).toBe('staging'); // Inherited
      expect(loggedData.correlationId).toBe('corr-789'); // New field
    });
  });

  describe('test_metadata_merging__when_logging_with_runtime_metadata__should_combine_all_sources', () => {
    test('combines base fields, child fields, and runtime metadata correctly', () => {
      const logger = new ConsoleLogger({ service: 'order-service' });
      const childLogger = logger.with({ orderId: 'order-123' });
      
      childLogger.info('Order processed', { 
        amount: 99.99,
        currency: 'USD',
        orderId: 'order-456' // This should override the child logger field
      });
      
      const loggedData = JSON.parse(mockConsole.log.mock.calls[0][0]);
      
      expect(loggedData).toMatchObject({
        service: 'order-service',    // From base
        orderId: 'order-456',        // From runtime (overrides child)
        amount: 99.99,               // From runtime
        currency: 'USD'              // From runtime
      });
    });
  });

  describe('test_json_structure__when_logging_complex_objects__should_serialize_properly', () => {
    test('properly serializes complex nested objects and arrays', () => {
      const logger = new ConsoleLogger({ service: 'data-processor' });
      
      const complexData = {
        user: {
          id: 123,
          profile: {
            name: 'John Doe',
            preferences: ['email', 'sms']
          }
        },
        metrics: [
          { name: 'response_time', value: 150 },
          { name: 'cpu_usage', value: 45.2 }
        ]
      };
      
      logger.info('Processing complex data', complexData);
      
      const loggedData = JSON.parse(mockConsole.log.mock.calls[0][0]);
      
      expect(loggedData.user.id).toBe(123);
      expect(loggedData.user.profile.name).toBe('John Doe');
      expect(loggedData.user.profile.preferences).toEqual(['email', 'sms']);
      expect(loggedData.metrics).toHaveLength(2);
      expect(loggedData.metrics[0].name).toBe('response_time');
    });
  });

  describe('test_timestamp_format__when_logging_any_message__should_include_iso_timestamp', () => {
    test('includes ISO 8601 timestamp in every log entry', () => {
      const logger = new ConsoleLogger();
      const beforeTime = new Date().toISOString();
      
      logger.info('Timestamp test');
      
      const afterTime = new Date().toISOString();
      const loggedData = JSON.parse(mockConsole.log.mock.calls[0][0]);
      
      expect(loggedData.timestamp).toBeDefined();
      expect(loggedData.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);
      expect(loggedData.timestamp >= beforeTime).toBe(true);
      expect(loggedData.timestamp <= afterTime).toBe(true);
    });
  });
});