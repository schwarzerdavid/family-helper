import { Db, Secrets, PubSub, EventEnvelope, ObjectStorage, Cache, FeatureFlags, Tracer, Logger } from '../interfaces';

/**
 * Simple console-based logger fallback for when no logger is provided
 */
const createConsoleLogger = (): Logger => ({
  info: (msg: string, meta?: Record<string, unknown>) => {
    const entry = { level: 'info', msg, ts: new Date().toISOString(), ...meta };
    console.log(JSON.stringify(entry));
  },
  error: (msg: string, meta?: Record<string, unknown>) => {
    const entry = { level: 'error', msg, ts: new Date().toISOString(), ...meta };
    console.error(JSON.stringify(entry));
  },
  warn: (msg: string, meta?: Record<string, unknown>) => {
    const entry = { level: 'warn', msg, ts: new Date().toISOString(), ...meta };
    console.warn(JSON.stringify(entry));
  },
  debug: (msg: string, meta?: Record<string, unknown>) => {
    const entry = { level: 'debug', msg, ts: new Date().toISOString(), ...meta };
    console.log(JSON.stringify(entry));
  },
  with: (_fields: Record<string, unknown>) => createConsoleLogger() // Simplified for stubs
});

/**
 * Stub implementation of the Database interface for development and testing.
 * Logs all operations but doesn't perform actual database operations.
 */
export class StubDatabase implements Db {
  private transactionDepth = 0;
  private logger: Logger;

  constructor(logger?: Logger) {
    this.logger = logger || createConsoleLogger();
  }

  async query<T>(sql: string, params: unknown[] = []): Promise<T[]> {
    const prefix = this.transactionDepth > 0 ? '[TX] ' : '';
    const message = `${prefix}Stub database query executed`;
    const metadata = { sql, params, transactionDepth: this.transactionDepth };

    this.logger.debug(message, metadata);
    
    // Return empty array - real implementation would return actual data
    return [] as T[];
  }

  async withTx<T>(fn: (tx: Db) => Promise<T>): Promise<T> {
    this.logger.debug('Starting database transaction', { transactionDepth: this.transactionDepth });
    
    this.transactionDepth++;
    
    try {
      // Pass this same stub instance as the transaction database
      // Real implementation would use a transaction-scoped connection
      const result = await fn(this);
      
      this.logger.debug('Database transaction committed', { transactionDepth: this.transactionDepth - 1 });
      
      return result;
    } catch (error) {
      this.logger.error('Database transaction rolled back', { 
        error: error instanceof Error ? error.message : String(error),
        transactionDepth: this.transactionDepth - 1 
      });
      throw error;
    } finally {
      this.transactionDepth--;
    }
  }
}

/**
 * Stub implementation of the Secrets interface.
 * Falls back to environment variables for development.
 */
export class StubSecrets implements Secrets {
  private secretCache = new Map<string, string>();
  private logger: Logger;

  constructor(logger?: Logger) {
    this.logger = logger || createConsoleLogger();
  }

  async get(name: string): Promise<string> {
    this.logger.debug('Retrieving secret', { secretName: name });
    
    // Check cache first
    if (this.secretCache.has(name)) {
      this.logger.debug('Secret found in cache', { secretName: name });
      return this.secretCache.get(name)!;
    }
    
    // Fallback to environment variable
    const envValue = process.env[name];
    if (envValue) {
      this.logger.debug('Secret found in environment variables', { secretName: name });
      this.secretCache.set(name, envValue);
      return envValue;
    }
    
    // In real implementation, this would throw an error
    // For stub, we'll return a placeholder
    const placeholder = `stub-secret-${name}`;
    
    this.logger.warn('Secret not found, returning placeholder', { 
      secretName: name, 
      placeholder: placeholder 
    });
    
    this.secretCache.set(name, placeholder);
    return placeholder;
  }
}

/**
 * Stub implementation of the PubSub interface.
 * Provides in-memory event handling for development and testing.
 */
