"""
API endpoint tests for AltFlex.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# Test Client Setup
# =============================================================================

@pytest.fixture(scope="module")
def client():
    """Create test client for API."""
    from src.app.main import app
    with TestClient(app) as c:
        yield c


# =============================================================================
# Health Endpoint Tests
# =============================================================================

class TestHealthEndpoints:
    """Tests for health and status endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns welcome message."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "AltFlex" in data["message"]
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "components" in data


# =============================================================================
# Analysis Endpoint Tests
# =============================================================================

class TestAnalysisEndpoints:
    """Tests for transaction analysis endpoints."""
    
    def test_analyze_transaction(self, client):
        """Test single transaction analysis."""
        tx_data = {
            "from_address": "0x1234567890abcdef1234567890abcdef12345678",
            "to_address": "0xabcdef1234567890abcdef1234567890abcdef12",
            "value_eth": 1.5,
            "gas_used": 100000,
            "gas_price_gwei": 25.0,
            "is_flash_loan": False
        }
        
        response = client.post("/api/analyze", json=tx_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "risk_score" in data
        assert "risk_level" in data
        assert "triggered_rules" in data
    
    def test_analyze_suspicious_transaction(self, client):
        """Test analysis of suspicious transaction."""
        tx_data = {
            "from_address": "0xb66cd966670d962C227B3EABA30a872DbFb995db",  # Known attacker
            "to_address": "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9",
            "value_eth": 5000.0,
            "gas_used": 2000000,
            "gas_price_gwei": 150.0,
            "is_flash_loan": True
        }
        
        response = client.post("/api/analyze", json=tx_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_suspicious"] == True
        assert len(data["triggered_rules"]) > 0
    
    def test_analyze_invalid_data(self, client):
        """Test analysis with invalid data."""
        # Missing required fields
        tx_data = {
            "value_eth": 1.5
        }
        
        response = client.post("/api/analyze", json=tx_data)
        
        # Should return validation error
        assert response.status_code == 422


# =============================================================================
# Address Check Endpoint Tests
# =============================================================================

class TestAddressEndpoints:
    """Tests for address checking endpoints."""
    
    def test_check_known_attacker(self, client):
        """Test checking a known attacker address."""
        response = client.post(
            "/api/address/check",
            json={"address": "0xb66cd966670d962C227B3EABA30a872DbFb995db"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_known_attacker"] == True
        assert data["exploit_info"] is not None
    
    def test_check_unknown_address(self, client):
        """Test checking an unknown address."""
        response = client.post(
            "/api/address/check",
            json={"address": "0x1234567890abcdef1234567890abcdef12345678"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_known_attacker"] == False


# =============================================================================
# Exploits Database Endpoint Tests
# =============================================================================

class TestExploitsEndpoints:
    """Tests for exploits database endpoints."""
    
    def test_list_exploits(self, client):
        """Test listing all exploits."""
        response = client.get("/api/exploits")
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "exploits" in data
        assert data["total"] > 0
    
    def test_list_exploits_with_filter(self, client):
        """Test listing exploits with chain filter."""
        response = client.get("/api/exploits?chain=ethereum")
        
        assert response.status_code == 200
        data = response.json()
        # All returned exploits should be on ethereum
        for exploit in data["exploits"]:
            assert exploit["chain"].lower() == "ethereum"
    
    def test_get_specific_exploit(self, client):
        """Test getting a specific exploit by ID."""
        response = client.get("/api/exploits/euler-2023")
        
        assert response.status_code == 200
        data = response.json()
        assert "Euler" in data["name"]
    
    def test_get_nonexistent_exploit(self, client):
        """Test getting a non-existent exploit."""
        response = client.get("/api/exploits/nonexistent-exploit")
        
        assert response.status_code == 404


# =============================================================================
# Detection Endpoint Tests
# =============================================================================

class TestDetectionEndpoints:
    """Tests for detection-specific endpoints."""
    
    def test_rules_only_detection(self, client):
        """Test rule-based detection only."""
        tx_data = {
            "from_address": "0x1234567890abcdef1234567890abcdef12345678",
            "to_address": "0xabcdef1234567890abcdef1234567890abcdef12",
            "value_eth": 500.0,  # Large value
            "gas_used": 100000,
            "gas_price_gwei": 25.0
        }
        
        response = client.post("/api/detect/rules", json=tx_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "rules_checked" in data
        assert "results" in data
    
    def test_get_detection_rules(self, client):
        """Test getting detection rules configuration."""
        response = client.get("/api/rules")
        
        assert response.status_code == 200
        # Should return rules config


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
