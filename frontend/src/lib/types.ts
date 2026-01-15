/**
 * AltFlex API Types
 * TypeScript definitions for backend API responses
 */

// =============================================================================
// Transaction Analysis Types
// =============================================================================

export interface TransactionInput {
    tx_hash?: string;
    from_address: string;
    to_address: string;
    value_eth: number;
    gas_used: number;
    gas_price_gwei: number;
    block_number?: number;
    timestamp?: number;
    is_flash_loan?: boolean;
}

export interface DetectionRule {
    rule_id: string;
    rule_name: string;
    is_triggered: boolean;
    severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
    confidence: number;
    details: string;
}

export interface TransactionAnalysisResponse {
    tx_hash: string;
    risk_score: number;
    risk_level: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "SAFE" | "MINIMAL";
    is_suspicious: boolean;
    triggered_rules: DetectionRule[];
    all_rules_checked: string[];
    ml_prediction?: {
        is_anomaly: boolean;
        confidence: number;
        anomaly_score: number;
    };
}

// =============================================================================
// Address Verification Types
// =============================================================================

export interface AddressCheckRequest {
    address: string;
}

export interface AddressCheckResponse {
    address: string;
    is_known_attacker: boolean;
    risk_level: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "SAFE";
    exploit_info: {
        name: string;
        date: string;
        loss_usd: number;
    } | null;
    message: string;
}

// =============================================================================
// Exploit Database Types
// =============================================================================

export interface Exploit {
    id: string;
    name: string;
    date: string;
    chain: string;
    protocol: string;
    loss_usd: number;
    attack_type: string;
    attack_vector: string;
    attacker_addresses: string[];
}

export interface ExploitsListResponse {
    total: number;
    exploits: Exploit[];
}

// =============================================================================
// Health & System Types
// =============================================================================

export interface HealthResponse {
    status: "healthy" | "unhealthy";
    version: string;
    timestamp: string;
    components: {
        api: boolean;
        anomaly_detector: boolean;
        exploit_detector: boolean;
        feature_engineer: boolean;
    };
}

export interface ModelInfoResponse {
    model_type: string;
    is_trained: boolean;
    feature_count: number;
    features: string[];
    training_samples?: number;
}

// =============================================================================
// UI Component Types
// =============================================================================

export interface MetricCard {
    title: string;
    value: string | number;
    change?: number;
    trend?: "up" | "down" | "neutral";
    icon?: React.ReactNode;
}

export interface NavItem {
    title: string;
    href: string;
    icon: React.ReactNode;
    badge?: string | number;
}