export class StubPubSub implements PubSub {
  private subscribers = new Map<string, Array<(event: EventEnvelope) => Promise<void>>>();
  private eventHistory: EventEnvelope[] = [];
  private logger: Logger;

  constructor(logger?: Logger) {
    this.logger = logger || createConsoleLogger();
  }

  async publish(topic: string, event: unknown, opts: { idempotencyKey?: string } = {}): Promise<void> {
    // Create event envelope
    const envelope: EventEnvelope = {
      id: this.generateUUID(),
      type: topic,
      occurredAt: new Date().toISOString(),
      payload: event,
      idempotencyKey: opts.idempotencyKey || this.generateUUID(),
      trace: {
        traceparent: this.getCurrentTraceId()
      }
    };

    this.logger.info('Publishing event to stub pub/sub', {
      topic,
      eventId: envelope.id,
      idempotencyKey: envelope.idempotencyKey,
      payloadType: typeof event,
      subscriberCount: this.subscribers.get(topic)?.length || 0
    });

    // Store in history for debugging
    this.eventHistory.push(envelope);
    
    // Keep only last 100 events to prevent memory leaks
    if (this.eventHistory.length > 100) {
      this.eventHistory.shift();
    }

    // Notify subscribers (simulate async processing)
    const handlers = this.subscribers.get(topic) || [];
    
    if (handlers.length === 0) {
      this.logger.debug('No subscribers found for topic', { topic });
    } else {
      this.logger.debug('Notifying subscribers', { topic, subscriberCount: handlers.length });
      
      // Process handlers asynchronously (don't await to simulate real pub/sub)
      setTimeout(async () => {
        for (const handler of handlers) {
          try {
            await handler(envelope);
          } catch (error) {
            this.logger.error('Event handler failed', {
              topic,
              eventId: envelope.id,
              error: error instanceof Error ? error.message : String(error)
            });
          }
        }
      }, 10); // Small delay to simulate network/queue latency
    }
  }

  subscribe(topic: string, handler: (event: EventEnvelope) => Promise<void>): () => void {
    this.logger.debug('Subscribing to topic', { topic });
    
    if (!this.subscribers.has(topic)) {
      this.subscribers.set(topic, []);
    }
    
    this.subscribers.get(topic)!.push(handler);
    
    // Return unsubscribe function
    return () => {
      this.logger.debug('Unsubscribing from topic', { topic });
      
      const handlers = this.subscribers.get(topic);
      if (handlers) {
        const index = handlers.indexOf(handler);
        if (index > -1) {
          handlers.splice(index, 1);
        }
        
        // Clean up empty topic arrays
        if (handlers.length === 0) {
          this.subscribers.delete(topic);
        }
      }
    };
  }

  /**
   * Debug method to see recent events (useful for development)
   */
  getEventHistory(): EventEnvelope[] {
    return [...this.eventHistory];
  }

  /**
   * Debug method to see current subscriptions
   */
  getSubscriptions(): Record<string, number> {
    const result: Record<string, number> = {};
    for (const [topic, handlers] of this.subscribers.entries()) {
      result[topic] = handlers.length;
    }
    return result;
  }

  private generateUUID(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  private getCurrentTraceId(): string | undefined {
    // In real implementation, this would extract from OpenTelemetry context
    return process.env.TRACE_ID || undefined;
  }
}

/**
 * Additional stub implementations for other interfaces
 */

export class StubObjectStorage implements ObjectStorage {
  private logger: Logger;

  constructor(logger?: Logger) {
    this.logger = logger || createConsoleLogger();
  }

  async put(key: string, data: Buffer, contentType: string): Promise<{ etag: string }> {
    this.logger.debug('Storing object in stub storage', { key, size: data.length, contentType });
    return { etag: `stub-etag-${Date.now()}` };
  }

  async get(key: string): Promise<Buffer> {
    this.logger.debug('Retrieving object from stub storage', { key });
    return Buffer.from(`stub-content-for-${key}`);
  }

