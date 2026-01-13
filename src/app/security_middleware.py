"""
Security Middleware Module.

Provides API security features including rate limiting, authentication,
request validation, and audit logging.

Part of Phase 2 Security Enhancement (Sprint 4).
"""

import os
import time
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set, Callable, Any
from collections import defaultdict
from dataclasses import dataclass, field
from functools import wraps

from fastapi import Request, Response, HTTPException, Depends, Header
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


# =============================================================================
# Configuration
# =============================================================================

class SecurityConfig:
    """Security configuration from environment variables."""
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv('RATE_LIMIT_WINDOW_SECONDS', '60'))
    
    # API Keys (comma-separated list)
    API_KEYS: Set[str] = set(filter(None, os.getenv('ALTFLEX_API_KEYS', '').split(',')))
    API_KEY_REQUIRED: bool = os.getenv('ALTFLEX_API_KEY_REQUIRED', 'false').lower() == 'true'
    
    # Endpoints that don't require authentication
    PUBLIC_ENDPOINTS: Set[str] = {
        '/',
        '/health',
        '/docs',
        '/openapi.json',
        '/redoc',
    }
    
    # Request size limits
    MAX_REQUEST_SIZE_BYTES: int = int(os.getenv('MAX_REQUEST_SIZE_BYTES', '1048576'))  # 1MB
    
    # Audit logging
    AUDIT_LOG_ENABLED: bool = os.getenv('AUDIT_LOG_ENABLED', 'true').lower() == 'true'
    AUDIT_LOG_FILE: str = os.getenv('AUDIT_LOG_FILE', 'logs/audit.log')


# =============================================================================
# Rate Limiter (API-P1-012)
# =============================================================================

@dataclass
class RateLimitBucket:
    """Token bucket for rate limiting."""
    tokens: float
    last_update: float
    
    
