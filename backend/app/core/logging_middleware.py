import time
import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.background import BackgroundTask
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import OperationLog, LoginLog, User
from app.core.security import oauth2_scheme, verify_password, get_current_user
from fastapi import Request, UploadFile

# Sensitive fields to mask in logs
SENSITIVE_FIELDS = ["password", "token", "access_token", "confirmPassword"]

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        process_time = time.time() - start_time
        latency_ms = int(process_time * 1000)
        
        # Log Logic
        # 1. Login Log: handled by specific endpoint interception or here if we verify content
        #    Intercepting POST /api/v1/auth/login is tricky in middleware because we can't easily read request body twice without consuming it.
        #    However, we can log the RESULT of login in the background.
        
        # 2. Operation Log: Log mutations (POST, PUT, DELETE)
        method = request.method
        path = request.url.path
        
        # Skip GET requests (unless critical, but standard is skip)
        # Skip OPTIONS
        if method in ["POST", "PUT", "DELETE"] and not path.startswith("/docs") and not path.startswith("/openapi.json"):
             response.background = BackgroundTask(
                self.log_operation,
                request=request,
                response_status=response.status_code,
                latency_ms=latency_ms,
                method=method,
                path=path
            )
            
        return response

    async def log_operation(self, request: Request, response_status: int, latency_ms: int, method: str, path: str):
        db = SessionLocal()
        try:
            # Attempt to identify user
            # This is "best effort" logging. Authorization header might be present.
            username = "anonymous"
            token = request.headers.get("Authorization")
            if token and token.startswith("Bearer "):
                # Decode token (simplified, avoiding full dependency injection complexity here)
                from jose import jwt
                from app.core.security import SECRET_KEY, ALGORITHM
                try:
                    token_str = token.split(" ")[1]
                    payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGORITHM])
                    username = payload.get("sub", "anonymous")
                except:
                    pass
            
            # Determine module
            module = "unknown"
            if "/auth/" in path:
                module = "Auth"
            elif "/doctors/" in path:
                module = "Doctor"
            elif "/analysis/" in path:
                module = "Analysis"
            elif "/reports/" in path:
                module = "Report"
            
            # Helper for summary
            summary = f"{method} {path}"
            
            # Params (limited)
            # CAUTION: Reading body in background task after response is sent might be empty or problematic
            # Typically middleware reads body before call_next, but that requires replacement.
            # For now, we'll log query params.
            params = str(request.query_params)
            
            # If it is login, we handle it specifically? 
            # Actually, for login, we might want to capture more.
            # But let's stick to generic Op Log first.
            
            log_entry = OperationLog(
                username=username,
                module=module,
                summary=summary,
                method=method,
                path=path,
                params=params, 
                status=response_status,
                latency_ms=latency_ms
            )
            db.add(log_entry)
            db.commit()
            
        except Exception as e:
            print(f"Logging Error: {e}")
        finally:
            db.close()
