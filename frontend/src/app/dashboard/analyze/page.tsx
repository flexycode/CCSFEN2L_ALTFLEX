"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Search, Loader2, AlertTriangle, CheckCircle, XCircle } from "lucide-react";
import { Header } from "@/components/layout/Header";
import { analyzeTransaction } from "@/lib/api";
import type { TransactionInput, TransactionAnalysisResponse } from "@/lib/types";
import { cn, getRiskColor, getRiskBadge } from "@/lib/utils";

export default function AnalyzePage() {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<TransactionAnalysisResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const [formData, setFormData] = useState<TransactionInput>({
        from_address: "",
        to_address: "",
        value_eth: 0,
        gas_used: 21000,
        gas_price_gwei: 20,
        is_flash_loan: false,
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await analyzeTransaction(formData);
            setResult(response);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Analysis failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <Header title="Transaction Analysis" subtitle="Deep analysis with ML-powered detection" />

            <div className="p-8">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Input Form */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                    >
                        <div className="glass-card p-6">
                            <h3 className="text-lg font-semibold text-white mb-6">Transaction Details</h3>

                            <form onSubmit={handleSubmit} className="space-y-4">
                                <div>
                                    <label className="block text-sm text-[#94A3B8] mb-2">From Address</label>
                                    <input
                                        type="text"
                                        placeholder="0x..."
                                        value={formData.from_address}
                                        onChange={(e) => setFormData({ ...formData, from_address: e.target.value })}
                                        className="w-full h-12 px-4 bg-[#1E293B] border border-[#334155] rounded-xl text-white font-mono text-sm focus:outline-none focus:border-[#3B82F6] transition-colors"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm text-[#94A3B8] mb-2">To Address</label>
                                    <input
                                        type="text"
                                        placeholder="0x..."
                                        value={formData.to_address}
                                        onChange={(e) => setFormData({ ...formData, to_address: e.target.value })}
                                        className="w-full h-12 px-4 bg-[#1E293B] border border-[#334155] rounded-xl text-white font-mono text-sm focus:outline-none focus:border-[#3B82F6] transition-colors"
                                        required
                                    />
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm text-[#94A3B8] mb-2">Value (ETH)</label>
                                        <input
                                            type="number"
                                            step="0.001"
                                            value={formData.value_eth}
                                            onChange={(e) => setFormData({ ...formData, value_eth: parseFloat(e.target.value) || 0 })}
                                            className="w-full h-12 px-4 bg-[#1E293B] border border-[#334155] rounded-xl text-white text-sm focus:outline-none focus:border-[#3B82F6] transition-colors"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm text-[#94A3B8] mb-2">Gas Used</label>
                                        <input
                                            type="number"
                                            value={formData.gas_used}
                                            onChange={(e) => setFormData({ ...formData, gas_used: parseInt(e.target.value) || 0 })}
                                            className="w-full h-12 px-4 bg-[#1E293B] border border-[#334155] rounded-xl text-white text-sm focus:outline-none focus:border-[#3B82F6] transition-colors"
                                        />
                                    </div>
                                </div>

                                <div className="flex items-center gap-3">
                                    <input
                                        type="checkbox"
                                        id="flash_loan"
                                        checked={formData.is_flash_loan}
                                        onChange={(e) => setFormData({ ...formData, is_flash_loan: e.target.checked })}
                                        className="w-5 h-5 rounded bg-[#1E293B] border-[#334155]"
                                    />
                                    <label htmlFor="flash_loan" className="text-sm text-[#94A3B8]">
                                        Mark as Flash Loan Transaction
                                    </label>
                                </div>

                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="w-full btn-primary flex items-center justify-center gap-2"
                                >
                                    {loading ? (
                                        <>
                                            <Loader2 className="w-5 h-5 animate-spin" />
                                            Analyzing...
                                        </>
                                    ) : (
                                        <>
                                            <Search className="w-5 h-5" />
                                            Analyze Transaction
                                        </>
                                    )}
                                </button>
                            </form>
                        </div>
                    </motion.div>

                    {/* Results */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                    >
                        {error && (
                            <div className="glass-card p-6 border-[#EF4444]/30">
                                <div className="flex items-center gap-3 text-[#EF4444]">
                                    <XCircle className="w-6 h-6" />
                                    <div>
                                        <h4 className="font-semibold">Analysis Failed</h4>
                                        <p className="text-sm opacity-80">{error}</p>
                                    </div>
                                </div>
                            </div>
                        )}

                        {result && (
                            <div className="space-y-4">
                                {/* Risk Score */}
                                <div className="glass-card p-6">
                                    <div className="flex items-center justify-between mb-4">
                                        <h3 className="text-lg font-semibold text-white">Risk Assessment</h3>
                                        <span className={cn("badge", getRiskBadge(result.risk_level))}>
                                            {result.risk_level}
                                        </span>
                                    </div>

                                    <div className="flex items-center gap-6">
                                        <div className="relative w-32 h-32">
                                            <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                                                <circle
                                                    cx="50"
                                                    cy="50"
                                                    r="45"
                                                    fill="none"
                                                    stroke="#1E293B"
                                                    strokeWidth="8"
                                                />
                                                <circle
                                                    cx="50"
                                                    cy="50"
                                                    r="45"
                                                    fill="none"
                                                    stroke={result.risk_score >= 0.7 ? "#EF4444" : result.risk_score >= 0.4 ? "#F59E0B" : "#10B981"}
                                                    strokeWidth="8"
                                                    strokeLinecap="round"
                                                    strokeDasharray={`${result.risk_score * 283} 283`}
                                                />
                                            </svg>
                                            <div className="absolute inset-0 flex items-center justify-center">
                                                <span className="text-3xl font-bold text-white">
                                                    {Math.round(result.risk_score * 100)}
                                                </span>
                                            </div>
                                        </div>
                                        <div>
                                            <p className="text-sm text-[#64748B] mb-1">Risk Score</p>
                                            <p className={cn("text-2xl font-bold", getRiskColor(result.risk_level))}>
                                                {result.risk_level}
                                            </p>
                                            <p className="text-sm text-[#94A3B8] mt-2">
                                                {result.triggered_rules.length} rules triggered
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                {/* Triggered Rules */}
                                {result.triggered_rules.length > 0 && (
                                    <div className="glass-card p-6">
                                        <h3 className="text-lg font-semibold text-white mb-4">Triggered Rules</h3>
                                        <div className="space-y-3">
                                            {result.triggered_rules.map((rule) => (
                                                <div
                                                    key={rule.rule_id}
                                                    className="p-4 rounded-xl bg-[#1E293B] border border-[#334155]"
                                                >
                                                    <div className="flex items-center justify-between mb-2">
                                                        <span className="font-medium text-white">{rule.rule_name}</span>
                                                        <span className={cn("badge", getRiskBadge(rule.severity))}>
                                                            {rule.severity}
                                                        </span>
                                                    </div>
                                                    <p className="text-sm text-[#94A3B8]">{rule.details}</p>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* ML Prediction */}
                                {result.ml_prediction && (
                                    <div className="glass-card p-6">
                                        <h3 className="text-lg font-semibold text-white mb-4">ML Prediction</h3>
                                        <div className="flex items-center gap-4">
                                            {result.ml_prediction.is_anomaly ? (
                                                <AlertTriangle className="w-8 h-8 text-[#F59E0B]" />
                                            ) : (
                                                <CheckCircle className="w-8 h-8 text-[#10B981]" />
                                            )}
                                            <div>
                                                <p className="font-medium text-white">
                                                    {result.ml_prediction.is_anomaly ? "Anomaly Detected" : "Normal Transaction"}
                                                </p>
                                                <p className="text-sm text-[#94A3B8]">
                                                    Confidence: {Math.round(result.ml_prediction.confidence * 100)}%
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}

                        {!result && !error && (
                            <div className="glass-card p-12 flex items-center justify-center">
                                <div className="text-center text-[#64748B]">
                                    <Search className="w-16 h-16 mx-auto mb-4 opacity-50" />
                                    <p className="text-lg">Enter transaction details</p>
                                    <p className="text-sm mt-1">Results will appear here</p>
                                </div>
                            </div>
                        )}
                    </motion.div>
                </div>
            </div>
        </>
    );
}
