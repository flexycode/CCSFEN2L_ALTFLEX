"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { CheckCircle, Loader2, XCircle, Shield, AlertTriangle, Copy, Check } from "lucide-react";
import { Header } from "@/components/layout/Header";
import { checkAddress } from "@/lib/api";
import type { AddressCheckResponse } from "@/lib/types";
import { cn, formatAddress, formatCurrency } from "@/lib/utils";

export default function VerifyPage() {
    const [loading, setLoading] = useState(false);
    const [address, setAddress] = useState("");
    const [result, setResult] = useState<AddressCheckResponse | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [copied, setCopied] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!address.trim()) return;

        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await checkAddress(address.trim());
            setResult(response);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Verification failed");
        } finally {
            setLoading(false);
        }
    };

    const copyAddress = () => {
        navigator.clipboard.writeText(address);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <>
            <Header title="Address Verification" subtitle="5-layer security verification for Ethereum addresses" />

            <div className="p-8 max-w-4xl mx-auto">
                {/* Search Form */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="glass-card p-8 mb-8"
                >
                    <form onSubmit={handleSubmit}>
                        <label className="block text-sm text-[#94A3B8] mb-3">Enter Ethereum Address</label>
                        <div className="flex gap-4">
                            <div className="flex-1 relative">
                                <input
                                    type="text"
                                    placeholder="0x..."
                                    value={address}
                                    onChange={(e) => setAddress(e.target.value)}
                                    className="w-full h-14 px-6 bg-[#1E293B] border border-[#334155] rounded-xl text-white font-mono text-lg focus:outline-none focus:border-[#3B82F6] transition-colors"
                                />
                                {address && (
                                    <button
                                        type="button"
                                        onClick={copyAddress}
                                        className="absolute right-4 top-1/2 -translate-y-1/2 text-[#64748B] hover:text-white transition-colors"
                                    >
                                        {copied ? <Check className="w-5 h-5 text-[#10B981]" /> : <Copy className="w-5 h-5" />}
                                    </button>
                                )}
                            </div>
                            <button
                                type="submit"
                                disabled={loading || !address.trim()}
                                className="btn-primary px-8 flex items-center gap-2"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        Verifying...
                                    </>
                                ) : (
                                    <>
                                        <Shield className="w-5 h-5" />
                                        Verify
                                    </>
                                )}
                            </button>
                        </div>
                    </form>
                </motion.div>

                {/* Error */}
                {error && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="glass-card p-6 border-[#EF4444]/30 mb-8"
                    >
                        <div className="flex items-center gap-3 text-[#EF4444]">
                            <XCircle className="w-6 h-6" />
                            <div>
                                <h4 className="font-semibold">Verification Failed</h4>
                                <p className="text-sm opacity-80">{error}</p>
                            </div>
                        </div>
                    </motion.div>
                )}

                {/* Result */}
                {result && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-6"
                    >
                        {/* Status Banner */}
                        <div
                            className={cn(
                                "glass-card p-8",
                                result.is_known_attacker
                                    ? "border-[#EF4444]/30"
                                    : "border-[#10B981]/30"
                            )}
                        >
                            <div className="flex items-center gap-6">
                                <div
                                    className={cn(
                                        "w-20 h-20 rounded-2xl flex items-center justify-center",
                                        result.is_known_attacker
                                            ? "bg-[#EF4444]/20"
                                            : "bg-[#10B981]/20"
                                    )}
                                >
                                    {result.is_known_attacker ? (
                                        <AlertTriangle className="w-10 h-10 text-[#EF4444]" />
                                    ) : (
                                        <CheckCircle className="w-10 h-10 text-[#10B981]" />
                                    )}
                                </div>
                                <div>
                                    <h2
                                        className={cn(
                                            "text-2xl font-bold mb-2",
                                            result.is_known_attacker ? "text-[#EF4444]" : "text-[#10B981]"
                                        )}
                                    >
                                        {result.is_known_attacker ? "⚠️ Known Attacker" : "✅ Address Safe"}
                                    </h2>
                                    <p className="text-[#94A3B8] text-lg">{result.message}</p>
                                </div>
                            </div>
                        </div>

                        {/* Address Details */}
                        <div className="glass-card p-6">
                            <h3 className="text-lg font-semibold text-white mb-4">Address Details</h3>
                            <div className="space-y-4">
                                <div className="flex items-center justify-between p-4 rounded-xl bg-[#1E293B]">
                                    <span className="text-[#64748B]">Address</span>
                                    <span className="font-mono text-white">{formatAddress(result.address, 10)}</span>
                                </div>
                                <div className="flex items-center justify-between p-4 rounded-xl bg-[#1E293B]">
                                    <span className="text-[#64748B]">Risk Level</span>
                                    <span
                                        className={cn(
                                            "badge",
                                            result.risk_level === "CRITICAL" || result.risk_level === "HIGH"
                                                ? "badge-critical"
                                                : result.risk_level === "MEDIUM"
                                                    ? "badge-warning"
                                                    : "badge-safe"
                                        )}
                                    >
                                        {result.risk_level}
                                    </span>
                                </div>
                                <div className="flex items-center justify-between p-4 rounded-xl bg-[#1E293B]">
                                    <span className="text-[#64748B]">Known Attacker</span>
                                    <span className={result.is_known_attacker ? "text-[#EF4444]" : "text-[#10B981]"}>
                                        {result.is_known_attacker ? "Yes" : "No"}
                                    </span>
                                </div>
                            </div>
                        </div>

                        {/* Exploit Info */}
                        {result.exploit_info && (
                            <div className="glass-card p-6 border-[#EF4444]/20">
                                <h3 className="text-lg font-semibold text-white mb-4">Associated Exploit</h3>
                                <div className="grid grid-cols-3 gap-4">
                                    <div className="p-4 rounded-xl bg-[#1E293B]">
                                        <p className="text-sm text-[#64748B] mb-1">Exploit Name</p>
                                        <p className="text-white font-semibold">{result.exploit_info.name}</p>
                                    </div>
                                    <div className="p-4 rounded-xl bg-[#1E293B]">
                                        <p className="text-sm text-[#64748B] mb-1">Date</p>
                                        <p className="text-white font-semibold">{result.exploit_info.date}</p>
                                    </div>
                                    <div className="p-4 rounded-xl bg-[#1E293B]">
                                        <p className="text-sm text-[#64748B] mb-1">Loss</p>
                                        <p className="text-[#EF4444] font-semibold">
                                            {formatCurrency(result.exploit_info.loss_usd)}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        )}
                    </motion.div>
                )}

                {/* Empty State */}
                {!result && !error && !loading && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="glass-card p-16 text-center"
                    >
                        <Shield className="w-20 h-20 mx-auto mb-6 text-[#3B82F6] opacity-50" />
                        <h3 className="text-xl font-semibold text-white mb-2">Verify Any Address</h3>
                        <p className="text-[#64748B] max-w-md mx-auto">
                            Enter an Ethereum address to check if it&apos;s associated with known exploits or attackers
                        </p>
                    </motion.div>
                )}
            </div>
        </>
    );
}
