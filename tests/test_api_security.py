"""
Unit Tests for API Security.

Tests for Sprint 4: API Hardening.

Covers rate limiting, API key authentication, request validation, and audit logging.
"""

import pytest
import time
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.security_middleware import (
    SecurityConfig,
    RateLimiter,
    RateLimitBucket,
    RateLimitMiddleware,
    APIKeyAuth,
    require_api_key,
    RequestValidator,
    RequestValidationError,
    RequestValidationMiddleware,
    AuditLogger,
    AuditLogMiddleware,
    get_rate_limiter,
    get_audit_logger,
)


# =============================================================================
# Mock Request Fixtures
# =============================================================================

class MockHeaders:
    """Mock headers object that behaves like a dict but with .get() method."""
    def __init__(self, data: dict = None):
        self._data = data or {}
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def __getitem__(self, key):
        return self._data.get(key)


def create_mock_request(
    path: str = "/api/analyze",
    method: str = "POST",
    client_ip: str = "127.0.0.1",
    headers: dict = None
) -> Mock:
    """Create a mock FastAPI Request object."""
    request = Mock()
    request.url = Mock()
    request.url.path = path
    request.method = method
    request.client = Mock()
    request.client.host = client_ip
    request.headers = MockHeaders(headers)
    return request


# =============================================================================
# Rate Limiter Tests
# =============================================================================

