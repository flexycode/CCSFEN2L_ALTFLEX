/**
 * AltFlex API Client
 * Handles all communication with the FastAPI backend
 */

import type {
    TransactionInput,
    TransactionAnalysisResponse,
    AddressCheckResponse,
    ExploitsListResponse,
    HealthResponse,
    ModelInfoResponse,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "";

/**
 * Base fetch wrapper with error handling and headers
 */
async function apiFetch<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const url = `${API_URL}${endpoint}`;

    const headers: HeadersInit = {
        "Content-Type": "application/json",
        ...(API_KEY && { "X-API-Key": API_KEY }),
        ...options.headers,
    };

    const response = await fetch(url, {
        ...options,
        headers,
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
}

// =============================================================================
// Health & Status
// =============================================================================

/**
 * Check API health status
 */
export async function getHealth(): Promise<HealthResponse> {
    return apiFetch<HealthResponse>("/health");
}

/**
 * Get ML model information
 */
export async function getModelInfo(): Promise<ModelInfoResponse> {
    return apiFetch<ModelInfoResponse>("/api/model/info");
}

// =============================================================================
// Transaction Analysis
// =============================================================================

/**
 * Analyze a single transaction
 */
export async function analyzeTransaction(
    data: TransactionInput
): Promise<TransactionAnalysisResponse> {
    return apiFetch<TransactionAnalysisResponse>("/api/analyze", {
        method: "POST",
        body: JSON.stringify(data),
    });
}

/**
 * Analyze multiple transactions in batch
 */
export async function analyzeBatch(
    transactions: TransactionInput[]
): Promise<{
    summary: {
        total_analyzed: number;
        suspicious_count: number;
        critical_count: number;
        high_risk_count: number;
        medium_risk_count: number;
        low_risk_count: number;
        safe_count: number;
    };
    results: TransactionAnalysisResponse[];
    processing_time_ms: number;
}> {
    return apiFetch("/api/analyze/batch", {
        method: "POST",
        body: JSON.stringify({ transactions }),
    });
}

// =============================================================================
// Address Verification
// =============================================================================

/**
 * Check if an address is a known attacker
 */
export async function checkAddress(
    address: string
): Promise<AddressCheckResponse> {
    return apiFetch<AddressCheckResponse>("/api/address/check", {
        method: "POST",
        body: JSON.stringify({ address }),
    });
}

// =============================================================================
// Exploit Database
// =============================================================================

/**
 * Get list of known exploits
 */
export async function getExploits(params?: {
    chain?: string;
    attack_type?: string;
}): Promise<ExploitsListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.chain) searchParams.set("chain", params.chain);
    if (params?.attack_type) searchParams.set("attack_type", params.attack_type);

    const query = searchParams.toString();
    const endpoint = query ? `/api/exploits?${query}` : "/api/exploits";

    return apiFetch<ExploitsListResponse>(endpoint);
}

/**
 * Get details of a specific exploit
 */
export async function getExploit(exploitId: string): Promise<unknown> {
    return apiFetch(`/api/exploits/${exploitId}`);
}

// =============================================================================
// Detection
// =============================================================================

/**
 * Run rule-based detection only
 */
export async function detectWithRules(
    data: TransactionInput
): Promise<{
    transaction: string;
    rules_checked: number;
    triggered: number;
    results: Array<{
        rule_id: string;
        rule_name: string;
        is_triggered: boolean;
        severity: string;
        confidence: number;
        details: string;
    }>;
}> {
    return apiFetch("/api/detect/rules", {
        method: "POST",
        body: JSON.stringify(data),
    });
}

/**
 * Run ML-based anomaly detection only
 */
export async function detectWithML(
    data: TransactionInput
): Promise<{
    transaction: string;
    ml_result: {
        is_anomaly: boolean;
        confidence: number;
        anomaly_score: number;
    } | null;
    features_used: string[];
}> {
    return apiFetch("/api/detect/anomaly", {
        method: "POST",
        body: JSON.stringify(data),
    });
}
