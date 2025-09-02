/**
 * Core platform interfaces that define the contracts for all infrastructure services.
 * These interfaces abstract away cloud provider specifics and enable testability.
 */

/**
 * Structured logging interface with contextual metadata support
 */
export interface Logger {
  info(msg: string, meta?: Record<string, unknown>): void;
  error(msg: string, meta?: Record<string, unknown>): void;
  warn(msg: string, meta?: Record<string, unknown>): void;
  debug(msg: string, meta?: Record<string, unknown>): void;
  with(fields: Record<string, unknown>): Logger;
}

/**
 * Configuration management interface for environment variables and settings
 */
export interface Config {
  get<T = string>(key: string, opts?: { required?: boolean; default?: T }): T;
}

/**
 * Secure secrets management interface
 */
export interface Secrets {
  get(name: string): Promise<string>;
}

/**
 * Database interface with connection pooling and transaction support
 */
export interface Db {
  query<T>(sql: string, params?: unknown[]): Promise<T[]>;
  withTx<T>(fn: (tx: Db) => Promise<T>): Promise<T>;
}

/**
 * Object storage interface for file operations (S3-like)
 */
export interface ObjectStorage {
  put(key: string, data: Buffer, contentType: string): Promise<{ etag: string }>;
  get(key: string): Promise<Buffer>;
  presignPut(key: string, expiresInSeconds: number): Promise<string>;
  presignGet(key: string, expiresInSeconds: number): Promise<string>;
}

/**
 * Cache interface for high-performance data storage (Redis-like)
 */
export interface Cache {
  get<T>(key: string): Promise<T | null>;
  set<T>(key: string, value: T, ttlSeconds?: number): Promise<void>;
  del(key: string): Promise<boolean>;
}

/**
 * Event envelope for all published events
 */
export interface EventEnvelope {
  id: string;
  type: string;
  occurredAt: string;
  payload: unknown;
  idempotencyKey: string;
  trace?: {
    traceparent?: string;
  };
}

/**
 * Pub/Sub interface for event-driven communication
 */
export interface PubSub {
  publish(topic: string, event: unknown, opts?: { idempotencyKey?: string }): Promise<void>;
  subscribe(topic: string, handler: (e: EventEnvelope) => Promise<void>): () => void;
}

/**
 * Feature flags interface for runtime configuration
 */
export interface FeatureFlags {
  isEnabled(flag: string, context?: Record<string, unknown>): Promise<boolean>;
  getValue<T>(flag: string, defaultValue: T, context?: Record<string, unknown>): Promise<T>;
}

/**
 * Distributed tracing interface
 */
export interface Tracer {
  startSpan<T>(name: string, fn: () => Promise<T>): Promise<T>;
  getCurrentTraceId(): string | null;
}