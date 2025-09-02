import { 
  Logger, 
  Config, 
  Secrets, 
  Db, 
  PubSub, 
  ObjectStorage, 
  Cache, 
  FeatureFlags, 
  Tracer 
} from './interfaces';

import { ConsoleLogger } from './implementations/logger';
import { EnvironmentConfig } from './implementations/config';
import { 
  StubDatabase, 
  StubSecrets, 
  StubPubSub, 
  StubObjectStorage, 
  StubCache, 
  StubFeatureFlags, 
  StubTracer 
} from './implementations/stubs';

/**
 * Platform services container that provides all infrastructure dependencies
 */
export interface PlatformServices {
  logger: Logger;
  config: Config;
  secrets: Secrets;
  db: Db;
  pubsub: PubSub;
  objectStorage: ObjectStorage;
  cache: Cache;
  featureFlags: FeatureFlags;
  tracer: Tracer;
}

/**
 * Configuration options for creating platform services
 */
export interface PlatformServicesOptions {
  /** Service name for logging context */
  serviceName?: string;
  /** Environment (development, staging, production) */
  environment?: string;
  /** Additional logger context fields */
  loggerContext?: Record<string, unknown>;
  /** Use stub implementations for development/testing */
  useStubs?: boolean;
}

/**
 * Factory function to create a complete set of platform services.
 * Uses stub implementations by default for easy development setup.
 * 
 * @param options Configuration options
 * @returns Complete platform services container
 * 
 * @example
 * ```typescript
 * import { createPlatformServices } from '@spark/platform-ts';
 * 
 * // Development setup with stubs
 * const platform = createPlatformServices({
 *   serviceName: 'my-service',
 *   useStubs: true
 * });
 * 
 * // Use the services
 * platform.logger.info('Service starting');
 * const dbUsers = await platform.db.query('SELECT * FROM users');
 * await platform.pubsub.publish('user.created', { userId: 123 });
 * ```
 */
export function createPlatformServices(options: PlatformServicesOptions = {}): PlatformServices {
  const {
    serviceName = 'unknown-service',
    environment = process.env.NODE_ENV || 'development',
    loggerContext = {},
    useStubs = true
  } = options;

  // Create logger first as other services may need it
  const logger = new ConsoleLogger({
    service: serviceName,
    environment,
    ...loggerContext
  });

  // Create config service
  const config = new EnvironmentConfig();

  // Create other services - use stubs by default for easy development
  const services: PlatformServices = {
    logger,
    config,
    secrets: new StubSecrets(logger),
    db: new StubDatabase(logger),
    pubsub: new StubPubSub(logger),
    objectStorage: new StubObjectStorage(logger),
    cache: new StubCache(logger),
    featureFlags: new StubFeatureFlags(logger),
    tracer: new StubTracer(logger)
  };

  logger.info('Platform services initialized', {
    serviceName,
    environment,
    useStubs,
    servicesCreated: Object.keys(services)
  });

  return services;
}

/**
 * Creates platform services specifically configured for testing.
 * Always uses stub implementations with minimal logging.
 */
export function createTestPlatformServices(serviceName = 'test-service'): PlatformServices {
  return createPlatformServices({
    serviceName,
    environment: 'test',
    useStubs: true,
    loggerContext: {
      testRun: true
    }
  });
}