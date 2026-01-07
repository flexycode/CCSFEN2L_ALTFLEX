"""
AltFlex API Main Application.

FastAPI backend for the AI-powered forensic framework for exploit detection
in Web3 cross-chain bridges and DeFi protocols.
"""

import os
import sys
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import schemas
from src.app.schemas import (
    TransactionAnalysisRequest,
    TransactionAnalysisResponse,
    AddressAnalysisRequest,
    AddressCheckResponse,
    BatchAnalysisRequest,
    BatchAnalysisResponse,
    ExploitsListResponse,
    ExploitInfo,
    HealthResponse,
    ModelInfoResponse,
    ErrorResponse,
    DetectionRuleResult,
    RiskLevel,
    AnalysisSummary
)

# Import detection modules
from src.forensics.exploit_detector import ExploitDetector
from src.models.feature_engineer import FeatureEngineer
from src.models.anomaly_detector import AnomalyDetector

# Try to load sample data
import pandas as pd


# =============================================================================
# Global State & Initialization
# =============================================================================

# Initialize components (will be set up in lifespan)
exploit_detector: Optional[ExploitDetector] = None
feature_engineer: Optional[FeatureEngineer] = None
anomaly_detector: Optional[AnomalyDetector] = None
sample_transactions: Optional[pd.DataFrame] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup application resources."""
    global exploit_detector, feature_engineer, anomaly_detector, sample_transactions
    
    print("🚀 Initializing AltFlex API...")
    
    # Initialize exploit detector
    try:
        exploit_detector = ExploitDetector()
        print(f"  ✓ Exploit Detector loaded with {len(exploit_detector.known_attacker_addresses)} known attackers")
    except Exception as e:
        print(f"  ✗ Exploit Detector failed: {e}")
        exploit_detector = None
    
    # Initialize feature engineer
    try:
        feature_engineer = FeatureEngineer()
        print("  ✓ Feature Engineer loaded")
    except Exception as e:
        print(f"  ✗ Feature Engineer failed: {e}")
        feature_engineer = None
    
    # Initialize anomaly detector
    try:
        anomaly_detector = AnomalyDetector()
        print("  ✓ Anomaly Detector loaded")
        
        # Try to train on sample data if available
        sample_path = "data/sample_transactions.csv"
        if os.path.exists(sample_path):
            sample_transactions = pd.read_csv(sample_path)
            X, y, feature_names = feature_engineer.prepare_training_data(sample_transactions)
            
            # Only train if we have both classes
            if len(set(y)) > 1:
                anomaly_detector.train(X, y, feature_names)
                print(f"  ✓ Anomaly Detector trained on {len(X)} samples")
            else:
                print("  ⚠ Skipping training - need both normal and malicious samples")
    except Exception as e:
        print(f"  ✗ Anomaly Detector setup failed: {e}")
        anomaly_detector = None
    
    print("✅ AltFlex API ready!")
    
    yield
    
    # Cleanup
    print("👋 Shutting down AltFlex API...")


# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="AltFlex API",
    description="""
    AI-powered forensic framework for exploit detection in Web3 cross-chain bridges and DeFi protocols.
    
    ## Features
    - 🔍 Transaction analysis with ML-based anomaly detection
    - 🛡️ Rule-based exploit signature matching
    - 📊 Known attacker address database
    - 📈 Risk scoring and assessment
    """,
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for Streamlit dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Health & Status Endpoints
# =============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API welcome message."""
    return {
        "message": "Welcome to AltFlex API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check API and component health status."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        components={
            "api": True,
            "anomaly_detector": anomaly_detector is not None,
            "exploit_detector": exploit_detector is not None,
            "feature_engineer": feature_engineer is not None
        }
    )


@app.get("/api/model/info", response_model=ModelInfoResponse, tags=["System"])
async def get_model_info():
    """Get information about the loaded ML model."""
    if anomaly_detector is None:
        raise HTTPException(status_code=503, detail="Anomaly detector not initialized")
    
    info = anomaly_detector.get_model_info()
    return ModelInfoResponse(**info)


