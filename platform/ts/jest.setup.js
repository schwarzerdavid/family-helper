/**
 * Jest setup file that runs before each test file.
 * Used to configure global test environment and utilities.
 */

// Set test environment
process.env.NODE_ENV = 'test';

// Increase test timeout for async operations
jest.setTimeout(15000);

// Global test utilities
global.testUtils = {
  /**
   * Creates a mock logger for testing
   */
  createMockLogger: () => ({
    info: jest.fn(),
    error: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn(),
    with: jest.fn().mockReturnThis()
  }),

  /**
   * Helper to wait for async operations in tests
   */
  waitFor: (ms) => new Promise(resolve => setTimeout(resolve, ms)),

  /**
   * Helper to capture console output during tests
   */
  captureConsole: () => {
    const originalConsole = {
      log: console.log,
      error: console.error,
      warn: console.warn,
      debug: console.debug
    };

    const mockConsole = {
      log: jest.fn(),
      error: jest.fn(),
      warn: jest.fn(),
      debug: jest.fn()
    };

    // Replace console methods
    console.log = mockConsole.log;
    console.error = mockConsole.error;
    console.warn = mockConsole.warn;
    console.debug = mockConsole.debug;

    return {
      mock: mockConsole,
      restore: () => {
        console.log = originalConsole.log;
        console.error = originalConsole.error;
        console.warn = originalConsole.warn;
        console.debug = originalConsole.debug;
      }
    };
  }
};

// Mock console methods by default to avoid noisy test output
const originalConsole = {
  log: console.log,
  error: console.error,
  warn: console.warn,
  debug: console.debug
};

// Only show console output if DEBUG environment variable is set
if (!process.env.DEBUG) {
  console.log = jest.fn();
  console.error = jest.fn();
  console.warn = jest.fn();
  console.debug = jest.fn();
}

// Clean up environment variables before each test
beforeEach(() => {
  // Store original env
  global.originalEnv = { ...process.env };
  
  // Clean up common test env vars
  delete process.env.TEST_CONFIG;
  delete process.env.TEST_SECRET;
  delete process.env.TRACE_ID;
});

// Restore environment after each test
afterEach(() => {
  if (global.originalEnv) {
    process.env = global.originalEnv;
  }
});

// Global error handler for uncaught exceptions in tests
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

// Extend Jest matchers for better assertions
expect.extend({
  /**
   * Custom matcher to check if a function was called with partial object match
   */
  toHaveBeenCalledWithObjectContaining(received, expected) {
    if (!jest.isMockFunction(received)) {
      return {
        message: () => 'Expected value to be a mock function',
        pass: false
      };
    }

    const calls = received.mock.calls;
    const found = calls.some(call => {
      return call.some(arg => {
        if (typeof arg === 'object' && arg !== null) {
          return Object.keys(expected).every(key => 
            arg.hasOwnProperty(key) && arg[key] === expected[key]
          );
        }
        return false;
      });
    });

    return {
      message: () => `Expected function to be called with object containing ${JSON.stringify(expected)}`,
      pass: found
    };
  },

  /**
   * Custom matcher to check if a value is a valid ISO timestamp
   */
  toBeValidISOTimestamp(received) {
    const isString = typeof received === 'string';
    const isValidDate = !isNaN(Date.parse(received));
    const isISOFormat = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/.test(received);

    const pass = isString && isValidDate && isISOFormat;

    return {
      message: () => `Expected ${received} to be a valid ISO timestamp`,
      pass
    };
  }
});