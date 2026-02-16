# Mnemos API Endpoints Report

This report provides a comprehensive overview of all API endpoints available in the Mnemos repository.

## Overview

Mnemos is a Personal RAG (Retrieval-Augmented Generation) system for managing documents (receipts, manuals, PDFs) with intelligent search and chat capabilities. The backend is built using:

- **Framework**: FastAPI
- **Python Version**: 3.12
- **Architecture**: Layered architecture with routes → services → models
- **API Base**: `/api/v1`

## Endpoints Summary

The API currently has **5 endpoints** across 3 main categories:

1. **Root Endpoint** (1 endpoint)
2. **Health Check Endpoints** (2 endpoints)
3. **AI Service Endpoints** (2 endpoints)

## Detailed Endpoint Documentation

### 1. Root Endpoint

#### GET `/`
- **Tags**: Root
- **Description**: API root endpoint providing basic information
- **Response**: JSON object with API info and useful links

**Response Example:**
```json
{
    "message": "Mnemos API",
    "version": "1.0.0",
    "docs": "/docs",
    "health": "/api/v1/health"
}
```

---

### 2. Health Check Endpoints

#### GET `/api/v1/health`
- **Tags**: Health
- **Description**: Basic health check - always returns success if API is running. Ideal for load balancer health checks.
- **Response Model**: `HealthCheck`

**Response Schema:**
```json
{
    "status": "healthy",  // Enum: "healthy" | "degraded"
    "version": "1.0.0"
}
```

#### GET `/api/v1/health/full`
- **Tags**: Health
- **Description**: Detailed health check including external service connectivity. Shows status of all dependencies.
- **Response Model**: `DetailedHealthCheck`
- **Dependencies Checked**: 
  - OpenAI API
  - PostgreSQL Database
  - (TODO: Qdrant vector database)

**Response Schema:**
```json
{
    "status": "healthy",  // Enum: "healthy" | "degraded"
    "version": "1.0.0",
    "services": {
        "openai": {
            "status": "connected",  // Enum: "connected" | "error" | "not_configured"
            "message": "OpenAI API is accessible"
        },
        "postgres": {
            "status": "connected",
            "message": "Database connection successful"
        }
    }
}
```

---

### 3. AI Service Endpoints

#### POST `/api/v1/ai/chat`
- **Tags**: AI
- **Description**: Send a chat message to the AI assistant (powered by OpenAI)
- **Request Model**: `ChatRequest`
- **Response Model**: `ChatResponse`
- **Error Codes**:
  - `503`: AI service not available
  - `502`: External AI service error
  - `500`: Unexpected error

**Request Schema:**
```json
{
    "message": "Hello, how are you?",  // Required, min length: 1
    "model": "gpt-4o-mini"              // Optional, defaults to "gpt-4o-mini"
}
```

**Response Schema:**
```json
{
    "response": "I'm doing well, thank you! How can I help you today?",
    "model": "gpt-4o-mini",
    "tokens_used": 42
}
```

#### GET `/api/v1/ai/test`
- **Tags**: AI
- **Description**: Test if AI service is available and functioning
- **Response Model**: `ServiceStatus`

**Response Schema:**
```json
{
    "status": "available",  // Enum: "available" | "unavailable" | "error"
    "message": "OpenAI API is accessible"
}
```

## API Features

### 1. Middleware Stack
The API includes several middleware layers (executed in reverse order):
- **Security Headers**: Adds security-related HTTP headers
- **Logging**: Request/response logging with correlation IDs
- **Request ID**: Assigns unique IDs to each request
- **CORS**: Configurable Cross-Origin Resource Sharing

### 2. Error Handling
Consistent error response format across all endpoints:
```json
{
    "error": "Validation error",
    "detail": "Request validation failed",
    "request_id": "uuid-string",
    "errors": [
        {
            "field": "message",
            "message": "field required",
            "type": "value_error.missing"
        }
    ]
}
```

### 3. OpenAPI Documentation
- **Interactive API Docs**: Available at `/docs` (Swagger UI)
- **Alternative Docs**: Available at `/redoc` (ReDoc)
- **OpenAPI Schema**: Available at `/openapi.json`

## Future Endpoints (Planned)

Based on the project's purpose as a document management RAG system, expected future endpoints might include:

- **Document Management**:
  - Upload documents (receipts, manuals, PDFs)
  - List/search documents
  - Delete documents
  - Extract text/metadata from documents

- **Vector Search**:
  - Semantic search across documents
  - Similar document retrieval

- **Chat with Context**:
  - Chat with specific documents
  - Multi-document chat sessions

- **User Management** (if multi-user support is added):
  - Authentication endpoints
  - User profile management

## Technical Notes

1. **Authentication**: Currently no authentication is implemented. All endpoints are publicly accessible.

2. **Rate Limiting**: No rate limiting is currently implemented.

3. **Database**: PostgreSQL is configured but not yet used for document storage.

4. **Vector Database**: Qdrant is mentioned in comments but not yet integrated.

5. **Dependency Injection**: The app uses FastAPI's dependency injection for services (e.g., `OpenAIService`).

## Running the API

The API is configured to run with:
- **Default Port**: Check `app/config.py` for configuration
- **Environment**: Configured via environment variables and `.env` files
- **Docker Support**: Docker Compose configuration available

## Development Commands

Key commands for working with the API:
```bash
just harness      # Run full verification suite
just test-local   # Run unit tests
just format-local # Format code
just check-local  # Lint and type check
```

---

*Report generated based on codebase analysis. Last updated: February 2026*