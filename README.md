# LMS Backend API

A comprehensive Learning Management System (LMS) backend built with FastAPI, SQLModel, PostgreSQL, and Alembic. This enterprise-grade solution provides complete functionality for managing online learning platforms, including user management, course creation, content delivery, assessments, and progress tracking.

## 🚀 Features

### Core Functionality
- **User Management**: Complete user lifecycle with role-based access control
- **Course Management**: Course creation, categorization, and publishing workflows
- **Content Delivery**: Support for documents, videos, and interactive content
- **Assessment System**: Comprehensive quiz and testing capabilities
- **Progress Tracking**: Detailed learning analytics and progress monitoring
- **Authentication**: JWT-based authentication with refresh tokens
- **Authorization**: Granular permission system with predefined roles

### Advanced Features
- **File Upload**: Secure file handling with type validation
- **Email Notifications**: Automated email system for user communications
- **Database Migrations**: Version-controlled schema management with Alembic
- **API Documentation**: Auto-generated OpenAPI documentation
- **Error Handling**: Comprehensive error responses with detailed feedback
- **Security**: Password hashing, token validation, and input sanitization

### Technical Highlights
- **FastAPI Framework**: High-performance async API with automatic validation
- **SQLModel ORM**: Type-safe database operations with Pydantic integration
- **PostgreSQL Database**: Robust relational database with JSON support
- **Alembic Migrations**: Database schema versioning and migration management
- **Pydantic Schemas**: Request/response validation and serialization
- **Docker Support**: Containerized deployment with Docker Compose
- **Testing Suite**: Comprehensive unit, integration, and end-to-end tests

## 📋 Requirements

### System Requirements
- Python 3.11 or higher
- PostgreSQL 12+ (for production) or SQLite (for development)
- Redis 6+ (optional, for caching and sessions)
- Docker and Docker Compose (optional, for containerized deployment)

### Python Dependencies
All dependencies are listed in `requirements.txt`:
- FastAPI 0.104+
- SQLModel 0.0.14+
- Alembic 1.13+
- PostgreSQL driver (psycopg2-binary)
- Authentication libraries (passlib, python-jose)
- Additional utilities and middleware

## 🛠️ Installation

### Quick Start (Development)

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd lms_backend
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database Setup (SQLite for Development)**
   ```bash
   echo "DATABASE_URL=sqlite:///./lms.db" > .env
   python init_db.py
   ```

6. **Start the Application**
   ```bash
   python main.py
   ```

The API will be available at:
- **Main API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Production Setup with PostgreSQL

1. **Database Setup**
   ```bash
   # Using Docker Compose
   docker-compose up -d postgres redis
   
   # Or install PostgreSQL manually and create database
   createdb lms_db
   ```

2. **Environment Configuration**
   ```bash
   # Update .env with PostgreSQL settings
   DATABASE_URL=postgresql://lms_user:lms_password@localhost:5432/lms_db
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=lms_user
   DB_PASSWORD=lms_password
   DB_NAME=lms_db
   ```

3. **Run Migrations**
   ```bash
   alembic upgrade head
   ```

4. **Initialize Default Data**
   ```bash
   python init_db.py
   ```

5. **Start Production Server**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

### Docker Deployment

1. **Build and Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Initialize Database**
   ```bash
   docker-compose exec app python init_db.py
   ```

The complete stack (API, PostgreSQL, Redis, Nginx) will be available with proper networking and persistence.

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```env
# Application Settings
DEBUG=True
LOG_LEVEL=INFO
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database Configuration
DATABASE_URL=postgresql://lms_user:lms_password@localhost:5432/lms_db
DB_HOST=localhost
DB_PORT=5432
DB_USER=lms_user
DB_PASSWORD=lms_password
DB_NAME=lms_db

# File Upload Settings
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=52428800  # 50MB in bytes

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0

# Security Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
CORS_ALLOW_CREDENTIALS=True
```

### Default Users and Data

The system initializes with the following default data:

**Default Admin User**
- Email: `admin@lms.com`
- Username: `admin`
- Password: `admin123`
- Role: Super Administrator

**Default Roles**
- `super_admin`: Complete system access
- `admin`: Administrative functions
- `manager`: Team and course management
- `instructor`: Course creation and teaching
- `employee`: Learning and course participation

**Default Categories**
- Technology
- Business
- Compliance
- Soft Skills
- Safety

## 🏗️ Project Structure

