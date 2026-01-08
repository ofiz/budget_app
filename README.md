# BudgetFlow - Financial Expense Tracking Application

A modern, secure web application for tracking personal finances with income and expense management.

## 🚀 Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Run Application
```powershell
docker-compose up -d
```

Open browser to: **http://localhost:8000**

### Stop Application
```powershell
docker-compose down
```

---

## 🎯 Features

- **User Management**: Secure registration and authentication
- **Transaction Tracking**: Add, view, and delete income/expenses with categories
- **Balance Dashboard**: Real-time balance calculation with visual indicators
- **Professional UI**: Distinctive, modern design with diagonal flow and bold aesthetics
- **Security-First**: OWASP Top 10 compliant with comprehensive security measures
- **Full Test Coverage**: E2E tests with Playwright and unit tests with pytest

## 🏗️ Architecture

### Tech Stack

- **Backend**: Python 3.12+ with FastAPI
- **Database**: MongoDB (NoSQL)
- **Frontend**: Vanilla JavaScript with modern CSS
- **Testing**: Playwright (E2E) + pytest (Unit)
- **Security**: Bcrypt password hashing, JWT authentication, OWASP protections
- **Deployment**: Docker + Docker Compose

### Docker Architecture

The application uses a multi-container Docker setup:

- **MongoDB**: Persistent database with health checks (port 27017)
- **Backend**: Python FastAPI application (port 8000)
- **E2E Tests**: Playwright tests (run on demand with `--profile testing`)

All containers communicate through a dedicated Docker network with proper health checks and restart policies.

### Project Structure

```
budget_app/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── auth.py          # Authentication routes
│   │   ├── transactions.py  # Transaction routes
│   │   ├── models.py        # Pydantic models
│   │   ├── database.py      # MongoDB connection
│   │   ├── security.py      # Security utilities
│   │   └── config.py        # Configuration
│   └── tests/               # Unit tests
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css   # Modern, distinctive styling
│   │   └── js/
│   │       └── app.js       # Frontend logic
│   └── templates/
│       └── index.html       # Single-page application
├── e2e_tests/
│   └── tests/
│       └── app.spec.ts      # Playwright E2E tests
└── .github/
    ├── skills/              # AI skill guidelines
    └── copilot-instructions.md
```

## 🔒 Security Implementation (OWASP Compliance)

### A01: Broken Access Control
- **Deny by default**: All routes require authentication
- **User isolation**: Users can only access their own data
- **UUID public IDs**: Internal database IDs never exposed

### A02: Cryptographic Failures
- **Bcrypt password hashing**: Industry-standard with automatic salting
- **Secure secret management**: All secrets from environment variables
- **HTTPS enforcement**: HSTS headers implemented

### A03: Injection
- **Parameterized queries**: MongoDB queries use safe parameterization
- **XSS prevention**: Frontend uses `.textContent` over `.innerHTML`
- **Input validation**: Pydantic models validate all inputs

### A05: Security Misconfiguration
- **Security headers**: CSP, X-Frame-Options, X-Content-Type-Options, HSTS
- **No debug in production**: Debug mode disabled by default
- **Secure defaults**: All security settings enabled

### A07: Identification & Authentication Failures
- **Strong password requirements**: Min 8 chars, uppercase, lowercase, digit
- **JWT tokens**: Short expiration (30 minutes)
- **Generic error messages**: Prevents user enumeration

### A08: Software and Data Integrity Failures
- **Input validation**: Pydantic models validate all API inputs
- **JSON serialization**: Safe JSON over pickle for data exchange

## 📦 Prerequisites

### For Docker (Recommended)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- PowerShell (Built into Windows)

### For Manual Setup
- Python 3.12+
- MongoDB
- Node.js 18+ (for E2E tests)

## 🚀 Setup Instructions

### Using Docker

1. **Start the application**:
   ```powershell
   docker-compose up -d
   ```

2. **Open browser** to http://localhost:8000

3. **Stop when done**:
   ```powershell
   docker-compose down
   ```

**Configuration**: Edit `.env` for custom settings.

**Before Production**:
```powershell
# Generate secure secrets
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Update SECRET_KEY and MONGO_PASSWORD in .env
```

**Useful Commands**:
- View logs: `docker-compose logs -f`
- Run tests: `docker-compose --profile testing run --rm e2e_tests`
- Restart: `docker-compose restart`
- Clean all: `docker-compose down -v` (⚠️ deletes data)

---