# =============================================================================
# Analysis Endpoints
# =============================================================================

@app.post("/api/analyze", response_model=TransactionAnalysisResponse, tags=["Analysis"])
async def analyze_transaction(request: TransactionAnalysisRequest):
    """
    Analyze a single transaction for potential exploits.
    
    Combines rule-based detection and ML anomaly detection.
    """
    if exploit_detector is None:
        raise HTTPException(status_code=503, detail="Exploit detector not initialized")
    
    # Convert request to dict for analysis
    tx_data = request.model_dump()
    
    # Run rule-based detection
    forensics_result = exploit_detector.analyze(tx_data)
    
    # Run ML detection if available
    ml_prediction = None
    if anomaly_detector is not None and feature_engineer is not None:
        try:
            # Create a single-row DataFrame
            df = pd.DataFrame([tx_data])
            features = feature_engineer.process_transaction_data(df)
            
            # Get feature columns (exclude is_flash_loan if present)
            feature_cols = [col for col in features.columns if col not in ['is_flash_loan']]
            X = features[feature_cols].values
            
            detection_results = anomaly_detector.detect(X)
            if detection_results:
                ml_prediction = detection_results[0]
        except Exception as e:
            ml_prediction = {"error": str(e)}
    
    # Convert detection results
    triggered_rules = [
        DetectionRuleResult(**rule) for rule in forensics_result['triggered_rules']
    ]
    
    return TransactionAnalysisResponse(
        tx_hash=request.tx_hash,
        risk_score=forensics_result['risk_score'],
        risk_level=RiskLevel(forensics_result['risk_level']),
        is_suspicious=forensics_result['is_suspicious'],
        triggered_rules=triggered_rules,
        all_rules_checked=forensics_result['all_rules_checked'],
        ml_prediction=ml_prediction
    )


@app.post("/api/analyze/batch", response_model=BatchAnalysisResponse, tags=["Analysis"])
async def analyze_batch(request: BatchAnalysisRequest):
    """Analyze multiple transactions in batch."""
    start_time = time.time()
    
    results = []
    summary_counts = {
        'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'safe': 0, 'suspicious': 0
    }
    
    for tx in request.transactions:
        result = await analyze_transaction(tx)
        results.append(result)
        
        # Update counts
        if result.is_suspicious:
            summary_counts['suspicious'] += 1
        
        level = result.risk_level.value.lower()
        if level == 'critical':
            summary_counts['critical'] += 1
        elif level == 'high':
            summary_counts['high'] += 1
        elif level == 'medium':
            summary_counts['medium'] += 1
        elif level in ['low', 'minimal']:
            summary_counts['low'] += 1
        else:
            summary_counts['safe'] += 1
    
    processing_time = (time.time() - start_time) * 1000
    
    return BatchAnalysisResponse(
        summary=AnalysisSummary(
            total_analyzed=len(results),
            suspicious_count=summary_counts['suspicious'],
            critical_count=summary_counts['critical'],
            high_risk_count=summary_counts['high'],
            medium_risk_count=summary_counts['medium'],
            low_risk_count=summary_counts['low'],
            safe_count=summary_counts['safe']
        ),
        results=results,
        processing_time_ms=processing_time
    )


@app.post("/api/address/check", response_model=AddressCheckResponse, tags=["Analysis"])
async def check_address(request: AddressAnalysisRequest):
    """
    Quick check if an address is a known attacker.
    """
    if exploit_detector is None:
        raise HTTPException(status_code=503, detail="Exploit detector not initialized")
    
    result = exploit_detector.check_address(request.address)
    
    risk_level = RiskLevel.CRITICAL if result['is_known_attacker'] else RiskLevel.SAFE
    message = f"Address is a KNOWN ATTACKER from {result['exploit_info']['name']}" if result['is_known_attacker'] \
              else "Address not found in known attacker database"
    
    return AddressCheckResponse(
        address=request.address,
        is_known_attacker=result['is_known_attacker'],
        risk_level=risk_level,
        exploit_info=result['exploit_info'],
        message=message
    )


