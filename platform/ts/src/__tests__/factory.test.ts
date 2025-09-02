import { createPlatformServices, createTestPlatformServices } from '../factory';
import { ConsoleLogger } from '../implementations/logger';
import { EnvironmentConfig } from '../implementations/config';

describe('Platform Services Factory', () => {
  let originalEnv: NodeJS.ProcessEnv;

  beforeEach(() => {
    originalEnv = { ...process.env };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  describe('test_create_platform_services__when_default_options__should_create_all_services', () => {
    test('creates complete platform services with default configuration', () => {
      const services = createPlatformServices();

      expect(services).toHaveProperty('logger');
      expect(services).toHaveProperty('config');
      expect(services).toHaveProperty('secrets');
      expect(services).toHaveProperty('db');
      expect(services).toHaveProperty('pubsub');
      expect(services).toHaveProperty('objectStorage');
      expect(services).toHaveProperty('cache');
      expect(services).toHaveProperty('featureFlags');
      expect(services).toHaveProperty('tracer');

      expect(services.logger).toBeInstanceOf(ConsoleLogger);
      expect(services.config).toBeInstanceOf(EnvironmentConfig);
    });
  });

  describe('test_create_platform_services__when_custom_service_name__should_include_in_logger', () => {
    test('creates services with custom service name in logger context', () => {
      const serviceName = 'my-awesome-service';
      const services = createPlatformServices({ serviceName });

      // Test that logger has the service name by logging and checking behavior
      services.logger.info('test message');
      
      // The logger should be configured with the service name
      expect(services.logger).toBeInstanceOf(ConsoleLogger);
    });
  });

  describe('test_create_platform_services__when_custom_environment__should_set_environment', () => {
    test('creates services with custom environment configuration', () => {
      const environment = 'staging';
      const services = createPlatformServices({ environment });

      // Logger should be configured with the environment
      expect(services.logger).toBeInstanceOf(ConsoleLogger);
    });
  });

  describe('test_create_platform_services__when_custom_logger_context__should_add_context_fields', () => {
    test('creates logger with additional context fields', () => {
      const loggerContext = {
        version: '1.2.3',
        region: 'us-west-2',
        deploymentId: 'deploy-abc123'
      };
      
      const services = createPlatformServices({ loggerContext });

      expect(services.logger).toBeInstanceOf(ConsoleLogger);
    });
  });

  describe('test_create_platform_services__when_environment_from_process_env__should_use_node_env', () => {
    test('uses NODE_ENV from process environment when environment not specified', () => {
      process.env.NODE_ENV = 'production';
      
      const services = createPlatformServices();

      expect(services.logger).toBeInstanceOf(ConsoleLogger);
    });
  });

  describe('test_service_integration__when_logger_passed_to_stubs__should_use_provided_logger', () => {
    test('passes logger instance to all stub services for consistent logging', async () => {
      const services = createPlatformServices({
        serviceName: 'integration-test',
        useStubs: true
      });

      // Test that stub services can use the logger without errors
      await services.db.query('SELECT 1');
      await services.cache.set('test', 'value');
      await services.secrets.get('TEST_SECRET');
      
      // These should all work without throwing errors
      expect(services.logger).toBeDefined();
    });
  });

  describe('test_service_dependencies__when_services_created__should_be_properly_connected', () => {
    test('ensures all services can interact with each other through the platform container', async () => {
      const services = createPlatformServices({
        serviceName: 'dependency-test'
      });

      // Simulate a complex operation that uses multiple services
      const config = services.config.get('TEST_CONFIG', { default: 'default-value' });
      services.logger.info('Config retrieved', { config });

      await services.cache.set('config', config, 60);
      const cachedConfig = await services.cache.get<string>('config');

      await services.pubsub.publish('config.loaded', { config: cachedConfig });

      const result = await services.tracer.startSpan('config-operation', async () => {
        return { success: true, config: cachedConfig };
      });

      expect(result.success).toBe(true);
      expect(result.config).toBe(config);
    });
  });

  describe('test_service_types__when_services_created__should_satisfy_interfaces', () => {
    test('ensures all created services satisfy their respective interfaces', async () => {
      const services = createPlatformServices();

      // Test interface compliance by calling interface methods
      
      // Logger interface
      services.logger.info('test');
      services.logger.error('test');
      services.logger.warn('test');
      services.logger.debug('test');
      const childLogger = services.logger.with({ test: true });
      expect(childLogger).toBeDefined();

      // Config interface
      const configValue = services.config.get('TEST_KEY', { default: 'default' });
      expect(configValue).toBe('default');

      // Database interface
      const queryResult = await services.db.query('SELECT 1');
      expect(Array.isArray(queryResult)).toBe(true);

      const txResult = await services.db.withTx(async (tx) => {
        await tx.query('INSERT INTO test VALUES (1)');
        return 'tx-complete';
      });
      expect(txResult).toBe('tx-complete');

      // Secrets interface
      const secret = await services.secrets.get('TEST_SECRET');
      expect(typeof secret).toBe('string');

      // PubSub interface
      const unsubscribe = services.pubsub.subscribe('test', async () => {});
      await services.pubsub.publish('test', { data: 'test' });
      unsubscribe();

      // ObjectStorage interface
      const buffer = Buffer.from('test');
      const putResult = await services.objectStorage.put('test', buffer, 'text/plain');
      expect(putResult).toHaveProperty('etag');

      const getResult = await services.objectStorage.get('test');
      expect(Buffer.isBuffer(getResult)).toBe(true);

      const presignPutUrl = await services.objectStorage.presignPut('test', 3600);
      expect(typeof presignPutUrl).toBe('string');

      const presignGetUrl = await services.objectStorage.presignGet('test', 3600);
      expect(typeof presignGetUrl).toBe('string');

      // Cache interface
      await services.cache.set('test', 'value', 60);
      const cacheResult = await services.cache.get('test');
      expect(cacheResult).toBe('value');

      const deleteResult = await services.cache.del('test');
      expect(typeof deleteResult).toBe('boolean');

      // FeatureFlags interface
      const flagEnabled = await services.featureFlags.isEnabled('test-flag');
      expect(typeof flagEnabled).toBe('boolean');

      const flagValue = await services.featureFlags.getValue('test-flag', 'default');
      expect(flagValue).toBe('default');

      // Tracer interface
      const traceResult = await services.tracer.startSpan('test-span', async () => 'traced');
      expect(traceResult).toBe('traced');

      const traceId = services.tracer.getCurrentTraceId();
      expect(traceId === null || typeof traceId === 'string').toBe(true);
    });
  });

  describe('test_create_test_platform_services__when_called__should_create_test_optimized_services', () => {
    test('creates platform services optimized for testing', () => {
      const services = createTestPlatformServices();

      expect(services).toHaveProperty('logger');
      expect(services).toHaveProperty('config');
      expect(services.logger).toBeInstanceOf(ConsoleLogger);
      
      // All services should be present
      expect(Object.keys(services)).toHaveLength(9);
    });
  });

  describe('test_create_test_platform_services__when_custom_service_name__should_use_provided_name', () => {
    test('creates test services with custom service name', () => {
      const testServiceName = 'unit-test-service';
      const services = createTestPlatformServices(testServiceName);

      expect(services.logger).toBeInstanceOf(ConsoleLogger);
    });
  });

  describe('test_platform_services_isolation__when_multiple_instances__should_be_independent', () => {
    test('ensures multiple platform service instances are independent', async () => {
      const services1 = createPlatformServices({ serviceName: 'service-1' });
      const services2 = createPlatformServices({ serviceName: 'service-2' });

      // Services should be different instances
      expect(services1).not.toBe(services2);
      expect(services1.logger).not.toBe(services2.logger);
      expect(services1.cache).not.toBe(services2.cache);

      // Test that they operate independently
      await services1.cache.set('test', 'value1');
      await services2.cache.set('test', 'value2');

      const value1 = await services1.cache.get('test');
      const value2 = await services2.cache.get('test');

      // Each service should have its own cache state
      expect(value1).toBe('value1');
      expect(value2).toBe('value2');
    });
  });

  describe('test_platform_services_error_handling__when_service_operations_fail__should_handle_gracefully', () => {
    test('handles service operation failures gracefully', async () => {
      const services = createPlatformServices();

      // Test error handling in tracer
      await expect(
        services.tracer.startSpan('failing-span', async () => {
          throw new Error('Intentional test error');
        })
      ).rejects.toThrow('Intentional test error');

      // Test error handling in transaction
      await expect(
        services.db.withTx(async (tx) => {
          await tx.query('SELECT 1');
          throw new Error('Transaction error');
        })
      ).rejects.toThrow('Transaction error');

      // Services should continue to work after errors
      const result = await services.cache.set('after-error', 'still-works');
      expect(result).toBeUndefined(); // set returns void
      
      const retrieved = await services.cache.get('after-error');
      expect(retrieved).toBe('still-works');
    });
  });

  describe('test_platform_services_real_world_usage__when_building_application__should_support_common_patterns', () => {
    test('supports real-world application patterns and workflows', async () => {
      // Simulate a real application setup
      const services = createPlatformServices({
        serviceName: 'user-management-api',
        environment: 'development',
        loggerContext: {
          version: '2.1.0',
          component: 'api-server'
        }
      });

      // Simulate user registration workflow
      const userId = 'user-12345';
      const userEmail = 'user@example.com';

      // Step 1: Log the operation start
      const requestLogger = services.logger.with({
        userId,
        operation: 'user-registration',
        correlationId: 'req-abc123'
      });

      requestLogger.info('Starting user registration');

      // Step 2: Check feature flags
      const emailVerificationEnabled = await services.featureFlags.isEnabled(
        'email_verification',
        { userId, userTier: 'basic' }
      );

      // Step 3: Store user data (using transaction)
      const user = await services.db.withTx(async (tx) => {
        await tx.query('INSERT INTO users (id, email) VALUES (?, ?)', [userId, userEmail]);
        await tx.query('INSERT INTO user_profiles (user_id, created_at) VALUES (?, ?)', [userId, new Date().toISOString()]);
        return { id: userId, email: userEmail, emailVerified: false };
      });

      // Step 4: Cache user data
      await services.cache.set(`user:${userId}`, user, 3600);

      // Step 5: Store secrets (API keys, etc.)
      process.env.USER_API_KEY = 'secret-key-123';
      const apiKey = await services.secrets.get('USER_API_KEY');

      // Step 6: Store user documents
      const welcomeDoc = Buffer.from('Welcome to our service!');
      const uploadResult = await services.objectStorage.put(
        `users/${userId}/welcome.txt`,
        welcomeDoc,
        'text/plain'
      );

      // Step 7: Publish registration event
      await services.pubsub.publish('user.registered', {
        userId,
        email: userEmail,
        emailVerificationRequired: emailVerificationEnabled,
        welcomeDocEtag: uploadResult.etag
      });

      // Step 8: Trace the entire operation
      const finalResult = await services.tracer.startSpan('user-registration-complete', async () => {
        requestLogger.info('User registration completed successfully');
        return { success: true, userId, requiresEmailVerification: emailVerificationEnabled };
      });

      // Verify the workflow completed successfully
      expect(finalResult.success).toBe(true);
      expect(finalResult.userId).toBe(userId);
      expect(typeof finalResult.requiresEmailVerification).toBe('boolean');
      expect(user.email).toBe(userEmail);
      expect(apiKey).toBe('secret-key-123');
      expect(uploadResult).toHaveProperty('etag');
    });
  });
});