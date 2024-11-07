# DivergesApp Project Structure

## Overview

This document provides a detailed breakdown of the project's directory structure and key components.

## Root Directory

```
DivergesApp/
│
├── backend/               # Backend application
│   ├── app/               # Main application code
│   │   ├── config/        # Configuration files
│   │   ├── middleware/    # Request middleware
│   │   ├── models/        # Database models
│   │   ├── routes/        # API route handlers
│   │   ├── schemas/       # Pydantic validation schemas
│   │   └── dependencies/  # Dependency injection
│   │
│   ├── migrations/        # Database migration scripts
│   ├── tests/             # Backend test suite
│   ├── Dockerfile         # Docker configuration
│   └── requirements.txt   # Python dependencies
│
├── frontend/              # Frontend application
│   ├── src/
│   │   ├── app/           # Next.js app router
│   │   ├── components/    # Reusable React components
│   │   ├── contexts/      # React context providers
│   │   ├── config/        # Configuration files
│   │   └── styles/        # CSS and styling
│   │
│   ├── public/            # Static assets
│   ├── Dockerfile         # Docker configuration
│   └── package.json       # Node.js dependencies
│
├── docker-compose.yml     # Docker orchestration
├── README.md              # Project documentation
├── CONTRIBUTING.md        # Contribution guidelines
└── LICENSE                # Project licensing
```

## Backend Structure Detailed

### `app/config/`
- `settings.py`: Environment configuration
- `firebase.py`: Firebase Admin SDK initialization

### `app/middleware/`
- `security.py`: Security-related middleware
- Request validation and authentication

### `app/models/`
- `base.py`: Base SQLAlchemy model
- `user.py`: User model with role-based access
- `content.py`: Educational content models

### `app/routes/`
- `auth.py`: Authentication routes
- `content.py`: Content management routes

### `app/schemas/`
- `auth.py`: Authentication request/response schemas
- `content.py`: Content-related validation schemas

## Frontend Structure Detailed

### `src/app/`
- Next.js application routes
- Page components

### `src/components/`
- Reusable React components
- Authentication components
- UI elements

### `src/contexts/`
- `AuthContext.tsx`: Authentication state management
- Global application contexts

### `src/config/`
- Firebase configuration
- Environment setup

## Key Features

### Authentication
- Multi-role system (student, teacher, guardian, admin)
- Firebase authentication
- Role-based access control

### Content Management
- Video, document, and e-book uploads
- Access tracking
- Progress monitoring

## Database Schema

### Users
- Supports multiple roles
- Relationship tracking
- Detailed profile information

### Educational Content
- Multiple content types
- Access logging
- Progress tracking
- Categorization

## Development Workflow

1. Backend: FastAPI with SQLAlchemy
2. Frontend: Next.js with React
3. Authentication: Firebase
4. Database: PostgreSQL
5. Containerization: Docker

## Environment Variables

Refer to `.env.example` files in backend and frontend directories for required configuration.

## Deployment

- Docker Compose for local development
- Supports production deployment
- Scalable architecture

## Recommended Tools

- Backend: 
  - Black (formatting)
  - Mypy (type checking)
  - Pytest (testing)

- Frontend:
  - ESLint
  - Prettier
  - Jest
  - React Testing Library

## Performance Considerations

- Connection pooling
- Efficient database queries
- Caching strategies
- Middleware for request optimization

## Security Measures

- JWT token validation
- Role-based access control
- Secure file uploads
- CORS protection
- Environment-based configuration

## Monitoring and Logging

- Comprehensive logging
- Request tracking
- Performance metrics

## Future Improvements

- Advanced analytics
- Real-time notifications
- Enhanced content recommendations
- Improved guardian dashboard
