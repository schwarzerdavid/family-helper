/**
 * Main entry point for the TypeScript Platform Wrapper package.
 * Provides ready-to-use instances matching Phase 0 requirements.
 */

// Export all core interfaces
export * from './interfaces';

// Export concrete implementations for advanced usage
export { ConsoleLogger } from './implementations/logger';
export { EnvironmentConfig, ConfigError } from './implementations/config';
export {
  StubDatabase,
  StubSecrets,
  StubPubSub,
  StubObjectStorage,
  StubCache,
  StubFeatureFlags,
  StubTracer
} from './implementations/stubs';

// Export convenience factory functions
export { createPlatformServices } from './factory';

// Import what we need to create instances
import { Logger, Config, Secrets, Db, PubSub } from './interfaces';
import { ConsoleLogger } from './implementations/logger';
import { EnvironmentConfig } from './implementations/config';
import { StubSecrets, StubDatabase, StubPubSub } from './implementations/stubs';

// Export ready-to-use instances as required by Phase 0 implementation guide
export const logger: Logger = new ConsoleLogger({ service: 'platform' });
export const config: Config = new EnvironmentConfig();
export const secrets: Secrets = new StubSecrets();
export const db: Db = new StubDatabase();
export const pubsub: PubSub = new StubPubSub();