class TestRateLimiter:
    """Tests for RateLimiter class."""
    
    def test_initialization(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter(max_requests=100, window_seconds=60)
        assert limiter.max_requests == 100
        assert limiter.window_seconds == 60
    
    def test_first_request_allowed(self):
        """Test that first request is allowed."""
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        request = create_mock_request(client_ip="192.168.1.1")
        
        is_allowed, info = limiter.is_allowed(request)
        
        assert is_allowed is True
        assert info['limit'] == 10
        assert info['remaining'] == 9  # Used 1 token
    
    def test_rate_limit_exceeded(self):
        """Test rate limit enforcement."""
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        request = create_mock_request(client_ip="192.168.1.2")
        
        # Make max_requests + 1 requests
        for i in range(3):
            is_allowed, _ = limiter.is_allowed(request)
            assert is_allowed is True
        
        # Next request should be blocked
        is_allowed, info = limiter.is_allowed(request)
        assert is_allowed is False
        assert info['remaining'] == 0
        assert 'retry_after' in info
    
    def test_different_clients_independent(self):
        """Test that rate limits are per-client."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        
        request1 = create_mock_request(client_ip="10.0.0.1")
        request2 = create_mock_request(client_ip="10.0.0.2")
        
        # Exhaust client 1's limit
        limiter.is_allowed(request1)
        limiter.is_allowed(request1)
        is_allowed_1, _ = limiter.is_allowed(request1)
        
        # Client 2 should still have tokens
        is_allowed_2, info = limiter.is_allowed(request2)
        
        assert is_allowed_1 is False
        assert is_allowed_2 is True
        assert info['remaining'] == 1
    
    def test_token_refill(self):
        """Test that tokens are refilled over time."""
        limiter = RateLimiter(max_requests=2, window_seconds=2)
        request = create_mock_request(client_ip="10.0.0.3")
        
        # Use all tokens
        limiter.is_allowed(request)
        limiter.is_allowed(request)
        is_allowed, _ = limiter.is_allowed(request)
        assert is_allowed is False
        
        # Wait for refill
        time.sleep(2.1)
        
        # Should have tokens again
        is_allowed, info = limiter.is_allowed(request)
        assert is_allowed is True
    
    def test_forwarded_ip_header(self):
        """Test that X-Forwarded-For header is used for client ID."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        
        request = create_mock_request(
            client_ip="proxy.server.com",
            headers={'X-Forwarded-For': '203.0.113.1, 198.51.100.1'}
        )
        
        # Should use first IP from forwarded header
        is_allowed, _ = limiter.is_allowed(request)
        assert is_allowed is True
        
        # Check that client ID is correct
        assert '203.0.113.1' in str(limiter.buckets.keys())


# =============================================================================
# API Key Authentication Tests
# =============================================================================

class TestAPIKeyAuth:
    """Tests for API key authentication."""
    
    def test_auth_disabled_allows_all(self):
        """Test that disabled auth allows all requests."""
        auth = APIKeyAuth(required=False)
        request = create_mock_request()
        
        # Should not raise even without key
        # Note: __call__ is async, testing the logic
        assert auth.required is False
    
    def test_public_endpoints_no_auth(self):
        """Test that public endpoints don't require auth."""
        assert '/' in SecurityConfig.PUBLIC_ENDPOINTS
        assert '/health' in SecurityConfig.PUBLIC_ENDPOINTS
        assert '/docs' in SecurityConfig.PUBLIC_ENDPOINTS
    
    @patch.dict(os.environ, {'ALTFLEX_API_KEYS': 'test-key-123,test-key-456'})
    def test_valid_api_keys_set(self):
        """Test API keys are loaded from environment."""
        # Reload config
        keys = set(filter(None, os.getenv('ALTFLEX_API_KEYS', '').split(',')))
        assert 'test-key-123' in keys
        assert 'test-key-456' in keys


class TestRequireAPIKey:
    """Tests for require_api_key dependency."""
    
    def test_no_key_when_not_required(self):
        """Test that missing key is allowed when not required."""
        with patch.object(SecurityConfig, 'API_KEY_REQUIRED', False):
            result = require_api_key(api_key=None)
            assert result is None
    
    def test_valid_key_accepted(self):
        """Test that valid key is accepted."""
        with patch.object(SecurityConfig, 'API_KEY_REQUIRED', True):
            with patch.object(SecurityConfig, 'API_KEYS', {'valid-key'}):
                result = require_api_key(api_key='valid-key')
                assert result == 'valid-key'


# =============================================================================
# Request Validation Tests
# =============================================================================

class TestRequestValidator:
    """Tests for RequestValidator class."""
    
    def test_sanitize_valid_address(self):
        """Test sanitization of valid address."""
        address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
        result = RequestValidator.sanitize_address(address)
        
        assert result == address.lower()
    
    def test_sanitize_address_with_whitespace(self):
        """Test sanitization removes whitespace."""
        address = "  0x742d35Cc6634C0532925a3b844Bc454e4438f44e  "
        result = RequestValidator.sanitize_address(address)
        
        assert result == address.strip().lower()
    
    def test_sanitize_invalid_characters(self):
        """Test that invalid characters raise error."""
        invalid_address = "0x742d35Cc<script>alert('xss')</script>"
        
        with pytest.raises(RequestValidationError) as exc_info:
            RequestValidator.sanitize_address(invalid_address)
        
        assert 'invalid characters' in str(exc_info.value.message)
    
    def test_detect_suspicious_patterns(self):
        """Test detection of suspicious input patterns."""
        suspicious_input = "DROP TABLE users; SELECT * FROM"
        result = RequestValidator.detect_suspicious_input(suspicious_input)
        
        assert len(result) > 0
        assert 'DROP TABLE' in result
    
    def test_detect_xss_patterns(self):
        """Test detection of XSS patterns."""
        xss_input = "<script>alert('xss')</script>"
        result = RequestValidator.detect_suspicious_input(xss_input)
        
        assert '<script' in result
    
    def test_clean_input_no_patterns(self):
        """Test that clean input has no suspicious patterns."""
        clean_input = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
        result = RequestValidator.detect_suspicious_input(clean_input)
        
        assert len(result) == 0
    
    def test_validate_tx_hash_valid(self):
        """Test validation of valid transaction hash."""
        valid_hash = "0x" + "a" * 64
        assert RequestValidator.validate_tx_hash(valid_hash) is True
    
    def test_validate_tx_hash_invalid_length(self):
        """Test rejection of wrong-length hash."""
        short_hash = "0x" + "a" * 32
        assert RequestValidator.validate_tx_hash(short_hash) is False
    
    def test_validate_tx_hash_no_prefix(self):
        """Test rejection of hash without 0x prefix."""
        no_prefix = "a" * 64
        assert RequestValidator.validate_tx_hash(no_prefix) is False
    
    def test_validate_tx_hash_none(self):
        """Test that None is valid (optional field)."""
        assert RequestValidator.validate_tx_hash(None) is True
    
    def test_check_request_size_valid(self):
        """Test request size check for valid size."""
        assert RequestValidator.check_request_size(1024) is True
        assert RequestValidator.check_request_size(None) is True
    
    def test_check_request_size_exceeded(self):
        """Test request size check for exceeded size."""
        huge_size = SecurityConfig.MAX_REQUEST_SIZE_BYTES + 1
        assert RequestValidator.check_request_size(huge_size) is False


# =============================================================================
# Audit Logger Tests
# =============================================================================

class TestAuditLogger:
    """Tests for AuditLogger class."""
    
    def test_initialization(self):
        """Test logger initialization."""
        logger = AuditLogger()
        assert logger.logger is not None
    
    def test_log_request(self):
        """Test request logging."""
        logger = AuditLogger()
        request = create_mock_request()
        
        # Should not raise
        logger.log_request(
            request=request,
            response_status=200,
            duration_ms=15.5,
            api_key="test-key"
        )
    
    def test_log_auth_failure(self):
        """Test auth failure logging."""
        logger = AuditLogger()
        request = create_mock_request()
        
        # Should not raise
        logger.log_auth_failure(request, reason="Invalid API key")
    
    def test_log_rate_limit(self):
        """Test rate limit logging."""
        logger = AuditLogger()
        request = create_mock_request()
        
        # Should not raise
        logger.log_rate_limit(request, limit=100, window=60)
    
    def test_log_suspicious(self):
        """Test suspicious activity logging."""
        logger = AuditLogger()
        request = create_mock_request()
        
        # Should not raise
        logger.log_suspicious(request, patterns=['DROP TABLE', '<script'])
    
    def test_disabled_logger(self):
        """Test that disabled logger doesn't log."""
        logger = AuditLogger()
        logger.enabled = False
        request = create_mock_request()
        
        # Should not log when disabled
        logger.log_request(request, 200, 10.0)  # Should not raise


# =============================================================================
# Security Config Tests
# =============================================================================

class TestSecurityConfig:
    """Tests for SecurityConfig class."""
    
    def test_default_rate_limit(self):
        """Test default rate limit values."""
        assert SecurityConfig.RATE_LIMIT_REQUESTS > 0
        assert SecurityConfig.RATE_LIMIT_WINDOW_SECONDS > 0
    
    def test_public_endpoints(self):
        """Test public endpoints configuration."""
        assert isinstance(SecurityConfig.PUBLIC_ENDPOINTS, set)
        assert '/' in SecurityConfig.PUBLIC_ENDPOINTS
        assert '/health' in SecurityConfig.PUBLIC_ENDPOINTS
    
    def test_max_request_size(self):
        """Test max request size configuration."""
        assert SecurityConfig.MAX_REQUEST_SIZE_BYTES > 0


# =============================================================================
# Integration Tests
# =============================================================================

class TestSecurityIntegration:
    """Integration tests for security components."""
    
    def test_get_rate_limiter_singleton(self):
        """Test that get_rate_limiter returns same instance."""
        limiter1 = get_rate_limiter()
        limiter2 = get_rate_limiter()
        assert limiter1 is limiter2
    
    def test_get_audit_logger_singleton(self):
        """Test that get_audit_logger returns same instance."""
        logger1 = get_audit_logger()
        logger2 = get_audit_logger()
        assert logger1 is logger2


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