```
lms_backend/
├── app/
│   ├── api/                    # API routes and endpoints
│   │   ├── auth/              # Authentication endpoints
│   │   ├── users/             # User management endpoints
│   │   ├── courses/           # Course management endpoints
│   │   ├── modules/           # Module and content endpoints
│   │   ├── quizzes/           # Quiz and assessment endpoints
│   │   └── v1/                # API version routing
│   ├── core/                  # Core application components
│   │   ├── config.py          # Configuration management
│   │   ├── security.py        # Security utilities
│   │   └── logging.py         # Logging configuration
│   ├── db/                    # Database configuration
│   │   └── database.py        # Database setup and session management
│   ├── models/                # SQLModel database models
│   │   ├── user.py           # User-related models
│   │   ├── course.py         # Course-related models
│   │   ├── module.py         # Module and content models
│   │   ├── quiz.py           # Quiz and assessment models
│   │   └── ...               # Additional model files
│   ├── schemas/               # Pydantic request/response schemas
│   │   ├── auth.py           # Authentication schemas
│   │   ├── user.py           # User management schemas
│   │   ├── course.py         # Course management schemas
│   │   └── ...               # Additional schema files
│   ├── services/              # Business logic layer
│   │   ├── auth_service.py   # Authentication service
│   │   ├── user_service.py   # User management service
│   │   ├── course_service.py # Course management service
│   │   └── ...               # Additional service files
│   └── utils/                 # Utility functions
├── alembic/                   # Database migration files
│   ├── versions/             # Migration version files
│   └── env.py                # Alembic environment configuration
├── tests/                     # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── e2e/                  # End-to-end tests
├── uploads/                   # File upload directory
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── alembic.ini               # Alembic configuration
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile                # Docker image configuration
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🔌 API Usage

### Authentication

**Register a New User**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "newuser",
    "password": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Login**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Use Authentication Token**
```bash
# Save the access_token from login response
TOKEN="your-access-token-here"

curl -X GET "http://localhost:8000/api/v1/users/profile" \
  -H "Authorization: Bearer $TOKEN"
```

### Course Management

**Create a Course**
```bash
curl -X POST "http://localhost:8000/api/v1/courses/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Introduction to Python",
    "description": "Learn Python programming basics",
    "category_id": "category-uuid",
    "difficulty_level": "beginner",
    "estimated_duration": 120,
    "is_mandatory": false
  }'
```

**List Courses**
```bash
curl -X GET "http://localhost:8000/api/v1/courses/?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Enroll in a Course**
```bash
curl -X POST "http://localhost:8000/api/v1/courses/course-id/enroll-me" \
  -H "Authorization: Bearer $TOKEN"
```

### Quiz Management

**Create a Quiz**
```bash
curl -X POST "http://localhost:8000/api/v1/quizzes/module/module-id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Basics Quiz",
    "description": "Test your Python knowledge",
    "time_limit": 1800,
    "max_attempts": 3,
    "passing_score": 70.0,
    "questions": [
      {
        "question_text": "What is a variable in Python?",
        "question_type": "multiple_choice",
        "points": 2.0,
        "options": [
          {
            "option_text": "A container for data",
            "is_correct": true,
            "order_index": 1
          },
          {
            "option_text": "A function",
            "is_correct": false,
            "order_index": 2
          }
        ]
      }
    ]
  }'
```

## 🧪 Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run tests in parallel
pytest -n auto
```

### Test Categories

**Unit Tests**: Test individual components in isolation
- Service layer business logic
- Data validation and transformation
- Utility functions and helpers

**Integration Tests**: Test component interactions
- API endpoint functionality
- Database operations
- Authentication flows

**End-to-End Tests**: Test complete user workflows
- User registration and login
- Course creation and enrollment
- Quiz taking and grading

## 📊 Database Schema

The database schema includes the following main entities:

### User Management
- **users**: User accounts with authentication data
- **roles**: System roles with permissions
- **departments**: Organizational structure

### Course Management
- **courses**: Course information and metadata
- **categories**: Course categorization system
- **enrollments**: User course enrollments with progress

### Content Management
- **modules**: Learning modules within courses
- **documents**: File attachments and documents
- **videos**: Video content with metadata

### Assessment System
- **quizzes**: Quiz definitions and configuration
- **questions**: Individual quiz questions
- **question_options**: Multiple choice options
- **quiz_attempts**: User quiz attempts and scores
- **quiz_responses**: Individual question responses

### Relationships
- Users belong to departments and have roles
- Courses belong to categories and have creators
- Modules belong to courses and contain content
- Quizzes belong to modules and contain questions
- Enrollments link users to courses with progress tracking

## 🔒 Security Features

### Authentication Security
- **Password Hashing**: Secure bcrypt hashing with salt
- **JWT Tokens**: Stateless authentication with configurable expiration
- **Token Refresh**: Secure token renewal mechanism
- **Password Reset**: Secure password reset with time-limited tokens

### Authorization Security
- **Role-Based Access Control**: Hierarchical permission system
- **Granular Permissions**: Fine-grained access control
- **API Endpoint Protection**: Permission-based route protection
- **Resource-Level Security**: User-specific data access controls

### Data Security
- **Input Validation**: Comprehensive request validation
- **SQL Injection Protection**: Parameterized queries and ORM protection
- **XSS Prevention**: Input sanitization and output encoding
- **File Upload Security**: Type validation and secure storage

### Infrastructure Security
- **HTTPS Enforcement**: SSL/TLS encryption in production
- **Security Headers**: Comprehensive security header configuration
- **CORS Configuration**: Proper cross-origin request handling
- **Rate Limiting**: API rate limiting and DDoS protection

## 🚀 Deployment

### Development Deployment
```bash
# Quick start with SQLite
python main.py
```

### Production Deployment
```bash
# With PostgreSQL and Redis
docker-compose up -d

