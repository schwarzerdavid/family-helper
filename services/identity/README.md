# Identity & Accounts Service

Core authentication and user management service for the Family Helper platform.

## Role

Provides centralized identity management:
- **User Registration**: Email/password and social OAuth flows
- **Authentication**: Login, logout, token refresh
- **Authorization**: Role-based access control (RBAC)
- **User Management**: Profile data, preferences, account lifecycle
- **JWT Issuance**: Token generation and validation

## Technology Stack

- **Framework**: TypeScript with NestJS
- **Database**: PostgreSQL (user data, roles, permissions)
- **Authentication**: Passport.js with OAuth strategies
- **Token Management**: JWT with RS256 signing
- **Platform**: Uses `@platform-ts` wrapper

## API Endpoints

```
POST /auth/register      - User registration
POST /auth/login         - Email/password login  
POST /auth/oauth/:provider - OAuth login (Google, etc.)
POST /auth/refresh       - Token refresh
POST /auth/logout        - User logout

GET  /users/me          - Current user profile
PUT  /users/me          - Update user profile
GET  /users/:id/roles   - User roles and permissions
```

## Events Published

- **UserCreated:v1** - When new user registers
  ```json
  {
    "userId": "uuid",
    "email": "string", 
    "displayName": "string",
    "locale": "en-US",
    "timezone": "Asia/Jerusalem"
  }
  ```

- **UserLoggedIn:v1** - When user authenticates
- **UserUpdated:v1** - When profile changes

## Database Schema

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT, -- nullable for OAuth-only users
  display_name TEXT NOT NULL,
  locale TEXT DEFAULT 'en-US',
  timezone TEXT DEFAULT 'Asia/Jerusalem',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_oauth (
  user_id UUID REFERENCES users(id),
  provider TEXT NOT NULL, -- 'google', 'facebook', etc.
  provider_id TEXT NOT NULL,
  PRIMARY KEY (provider, provider_id)
);
```

## Configuration

Environment variables:
```bash
DATABASE_URL=postgresql://...
JWT_SECRET=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

## Development

```bash
npm install
npm run dev    # Start in development mode
npm test       # Run tests
npm run build  # Build for production
```