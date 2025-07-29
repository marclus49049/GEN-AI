# Simple FastAPI Backend

A simple Hello World FastAPI backend following best practices.

## Features

- ✅ RESTful API endpoints
- ✅ API versioning (v1)
- ✅ CORS middleware configured
- ✅ Auto-generated API documentation
- ✅ Type hints throughout
- ✅ Modular project structure
- ✅ Environment configuration support

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Navigate to the Backend directory:
   ```bash
   cd Backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file by copying the example:
   ```bash
   cp .env.example .env
   ```

## Running the Server

1. Make sure your virtual environment is activated

2. Run the server with auto-reload:
   ```bash
   uvicorn app.main:app --reload
   ```

   Or run on a specific port:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

3. The server will start at `http://localhost:8000`

## API Endpoints

### Root Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check endpoint

### Hello World Endpoints

- `GET /api/v1/hello` - Returns "Hello, World!"
- `GET /api/v1/hello/{name}` - Returns personalized greeting

## API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
Backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application instance
│   └── api/
│       ├── __init__.py
│       └── endpoints/
│           ├── __init__.py
│           └── hello.py     # Hello world endpoints
├── requirements.txt         # Python dependencies
├── .env.example            # Example environment variables
├── .gitignore             # Git ignore patterns
└── README.md              # This file
```

## Development Tips

1. **Auto-reload**: The `--reload` flag enables auto-reload during development
2. **Type checking**: FastAPI uses type hints for validation and documentation
3. **Environment variables**: Use `.env` file for configuration
4. **Testing API**: Use the interactive docs at `/docs` to test endpoints

## Environment Variables

See `.env.example` for available configuration options:

- `APP_NAME`: Application name
- `APP_VERSION`: Application version
- `DEBUG`: Debug mode (True/False)
- `HOST`: Server host
- `PORT`: Server port
- `ALLOWED_ORIGINS`: CORS allowed origins
- `ENVIRONMENT`: Current environment (development/production)

## Next Steps

- Add more endpoints in `app/api/endpoints/`
- Implement database integration
- Add authentication and authorization
- Create unit and integration tests
- Set up CI/CD pipeline

## License

This project is open source and available under the MIT License.