# Or manual deployment
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Environment-Specific Configuration
- **Development**: SQLite database, debug logging, CORS enabled
- **Staging**: PostgreSQL database, info logging, limited CORS
- **Production**: PostgreSQL with connection pooling, error logging, strict CORS

## 📈 Performance Considerations

### Database Optimization
- **Connection Pooling**: Configured for high-concurrency workloads
- **Query Optimization**: Efficient queries with proper indexing
- **Caching Strategy**: Redis caching for frequently accessed data
- **Async Operations**: Non-blocking database operations

### API Performance
- **Async Framework**: FastAPI with async/await support
- **Response Compression**: Gzip compression for large responses
- **Pagination**: Efficient pagination for large datasets
- **Field Selection**: Selective field loading to reduce payload size

### Scalability Features
- **Horizontal Scaling**: Stateless design for load balancing
- **Database Sharding**: Support for database partitioning
- **CDN Integration**: Static file serving through CDN
- **Microservice Ready**: Modular design for service decomposition

## 🔧 Maintenance

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

### Backup and Recovery
```bash
# Database backup
pg_dump lms_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Database restore
psql lms_db < backup_file.sql
```

### Monitoring and Logging
- **Application Logs**: Structured JSON logging with correlation IDs
- **Performance Metrics**: Request timing and throughput monitoring
- **Error Tracking**: Comprehensive error logging and alerting
- **Health Checks**: Endpoint health monitoring and status reporting

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Standards
- **Python Style**: Follow PEP 8 guidelines
- **Type Hints**: Use type annotations throughout
- **Documentation**: Document all public APIs
- **Testing**: Maintain test coverage above 90%

### Commit Guidelines
- Use conventional commit messages
- Include tests for new features
- Update documentation as needed
- Ensure CI/CD pipeline passes

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 🆘 Support

### Documentation
- **API Documentation**: Available at `/docs` when running the application
- **Database Schema**: Detailed schema documentation in `API_DOCUMENTATION.md`
- **Deployment Guide**: Comprehensive deployment instructions included

### Getting Help
- **Issues**: Report bugs and feature requests via GitHub issues
- **Discussions**: Join community discussions for questions and ideas
- **Documentation**: Comprehensive documentation available in the repository

### Common Issues

**Database Connection Issues**
- Verify PostgreSQL is running and accessible
- Check database credentials in `.env` file
- Ensure database exists and user has proper permissions

**Authentication Problems**
- Verify JWT secret key is properly configured
- Check token expiration settings
- Ensure user account is active and verified

**File Upload Issues**
- Check upload directory permissions
- Verify file size limits configuration
- Ensure proper file type validation

## 🎯 Roadmap

### Upcoming Features
- **Advanced Analytics**: Detailed learning analytics and reporting
- **Mobile API**: Enhanced mobile application support
- **Integration APIs**: Third-party system integration capabilities
- **Advanced Notifications**: Real-time notifications and messaging
- **Content Authoring**: Built-in content creation tools

### Performance Improvements
- **Caching Layer**: Enhanced Redis caching implementation
- **Database Optimization**: Advanced query optimization and indexing
- **API Rate Limiting**: Sophisticated rate limiting and throttling
- **Content Delivery**: CDN integration for media files

### Security Enhancements
- **Two-Factor Authentication**: 2FA support for enhanced security
- **OAuth Integration**: Social login and SSO capabilities
- **Audit Logging**: Comprehensive audit trail and compliance features
- **Advanced Permissions**: Dynamic permission system with custom roles

This LMS Backend API provides a solid foundation for building comprehensive learning management systems with enterprise-grade features, security, and scalability. The modular architecture and comprehensive documentation make it easy to customize and extend for specific requirements.