# =============================================================================
# Exploits Database Endpoints
# =============================================================================

@app.get("/api/exploits", response_model=ExploitsListResponse, tags=["Database"])
async def list_exploits(
    chain: Optional[str] = Query(None, description="Filter by chain (ethereum, bsc)"),
    attack_type: Optional[str] = Query(None, description="Filter by attack type")
):
    """Get list of known exploits from the database."""
    if exploit_detector is None:
        raise HTTPException(status_code=503, detail="Exploit detector not initialized")
    
    exploits = exploit_detector.get_known_exploits()
    
    # Apply filters
    if chain:
        exploits = [e for e in exploits if e.get('chain', '').lower() == chain.lower()]
    if attack_type:
        exploits = [e for e in exploits if e.get('attack_type', '').lower() == attack_type.lower()]
    
    # Convert to response model
    exploit_infos = []
    for e in exploits:
        exploit_infos.append(ExploitInfo(
            id=e.get('id', 'unknown'),
            name=e.get('name', 'Unknown'),
            date=e.get('date', ''),
            chain=e.get('chain', 'unknown'),
            protocol=e.get('protocol', 'Unknown'),
            loss_usd=e.get('loss_usd', 0),
            attack_type=e.get('attack_type', 'unknown'),
            attack_vector=e.get('attack_vector', ''),
            attacker_addresses=e.get('attacker_addresses', [])
        ))
    
    return ExploitsListResponse(
        total=len(exploit_infos),
        exploits=exploit_infos
    )


@app.get("/api/exploits/{exploit_id}", tags=["Database"])
async def get_exploit(exploit_id: str):
    """Get details of a specific exploit."""
    if exploit_detector is None:
        raise HTTPException(status_code=503, detail="Exploit detector not initialized")
    
    exploits = exploit_detector.get_known_exploits()
    
    for exploit in exploits:
        if exploit.get('id') == exploit_id:
            return exploit
    
    raise HTTPException(status_code=404, detail=f"Exploit '{exploit_id}' not found")


# =============================================================================
# Detection Rules Endpoints
# =============================================================================

@app.get("/api/rules", tags=["Detection"])
async def get_detection_rules():
    """Get the current detection rules configuration."""
    if exploit_detector is None:
        raise HTTPException(status_code=503, detail="Exploit detector not initialized")
    
    return exploit_detector.get_detection_rules()


@app.post("/api/detect/rules", tags=["Detection"])
async def detect_with_rules(request: TransactionAnalysisRequest):
    """Run only rule-based detection (no ML)."""
    if exploit_detector is None:
        raise HTTPException(status_code=503, detail="Exploit detector not initialized")
    
    tx_data = request.model_dump()
    results = exploit_detector.detect_all(tx_data)
    
    return {
        "transaction": request.tx_hash or "N/A",
        "rules_checked": len(results),
        "triggered": sum(1 for r in results if r.is_triggered),
        "results": [
            {
                "rule_id": r.rule_id,
                "rule_name": r.rule_name,
                "is_triggered": r.is_triggered,
                "severity": r.severity,
                "confidence": r.confidence,
                "details": r.details
            }
            for r in results
        ]
    }


@app.post("/api/detect/anomaly", tags=["Detection"])
async def detect_with_ml(request: TransactionAnalysisRequest):
    """Run only ML-based anomaly detection."""
    if anomaly_detector is None or feature_engineer is None:
        raise HTTPException(status_code=503, detail="ML components not initialized")
    
    tx_data = request.model_dump()
    df = pd.DataFrame([tx_data])
    
    try:
        features = feature_engineer.process_transaction_data(df)
        feature_cols = [col for col in features.columns if col not in ['is_flash_loan']]
        X = features[feature_cols].values
        
        detection_results = anomaly_detector.detect(X)
        
        return {
            "transaction": request.tx_hash or "N/A",
            "ml_result": detection_results[0] if detection_results else None,
            "features_used": feature_cols
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML detection failed: {str(e)}")


# =============================================================================
# Error Handlers
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app.main:app", host="0.0.0.0", port=8000, reload=True)