class RateLimiter:
    """
    Token bucket rate limiter.
    
    Tracks request counts per client IP and enforces rate limits.
    """
    
    def __init__(
        self, 
        max_requests: int = SecurityConfig.RATE_LIMIT_REQUESTS,
        window_seconds: int = SecurityConfig.RATE_LIMIT_WINDOW_SECONDS
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.buckets: Dict[str, RateLimitBucket] = {}
        self._cleanup_interval = 300  # Cleanup stale buckets every 5 minutes
        self._last_cleanup = time.time()
    
    def _get_client_id(self, request: Request) -> str:
        """Get unique identifier for client (IP address)."""
        # Get real IP from forwarded headers if behind proxy
        forwarded = request.headers.get('X-Forwarded-For')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return request.client.host if request.client else 'unknown'
    
    def _refill_tokens(self, bucket: RateLimitBucket) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - bucket.last_update
        
        # Calculate tokens to add (linear refill)
        tokens_to_add = elapsed * (self.max_requests / self.window_seconds)
        bucket.tokens = min(self.max_requests, bucket.tokens + tokens_to_add)
        bucket.last_update = now
    
    def _cleanup_stale_buckets(self) -> None:
        """Remove old buckets to prevent memory growth."""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        
        stale_threshold = now - (self.window_seconds * 2)
        stale_keys = [
            k for k, v in self.buckets.items() 
            if v.last_update < stale_threshold
        ]
        for k in stale_keys:
            del self.buckets[k]
        
        self._last_cleanup = now
    
    def is_allowed(self, request: Request) -> tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed under rate limit.
        
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        self._cleanup_stale_buckets()
        
        client_id = self._get_client_id(request)
        now = time.time()
        
        # Get or create bucket
        if client_id not in self.buckets:
            self.buckets[client_id] = RateLimitBucket(
                tokens=self.max_requests,
                last_update=now
            )
        
        bucket = self.buckets[client_id]
        self._refill_tokens(bucket)
        
        # Check if request is allowed
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True, {
                'limit': self.max_requests,
                'remaining': int(bucket.tokens),
                'reset': int(now + self.window_seconds)
            }
        else:
            return False, {
                'limit': self.max_requests,
                'remaining': 0,
                'reset': int(bucket.last_update + self.window_seconds),
                'retry_after': int(self.window_seconds - (now - bucket.last_update))
            }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting."""
    
    def __init__(self, app, rate_limiter: Optional[RateLimiter] = None):
        super().__init__(app)
        self.rate_limiter = rate_limiter or RateLimiter()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in SecurityConfig.PUBLIC_ENDPOINTS:
            return await call_next(request)
        
        is_allowed, info = self.rate_limiter.is_allowed(request)
        
        if not is_allowed:
            return JSONResponse(
                status_code=429,
                content={
                    'error': 'Rate limit exceeded',
                    'detail': f'Maximum {info["limit"]} requests per {self.rate_limiter.window_seconds} seconds',
                    'retry_after': info.get('retry_after', 60)
                },
                headers={
                    'X-RateLimit-Limit': str(info['limit']),
                    'X-RateLimit-Remaining': str(info['remaining']),
                    'X-RateLimit-Reset': str(info['reset']),
                    'Retry-After': str(info.get('retry_after', 60))
                }
            )
        
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers['X-RateLimit-Limit'] = str(info['limit'])
        response.headers['X-RateLimit-Remaining'] = str(info['remaining'])
        response.headers['X-RateLimit-Reset'] = str(info['reset'])
        
        return response


# =============================================================================
# API Key Authentication (API-P2-014)
# =============================================================================

api_key_header = APIKeyHeader(name='X-API-Key', auto_error=False)


class APIKeyAuth:
    """API Key authentication handler."""
    
    def __init__(self, required: bool = SecurityConfig.API_KEY_REQUIRED):
        self.required = required
        self.valid_keys = SecurityConfig.API_KEYS
    
    def _hash_key(self, key: str) -> str:
        """Hash API key for logging (don't log raw keys)."""
        return hashlib.sha256(key.encode()).hexdigest()[:12]
    
    async def __call__(
        self, 
        request: Request,
        api_key: Optional[str] = Depends(api_key_header)
    ) -> Optional[str]:
        """
        Validate API key from request header.
        
        Returns the API key if valid, or raises HTTPException if invalid.
        """
        # Skip auth for public endpoints
        if request.url.path in SecurityConfig.PUBLIC_ENDPOINTS:
            return None
        
        # If API key auth is not required, allow all requests
        if not self.required:
            return api_key
        
        # Check if key is provided
        if not api_key:
            raise HTTPException(
                status_code=401,
                detail='API key required. Provide X-API-Key header.',
                headers={'WWW-Authenticate': 'ApiKey'}
            )
        
        # Validate key
        if api_key not in self.valid_keys:
            raise HTTPException(
                status_code=403,
                detail='Invalid API key',
                headers={'WWW-Authenticate': 'ApiKey'}
            )
        
        return api_key


def require_api_key(
    api_key: Optional[str] = Depends(api_key_header)
) -> Optional[str]:
    """Dependency for endpoints that require API key authentication."""
    auth = APIKeyAuth(required=True)
    # Note: This is a simplified version; full async handling needs Request
    if SecurityConfig.API_KEY_REQUIRED:
        if not api_key:
            raise HTTPException(
                status_code=401,
                detail='API key required'
            )
        if api_key not in SecurityConfig.API_KEYS:
            raise HTTPException(
                status_code=403,
                detail='Invalid API key'
            )
    return api_key


# =============================================================================
# Request Validation (API-P1-013)
# =============================================================================

class RequestValidationError(Exception):
    """Custom exception for request validation errors."""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(message)


class RequestValidator:
    """Enhanced request validation utilities."""
    
    # Suspicious patterns to detect in input
    SUSPICIOUS_PATTERNS: List[str] = [
        '<script', 'javascript:', 'onerror=', 'onclick=',
        'DROP TABLE', 'DELETE FROM', 'INSERT INTO', '--',
    ]
    
    @staticmethod
    def sanitize_address(address: str) -> str:
        """
        Sanitize Ethereum address input.
        
        Args:
            address: Raw address string
            
        Returns:
            Sanitized address
            
        Raises:
            RequestValidationError: If address contains invalid characters
        """
        # Remove whitespace
        address = address.strip()
        
        # Check for valid hex characters only
        if not all(c in '0123456789abcdefABCDEFx' for c in address):
            raise RequestValidationError(
                'Address contains invalid characters',
                field='address'
            )
        
        return address.lower()
    
    @staticmethod
    def check_request_size(content_length: Optional[int]) -> bool:
        """Check if request size is within limits."""
        if content_length is None:
            return True
        return content_length <= SecurityConfig.MAX_REQUEST_SIZE_BYTES
    
    @classmethod
    def detect_suspicious_input(cls, data: str) -> List[str]:
        """
        Detect suspicious patterns in input data.
        
        Returns list of detected patterns.
        """
        data_lower = data.lower()
        return [
            pattern for pattern in cls.SUSPICIOUS_PATTERNS
            if pattern.lower() in data_lower
        ]
    
    @staticmethod
    def validate_tx_hash(tx_hash: Optional[str]) -> bool:
        """Validate transaction hash format."""
        if tx_hash is None:
            return True
        
        # Must be 66 characters (0x + 64 hex chars)
        if len(tx_hash) != 66:
            return False
        
        if not tx_hash.startswith('0x'):
            return False
        
        # Check hex characters
        try:
            int(tx_hash, 16)
            return True
        except ValueError:
            return False


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for request validation."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check content length
        content_length = request.headers.get('content-length')
        if content_length:
            try:
                if int(content_length) > SecurityConfig.MAX_REQUEST_SIZE_BYTES:
                    return JSONResponse(
                        status_code=413,
                        content={
                            'error': 'Request too large',
                            'detail': f'Maximum request size is {SecurityConfig.MAX_REQUEST_SIZE_BYTES} bytes'
                        }
                    )
            except ValueError:
                pass
        
        return await call_next(request)


# =============================================================================
# Audit Logger (API-P2-015)
# =============================================================================

class AuditLogger:
    """
    Security audit logger for tracking API activity.
    
    Logs:
    - All API requests
    - Authentication attempts
    - Rate limit violations
    - Suspicious activity
    """
    
    def __init__(self, log_file: str = SecurityConfig.AUDIT_LOG_FILE):
        self.enabled = SecurityConfig.AUDIT_LOG_ENABLED
        self.log_file = log_file
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Configure the audit logger."""
        logger = logging.getLogger('altflex.audit')
        logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - AUDIT - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        # File handler (if path is valid)
        if self.log_file:
            try:
                log_dir = os.path.dirname(self.log_file)
                if log_dir:
                    os.makedirs(log_dir, exist_ok=True)
                
                file_handler = logging.FileHandler(self.log_file)
                file_handler.setLevel(logging.INFO)
                file_format = logging.Formatter(
                    '%(asctime)s|%(levelname)s|%(message)s'
                )
                file_handler.setFormatter(file_format)
                logger.addHandler(file_handler)
            except Exception as e:
                logger.warning(f"Could not create file handler: {e}")
        
        return logger
    
    def log_request(
        self, 
        request: Request, 
        response_status: int,
        duration_ms: float,
        api_key: Optional[str] = None
    ) -> None:
        """Log an API request."""
        if not self.enabled:
            return
        
        client_ip = request.headers.get('X-Forwarded-For', 
                                        request.client.host if request.client else 'unknown')
        
        key_indicator = f"key:{hashlib.sha256(api_key.encode()).hexdigest()[:8]}" if api_key else "no-key"
        
        self.logger.info(
            f"REQUEST|{request.method}|{request.url.path}|"
            f"status:{response_status}|ip:{client_ip}|{key_indicator}|"
            f"duration:{duration_ms:.2f}ms"
        )
    
    def log_auth_failure(
        self, 
        request: Request, 
        reason: str
    ) -> None:
        """Log an authentication failure."""
        if not self.enabled:
            return
        
        client_ip = request.headers.get('X-Forwarded-For',
                                        request.client.host if request.client else 'unknown')
        
        self.logger.warning(
            f"AUTH_FAILURE|{request.method}|{request.url.path}|"
            f"ip:{client_ip}|reason:{reason}"
        )
    
    def log_rate_limit(
        self, 
        request: Request,
        limit: int,
        window: int
    ) -> None:
        """Log a rate limit violation."""
        if not self.enabled:
            return
        
        client_ip = request.headers.get('X-Forwarded-For',
                                        request.client.host if request.client else 'unknown')
        
        self.logger.warning(
            f"RATE_LIMIT|{request.method}|{request.url.path}|"
            f"ip:{client_ip}|limit:{limit}/{window}s"
        )
    
    def log_suspicious(
        self, 
        request: Request,
        patterns: List[str]
    ) -> None:
        """Log suspicious activity."""
        if not self.enabled:
            return
        
        client_ip = request.headers.get('X-Forwarded-For',
                                        request.client.host if request.client else 'unknown')
        
        self.logger.warning(
            f"SUSPICIOUS|{request.method}|{request.url.path}|"
            f"ip:{client_ip}|patterns:{','.join(patterns)}"
        )


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Middleware for audit logging all requests."""
    
    def __init__(self, app, audit_logger: Optional[AuditLogger] = None):
        super().__init__(app)
        self.audit_logger = audit_logger or AuditLogger()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        response = await call_next(request)
        
        duration_ms = (time.time() - start_time) * 1000
        api_key = request.headers.get('X-API-Key')
        
        self.audit_logger.log_request(
            request=request,
            response_status=response.status_code,
            duration_ms=duration_ms,
            api_key=api_key
        )
        
        return response


# =============================================================================
# Convenience Functions
# =============================================================================

# Global instances
_rate_limiter: Optional[RateLimiter] = None
_audit_logger: Optional[AuditLogger] = None


def get_rate_limiter() -> RateLimiter:
    """Get or create the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def get_audit_logger() -> AuditLogger:
    """Get or create the global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def setup_security_middleware(app) -> None:
    """
    Add all security middleware to a FastAPI application.
    
    Should be called after CORS middleware.
    """
    # Order matters: audit first, then validation, then rate limiting
    app.add_middleware(AuditLogMiddleware, audit_logger=get_audit_logger())
    app.add_middleware(RequestValidationMiddleware)
    app.add_middleware(RateLimitMiddleware, rate_limiter=get_rate_limiter())


if __name__ == "__main__":
    # Demo
    print("Security Middleware Module")
    print(f"Rate Limit: {SecurityConfig.RATE_LIMIT_REQUESTS}/{SecurityConfig.RATE_LIMIT_WINDOW_SECONDS}s")
    print(f"API Key Required: {SecurityConfig.API_KEY_REQUIRED}")
    print(f"Audit Logging: {SecurityConfig.AUDIT_LOG_ENABLED}")
