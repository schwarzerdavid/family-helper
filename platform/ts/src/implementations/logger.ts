import { Logger } from '../interfaces';

/**
 * Simple console-based logger implementation for development and basic production use.
 * Outputs structured JSON logs that can be easily parsed by log aggregation systems.
 */
export class ConsoleLogger implements Logger {
  private baseFields: Record<string, unknown>;

  constructor(baseFields: Record<string, unknown> = {}) {
    this.baseFields = {
      service: 'unknown',
      environment: process.env.NODE_ENV || 'development',
      ...baseFields
    };
  }

  info(msg: string, meta: Record<string, unknown> = {}): void {
    this.writeLog('info', msg, meta);
  }

  error(msg: string, meta: Record<string, unknown> = {}): void {
    this.writeLog('error', msg, meta);
  }

  warn(msg: string, meta: Record<string, unknown> = {}): void {
    this.writeLog('warn', msg, meta);
  }

  debug(msg: string, meta: Record<string, unknown> = {}): void {
    // Only log debug messages in development
    if (process.env.NODE_ENV === 'development' || process.env.LOG_LEVEL === 'debug') {
      this.writeLog('debug', msg, meta);
    }
  }

  /**
   * Creates a child logger with additional context fields.
   * This is useful for adding request-specific context like userId, correlationId, etc.
   */
  with(fields: Record<string, unknown>): Logger {
    return new ConsoleLogger({
      ...this.baseFields,
      ...fields
    });
  }

  /**
   * Internal method to write structured log entries.
   * Outputs JSON format for easy parsing by log systems.
   */
  private writeLog(level: string, msg: string, meta: Record<string, unknown>): void {
    const logEntry = {
      timestamp: new Date().toISOString(),
      level,
      msg,
      ...this.baseFields,
      ...meta
    };

    const logString = JSON.stringify(logEntry);

    // Use appropriate console method based on level
    switch (level) {
      case 'error':
        console.error(logString);
        break;
      case 'warn':
        console.warn(logString);
        break;
      case 'debug':
        console.debug(logString);
        break;
      default:
        console.log(logString);
    }
  }
}