## 🧪 Testing
```

### 4. Start MongoDB

Ensure MongoDB is running locally or configure cloud connection in `.env`.

```powershell
# If using Docker:
docker run -d -p 27017:27017 --name mongodb mongo:latest
```---

## 🧪 Testing

### E2E Tests
```powershell
docker-compose --profile testing run --rm e2e_tests
```

### Unit Tests
```powershell
docker-compose exec backend pytest backend/tests/ -v
```

---

## 📊 Database Schema

### Users Collection

```json
{
  "public_id": "uuid",
  "email": "string (unique)",
  "full_name": "string",
  "hashed_password": "string (bcrypt)",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime",
  "deleted_at": "datetime | null"
}
```

### Transactions Collection

```json
{
  "public_id": "uuid",
  "user_public_id": "uuid",
  "type": "income | expense",
  "category": "string (enum)",
  "amount": "float (positive)",
  "description": "string",
  "date": "datetime",
  "created_at": "datetime",
  "updated_at": "datetime",
  "deleted_at": "datetime | null"
}
```

## 🎨 Design Philosophy

Following the **frontend-design skill**, this application features:

- **Distinctive Typography**: Outfit (display) + Space Grotesk (body)
- **Bold Color Palette**: Deep navy with electric cyan accents
- **Asymmetric Layout**: Diagonal emphasis, overlapping elements
- **High-Impact Animations**: Orchestrated reveals and transitions
- **NO Generic AI Aesthetics**: No Inter, Roboto, or typical purple gradients

## 🔧 Implementation Choices Explained

### Why FastAPI?
- Modern async support for better performance
- Automatic API documentation (OpenAPI)
- Built-in validation with Pydantic
- Type safety with Python 3.12+ type hints

### Why MongoDB?
- Assignment requirement (NoSQL database)
- Flexible schema for rapid development
- Native Python support via Motor (async)
- Easy scaling and replication

### Why Bcrypt for Passwords?
- OWASP recommended for password hashing
- Automatic salt generation
- Configurable work factor (future-proof)
- Timing-safe comparison

### Why JWT Tokens?
- Stateless authentication
- Scalable across multiple servers
- Standard format (RFC 7519)
- Short expiration for security

### Why Vanilla JavaScript?
- No framework overhead
- Direct control over XSS prevention
- Faster load times
- Demonstrates security implementation clearly

### UUID Public IDs?
- Prevents enumeration attacks
- No information leakage
- Globally unique identifiers
- Following backend-development skill pattern

### Soft Deletes?
- Data recovery capability
- Audit trail preservation
- GDPR compliance ready
- Following backend-development skill pattern

## 🧪 Testing Strategy

### E2E Tests (Playwright)
- User registration flow
- Login/logout functionality
- Adding income/expense transactions
- Balance calculation accuracy
- Transaction deletion
- Form validation
- Security error handling

### Unit Tests (pytest)
- Password hashing security
- Security headers validation
- Authentication endpoints
- Transaction CRUD operations
- Input validation
- Injection prevention
- Access control enforcement

## 📈 Future Enhancements

- Rate limiting for API endpoints (OWASP A05)
- Email verification for registration
- Password reset functionality
- Transaction categories customization
- Budget goals and alerts
- Data export (CSV, PDF)
- Multi-currency support
- Recurring transactions

## 🤝 Contributing

This is a university assignment project. For production use, consider:

1. Add rate limiting (e.g., slowapi)
2. Implement refresh tokens
3. Add logging and monitoring
4. Set up CI/CD pipeline
5. Configure production-grade MongoDB
6. Add Redis caching for sessions
7. Implement proper CORS restrictions

## 📄 License

Educational/Assignment Project

## 👨‍💻 Developer Notes

### Key Security Measures Implemented

1. **Never hardcode secrets** - All from environment
2. **Bcrypt for passwords** - OWASP A02 compliance
3. **Parameterized queries** - OWASP A03 injection prevention
4. **Security headers** - OWASP A05 misconfiguration protection
5. **JWT with short expiration** - OWASP A07 authentication protection
6. **XSS prevention** - `.textContent` usage in frontend
7. **Generic error messages** - Prevents user enumeration
8. **UUID public IDs** - Prevents ID enumeration
9. **Soft deletes** - Data integrity and recovery
10. **Access control** - Deny by default, user isolation

### Running in Production

1. Set `DEBUG=False` in `.env`
2. Use strong `SECRET_KEY` (64+ random characters)
3. Configure MongoDB with authentication
4. Use HTTPS/TLS for all connections
5. Set proper CORS origins (not `*`)
6. Enable MongoDB backups
7. Monitor with logging service
8. Set up rate limiting

---

**Built with security-first mindset following OWASP Top 10 guidelines** 🔒