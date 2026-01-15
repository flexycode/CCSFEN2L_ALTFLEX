"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import {
    Shield,
    Search,
    CheckCircle,
    Database,
    Activity,
    TrendingUp,
    AlertTriangle,
    Clock,
    ArrowRight,
} from "lucide-react";
import { Header } from "@/components/layout/Header";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { HealthStatus } from "@/components/dashboard/HealthStatus";
import { getExploits } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

export default function DashboardPage() {
    const [exploitCount, setExploitCount] = useState(0);
    const [totalLoss, setTotalLoss] = useState(0);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const data = await getExploits();
                setExploitCount(data.total);
                const loss = data.exploits.reduce((sum, e) => sum + e.loss_usd, 0);
                setTotalLoss(loss);
            } catch (err) {
                console.error("Failed to fetch exploits:", err);
            }
        };
        fetchStats();
    }, []);

    const quickActions = [
        {
            title: "Analyze Transaction",
            description: "Deep analysis with ML detection",
            icon: Search,
            href: "/dashboard/analyze",
            color: "blue" as const,
        },
        {
            title: "Verify Address",
            description: "5-layer security verification",
            icon: CheckCircle,
            href: "/dashboard/verify",
            color: "green" as const,
        },
        {
            title: "View Exploits",
            description: "Browse known attacks",
            icon: Database,
            href: "/dashboard/exploits",
            color: "amber" as const,
        },
    ];

    return (
        <>
            <Header title="Dashboard" subtitle="Monitor and analyze blockchain security" />

            <div className="p-8">
                {/* Welcome Section */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-8"
                >
                    <h2 className="text-2xl font-bold text-white mb-2">
                        Welcome to AltFlex Security Platform
                    </h2>
                    <p className="text-[#94A3B8]">
                        AI-powered forensic analysis for Web3 protocols and DeFi security
                    </p>
                </motion.div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <MetricCard
                        title="Known Exploits"
                        value={exploitCount}
                        subtitle="In database"
                        icon={AlertTriangle}
                        color="red"
                    />
                    <MetricCard
                        title="Total Tracked Loss"
                        value={formatCurrency(totalLoss)}
                        subtitle="From all exploits"
                        icon={TrendingUp}
                        color="amber"
                    />
                    <MetricCard
                        title="Detection Rules"
                        value={6}
                        subtitle="Active rules"
                        icon={Shield}
                        color="blue"
                    />
                    <MetricCard
                        title="Unit Tests"
                        value={159}
                        subtitle="All passing"
                        icon={Activity}
                        color="green"
                        trend={{ value: 100, isPositive: true }}
                    />
                </div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Quick Actions */}
                    <div className="col-span-1 lg:col-span-2">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 }}
                        >
                            <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                                {quickActions.map((action, index) => (
                                    <Link
                                        key={action.href}
                                        href={action.href}
                                        className="glass-card glass-card-hover p-6 group"
                                    >
                                        <motion.div
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: 0.1 + index * 0.05 }}
                                        >
                                            <div
                                                className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${action.color === "blue"
                                                    ? "bg-[#3B82F6]/20 text-[#3B82F6]"
                                                    : action.color === "green"
                                                        ? "bg-[#10B981]/20 text-[#10B981]"
                                                        : "bg-[#F59E0B]/20 text-[#F59E0B]"
                                                    }`}
                                            >
                                                <action.icon className="w-6 h-6" />
                                            </div>
                                            <h4 className="text-white font-semibold mb-1 flex items-center gap-2">
                                                {action.title}
                                                <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                                            </h4>
                                            <p className="text-sm text-[#64748B]">{action.description}</p>
                                        </motion.div>
                                    </Link>
                                ))}
                            </div>
                        </motion.div>

                        {/* Recent Activity Placeholder */}
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                            className="mt-6"
                        >
                            <h3 className="text-lg font-semibold text-white mb-4">Recent Activity</h3>
                            <div className="glass-card p-6">
                                <div className="flex items-center justify-center py-8 text-[#64748B]">
                                    <div className="text-center">
                                        <Clock className="w-12 h-12 mx-auto mb-3 opacity-50" />
                                        <p>No recent activity</p>
                                        <p className="text-sm mt-1">Start by analyzing a transaction</p>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    </div>

                    {/* Sidebar */}
                    <div className="space-y-6">
                        {/* Health Status */}
                        <HealthStatus />

                        {/* API Info */}
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.3 }}
                            className="glass-card p-6"
                        >
                            <h3 className="text-lg font-semibold text-white mb-4">API Information</h3>
                            <div className="space-y-3">
                                <div className="flex items-center justify-between">
                                    <span className="text-sm text-[#64748B]">Endpoints</span>
                                    <span className="text-sm text-white font-medium">12</span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-sm text-[#64748B]">Rate Limit</span>
                                    <span className="text-sm text-white font-medium">100/min</span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-sm text-[#64748B]">Backend</span>
                                    <span className="text-sm text-white font-medium">FastAPI</span>
                                </div>
                            </div>
                            <a
                                href="http://localhost:8000/docs"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="mt-4 w-full btn-secondary text-sm flex items-center justify-center gap-2"
                            >
                                View API Docs
                                <ArrowRight className="w-4 h-4" />
                            </a>
                        </motion.div>
                    </div>
                </div>
            </div>
        </>
    );
}