  async presignPut(key: string, expiresInSeconds: number): Promise<string> {
    this.logger.debug('Generating presigned PUT URL', { key, expiresInSeconds });
    return `https://stub-storage.example.com/upload?key=${encodeURIComponent(key)}&expires=${expiresInSeconds}`;
  }

  async presignGet(key: string, expiresInSeconds: number): Promise<string> {
    this.logger.debug('Generating presigned GET URL', { key, expiresInSeconds });
    return `https://stub-storage.example.com/download?key=${encodeURIComponent(key)}&expires=${expiresInSeconds}`;
  }
}

export class StubCache implements Cache {
  private store = new Map<string, { value: unknown; expires?: number }>();
  private logger: Logger;

  constructor(logger?: Logger) {
    this.logger = logger || createConsoleLogger();
  }

  async get<T>(key: string): Promise<T | null> {
    this.logger.debug('Getting value from stub cache', { key });
    const entry = this.store.get(key);
    
    if (!entry) {
      this.logger.debug('Cache miss', { key });
      return null;
    }
    
    // Check expiration
    if (entry.expires && Date.now() > entry.expires) {
      this.logger.debug('Cache entry expired', { key, expiredAt: entry.expires });
      this.store.delete(key);
      return null;
    }
    
    this.logger.debug('Cache hit', { key });
    return entry.value as T;
  }

  async set<T>(key: string, value: T, ttlSeconds?: number): Promise<void> {
    const metadata: Record<string, unknown> = { key, hasTTL: !!ttlSeconds };
    if (ttlSeconds) {
      metadata.ttlSeconds = ttlSeconds;
    }
    this.logger.debug('Setting value in stub cache', metadata);
    
    const entry: { value: T; expires?: number } = { value };
    if (ttlSeconds) {
      entry.expires = Date.now() + (ttlSeconds * 1000);
    }
    
    this.store.set(key, entry);
  }

  async del(key: string): Promise<boolean> {
    this.logger.debug('Deleting value from stub cache', { key });
    const existed = this.store.delete(key);
    this.logger.debug('Cache deletion result', { key, existed });
    return existed;
  }
}

export class StubFeatureFlags implements FeatureFlags {
  private logger: Logger;

  constructor(logger?: Logger) {
    this.logger = logger || createConsoleLogger();
  }

  async isEnabled(flag: string, context?: Record<string, unknown>): Promise<boolean> {
    this.logger.debug('Checking feature flag enabled status', { flag, context, result: true });
    // Default to enabled for development
    return true;
  }

  async getValue<T>(flag: string, defaultValue: T, context?: Record<string, unknown>): Promise<T> {
    this.logger.debug('Getting feature flag value', { flag, defaultValue, context, result: defaultValue });
    return defaultValue;
  }
}

export class StubTracer implements Tracer {
  private logger: Logger;

  constructor(logger?: Logger) {
    this.logger = logger || createConsoleLogger();
  }

  async startSpan<T>(name: string, fn: () => Promise<T>): Promise<T> {
    const spanId = this.generateSpanId();
    this.logger.debug('Starting tracing span', { spanName: name, spanId });
    
    const startTime = Date.now();
    try {
      const result = await fn();
      const duration = Date.now() - startTime;
      this.logger.debug('Tracing span completed', { spanName: name, spanId, duration });
      return result;
    } catch (error) {
      const duration = Date.now() - startTime;
      this.logger.error('Tracing span failed', { 
        spanName: name, 
        spanId, 
        duration, 
        error: error instanceof Error ? error.message : String(error) 
      });
      throw error;
    }
  }

  getCurrentTraceId(): string | null {
    const traceId = process.env.TRACE_ID || null;
    this.logger.debug('Getting current trace ID', { traceId });
    return traceId;
  }

  private generateSpanId(): string {
    return Math.random().toString(16).substr(2, 8);
  }
}