"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { CheckCircle, XCircle, AlertCircle, RefreshCw } from "lucide-react";
import { getHealth } from "@/lib/api";
import type { HealthResponse } from "@/lib/types";
import { cn } from "@/lib/utils";

interface ComponentStatus {
    name: string;
    status: boolean | null;
    label: string;
}

export function HealthStatus() {
    const [health, setHealth] = useState<HealthResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchHealth = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await getHealth();
            setHealth(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to fetch health");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHealth();
        const interval = setInterval(fetchHealth, 30000); // Refresh every 30s
        return () => clearInterval(interval);
    }, []);

    const components: ComponentStatus[] = health
        ? [
            { name: "api", status: health.components.api, label: "API Server" },
            { name: "anomaly_detector", status: health.components.anomaly_detector, label: "ML Detector" },
            { name: "exploit_detector", status: health.components.exploit_detector, label: "Exploit Detector" },
            { name: "feature_engineer", status: health.components.feature_engineer, label: "Feature Engine" },
        ]
        : [];

    const allHealthy = components.every((c) => c.status);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card p-6"
        >
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <div
                        className={cn(
                            "w-10 h-10 rounded-xl flex items-center justify-center",
                            loading
                                ? "bg-[#64748B]/20"
                                : error
                                    ? "bg-[#EF4444]/20"
                                    : allHealthy
                                        ? "bg-[#10B981]/20"
                                        : "bg-[#F59E0B]/20"
                        )}
                    >
                        {loading ? (
                            <RefreshCw className="w-5 h-5 text-[#64748B] animate-spin" />
                        ) : error ? (
                            <XCircle className="w-5 h-5 text-[#EF4444]" />
                        ) : allHealthy ? (
                            <CheckCircle className="w-5 h-5 text-[#10B981]" />
                        ) : (
                            <AlertCircle className="w-5 h-5 text-[#F59E0B]" />
                        )}
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold text-white">System Health</h3>
                        <p className="text-sm text-[#64748B]">
                            {loading
                                ? "Checking..."
                                : error
                                    ? "Connection Error"
                                    : allHealthy
                                        ? "All Systems Operational"
                                        : "Some Issues Detected"}
                        </p>
                    </div>
                </div>

                <button
                    onClick={fetchHealth}
                    className="p-2 rounded-lg hover:bg-[#1E293B] transition-colors"
                    disabled={loading}
                >
                    <RefreshCw
                        className={cn(
                            "w-4 h-4 text-[#64748B]",
                            loading && "animate-spin"
                        )}
                    />
                </button>
            </div>

            {/* Components Grid */}
            {error ? (
                <div className="p-4 rounded-xl bg-[#EF4444]/10 border border-[#EF4444]/20">
                    <p className="text-sm text-[#EF4444]">{error}</p>
                    <p className="text-xs text-[#64748B] mt-1">
                        Make sure the API server is running on localhost:8000
                    </p>
                </div>
            ) : (
                <div className="grid grid-cols-2 gap-3">
                    {components.map((component) => (
                        <div
                            key={component.name}
                            className={cn(
                                "p-3 rounded-xl border flex items-center gap-2",
                                component.status === null
                                    ? "bg-[#1E293B] border-[#334155]"
                                    : component.status
                                        ? "bg-[#10B981]/5 border-[#10B981]/20"
                                        : "bg-[#EF4444]/5 border-[#EF4444]/20"
                            )}
                        >
                            <span
                                className={cn(
                                    "w-2 h-2 rounded-full",
                                    component.status === null
                                        ? "bg-[#64748B]"
                                        : component.status
                                            ? "bg-[#10B981]"
                                            : "bg-[#EF4444]"
                                )}
                            />
                            <span className="text-sm text-[#94A3B8]">{component.label}</span>
                        </div>
                    ))}
                </div>
            )}

            {/* Version */}
            {health && (
                <div className="mt-4 pt-4 border-t border-[#1E293B] flex items-center justify-between text-xs text-[#64748B]">
                    <span>Version: {health.version}</span>
                    <span>Last check: {new Date(health.timestamp).toLocaleTimeString()}</span>
                </div>
            )}
        </motion.div>
    );
}
