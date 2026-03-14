"""
Global Exception Handlers for FastAPI.
Provides consistent error responses across the application.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
import traceback


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": "Validation error",
            "errors": exc.errors()
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy database errors."""
    error_msg = "Database error occurred"

    # Provide more specific messages for common errors
    if isinstance(exc, IntegrityError):
        error_msg = "Database integrity constraint violated (duplicate or invalid data)"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": error_msg,
            "detail": str(exc) if hasattr(exc, '__str__') else "Unknown database error"
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other unexpected exceptions."""
    # Log the full traceback for debugging
    print(f"Unexpected error: {exc}")
    print(traceback.format_exc())

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "Internal server error",
            "detail": str(exc) if request.app.debug else "An unexpected error occurred"
        }
    )
