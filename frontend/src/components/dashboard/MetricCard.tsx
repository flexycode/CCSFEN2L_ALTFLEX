"use client";

import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
    title: string;
    value: string | number;
    subtitle?: string;
    icon: LucideIcon;
    trend?: {
        value: number;
        isPositive: boolean;
    };
    color?: "blue" | "green" | "amber" | "red";
}

const colorStyles = {
    blue: {
        bg: "from-[#3B82F6]/20 to-transparent",
        icon: "bg-[#3B82F6]/20 text-[#3B82F6]",
        glow: "shadow-[0_0_30px_rgba(59,130,246,0.15)]",
    },
    green: {
        bg: "from-[#10B981]/20 to-transparent",
        icon: "bg-[#10B981]/20 text-[#10B981]",
        glow: "shadow-[0_0_30px_rgba(16,185,129,0.15)]",
    },
    amber: {
        bg: "from-[#F59E0B]/20 to-transparent",
        icon: "bg-[#F59E0B]/20 text-[#F59E0B]",
        glow: "shadow-[0_0_30px_rgba(245,158,11,0.15)]",
    },
    red: {
        bg: "from-[#EF4444]/20 to-transparent",
        icon: "bg-[#EF4444]/20 text-[#EF4444]",
        glow: "shadow-[0_0_30px_rgba(239,68,68,0.15)]",
    },
};

export function MetricCard({
    title,
    value,
    subtitle,
    icon: Icon,
    trend,
    color = "blue",
}: MetricCardProps) {
    const styles = colorStyles[color];

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={cn(
                "glass-card p-8 hover:border-[#3B82F6]/30 transition-all duration-300",
                styles.glow
            )}
        >
            <div className="flex items-start justify-between mb-6">
                <div className={cn("w-16 h-16 rounded-2xl flex items-center justify-center", styles.icon)}>
                    <Icon className="w-8 h-8" />
                </div>
                {trend && (
                    <div
                        className={cn(
                            "flex items-center gap-1 text-lg font-semibold",
                            trend.isPositive ? "text-[#10B981]" : "text-[#EF4444]"
                        )}
                    >
                        <span>{trend.isPositive ? "+" : ""}{trend.value}%</span>
                    </div>
                )}
            </div>

            <div className="space-y-2">
                <p className="text-base text-[#64748B] font-medium">{title}</p>
                <p className="text-4xl font-bold text-white">{value}</p>
                {subtitle && (
                    <p className="text-base text-[#94A3B8]">{subtitle}</p>
                )}
            </div>
        </motion.div>
    );
}
