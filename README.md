# FastAPI Bootstrapped

A production-ready FastAPI project template with best practices for rapid development.

## Features

- 🚀 FastAPI for high-performance API development
- 🔐 User authentication and authorization
- 📦 SQLAlchemy, SQLModel, and Alembic for database management
- 🎯 Repository pattern for clean architecture
- 🛠️ PDM for dependency management
- 📝 Logging setup with proper error handling
- 🔍 API versioning
- 🧪 Testing setup (ready for your tests)

## Project Structure

```
├── migrations/          # Database migrations
├── scripts/             # Utility scripts
├── src/                 # Source code
│   ├── api/             # API routes, endpoints and business logic
│   ├── base/            # Base classes and interfaces
│   ├── core/            # Core configurations
│   ├── helpers/         # Helper utilities
│   ├── models/          # Database models
│   └── repositories/   # Data layer and business logic
└── tests/               # Test files
```

## Getting Started

### Prerequisites

- Python 3.10 or higher
- PDM package manager
- PostgreSQL

### Installation

1. Clone the repository:

```bash
git clone https://github.com/monarchmaisuriya/fastapi-bootstrapped.git
cd fastapi-bootstrapped
```

2. Setup and install dependencies:

```bash
pdm venv create 3.10
pdm use -f .venv
pdm install
```

3. Set up environment variables:

```bash
cp example.env .env
# Edit .env with your configuration
```

4. Run database migrations:

```bash
pdm run alembic upgrade head
```

5. Start the development server:

```bash
pdm run dev
```

The API will be available at `http://localhost:8080`

### API Documentation

Once the server is running, you can access:

- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## Development

### Creating New Migrations

```bash
pdm run alembic revision -m "your migration description"
```

### Running Tests

```bash
pdm run test
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
