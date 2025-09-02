module.exports = {
  // Test environment
  testEnvironment: 'node',

  // TypeScript support
  preset: 'ts-jest',

  // Test file patterns
  testMatch: [
    '**/__tests__/**/*.(test|spec).(ts|tsx|js)',
    '**/*.(test|spec).(ts|tsx|js)'
  ],

  // Coverage configuration
  collectCoverage: true,
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/__tests__/**/*',
    '!src/**/node_modules/**'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: [
    'text',
    'lcov',
    'html',
    'json-summary'
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70
    }
  },

  // Module resolution
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },

  // Setup files
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],

  // Clear mocks between tests
  clearMocks: true,
  restoreMocks: true,

  // Verbose output for better debugging
  verbose: true,

  // Transform configuration
  transform: {
    '^.+\\.(ts|tsx)$': ['ts-jest', {
      tsconfig: 'tsconfig.json'
    }]
  },

  // Module file extensions
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],

  // Ignore patterns
  testPathIgnorePatterns: [
    '/node_modules/',
    '/dist/'
  ]
};