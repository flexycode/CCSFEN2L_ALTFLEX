"""
API Schemas Module.

Pydantic models for request/response validation in the AltFlex API.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


# =============================================================================
# Enums
# =============================================================================

class RiskLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    MINIMAL = "MINIMAL"
    SAFE = "SAFE"


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# =============================================================================
# Request Models
# =============================================================================

class TransactionAnalysisRequest(BaseModel):
    """Request model for analyzing a single transaction."""
    tx_hash: Optional[str] = Field(None, description="Transaction hash")
    from_address: str = Field(..., description="Sender address")
    to_address: str = Field(..., description="Recipient address")
    value_eth: float = Field(..., ge=0, description="Transaction value in ETH")
    gas_used: int = Field(500000, ge=0, description="Gas used")
    gas_price_gwei: float = Field(30.0, ge=0, description="Gas price in gwei")
    block_number: Optional[int] = Field(None, description="Block number")
    timestamp: Optional[int] = Field(None, description="Unix timestamp")
    is_flash_loan: bool = Field(False, description="Flash loan indicator")
    
    class Config:
        json_schema_extra = {
            "example": {
                "from_address": "0x1234567890abcdef1234567890abcdef12345678",
                "to_address": "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9",
                "value_eth": 150.5,
                "gas_used": 250000,
                "gas_price_gwei": 45.0,
                "is_flash_loan": False
            }
        }


class AddressAnalysisRequest(BaseModel):
    """Request model for analyzing an address."""
    address: str = Field(..., description="Ethereum address to analyze")
    include_transactions: bool = Field(True, description="Include transaction analysis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "address": "0xb66cd966670d962C227B3EABA30a872DbFb995db",
                "include_transactions": True
            }
        }


class BatchAnalysisRequest(BaseModel):
    """Request model for batch transaction analysis."""
    transactions: List[TransactionAnalysisRequest] = Field(..., min_length=1, max_length=100)


# =============================================================================
# Response Models
# =============================================================================

class DetectionRuleResult(BaseModel):
    """Result of a single detection rule."""
    rule_id: str
    rule_name: str
    is_triggered: bool
    severity: str
    confidence: float
    details: str
    indicators: List[str]


class TransactionAnalysisResponse(BaseModel):
    """Response model for transaction analysis."""
    success: bool = True
    tx_hash: Optional[str] = None
    
    # Risk assessment
    risk_score: float = Field(..., ge=0, le=1, description="Overall risk score (0-1)")
    risk_level: RiskLevel
    is_suspicious: bool
    
    # Detection results
    triggered_rules: List[DetectionRuleResult]
    all_rules_checked: int
    
    # ML prediction (optional)
    ml_prediction: Optional[Dict[str, Any]] = None
    
    # Metadata
    analysis_timestamp: datetime = Field(default_factory=datetime.now)


class AddressCheckResponse(BaseModel):
    """Response for quick address check."""
    address: str
    is_known_attacker: bool
    risk_level: RiskLevel
    exploit_info: Optional[Dict[str, Any]] = None
    message: str


class ExploitInfo(BaseModel):
    """Information about a known exploit."""
    id: str
    name: str
    date: str
    chain: str
    protocol: str
    loss_usd: int
    attack_type: str
    attack_vector: str
    attacker_addresses: List[str]


class ExploitsListResponse(BaseModel):
    """Response containing list of known exploits."""
    total: int
    exploits: List[ExploitInfo]


class HealthResponse(BaseModel):
    """API health check response."""
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)
    components: Dict[str, bool] = Field(
        default_factory=lambda: {
            "api": True,
            "anomaly_detector": True,
            "exploit_detector": True,
            "feature_engineer": True
        }
    )


class ModelInfoResponse(BaseModel):
    """Response with model information."""
    is_trained: bool
    model_type: str
    n_features: int
    feature_names: List[str]
    training_stats: Dict[str, Any]


class AnalysisSummary(BaseModel):
    """Summary of multiple analyses."""
    total_analyzed: int
    suspicious_count: int
    critical_count: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    safe_count: int


class BatchAnalysisResponse(BaseModel):
    """Response for batch analysis."""
    success: bool = True
    summary: AnalysisSummary
    results: List[TransactionAnalysisResponse]
    processing_time_ms: float


# =============================================================================
# Error Models
# =============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
