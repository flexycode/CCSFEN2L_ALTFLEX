"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
    Shield,
    LayoutDashboard,
    Search,
    CheckCircle,
    Database,
    Settings,
    Activity,
    ChevronLeft,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface NavItem {
    title: string;
    href: string;
    icon: React.ElementType;
}

const navItems: NavItem[] = [
    { title: "Overview", href: "/dashboard", icon: LayoutDashboard },
    { title: "Analyze", href: "/dashboard/analyze", icon: Search },
    { title: "Verify Address", href: "/dashboard/verify", icon: CheckCircle },
    { title: "Exploits", href: "/dashboard/exploits", icon: Database },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="fixed left-0 top-0 bottom-0 w-[288px] bg-[#0F172A] border-r border-[#1E293B] flex flex-col z-50">
            {/* Logo */}
            <div className="p-8 border-b border-[#1E293B]">
                <Link href="/" className="flex items-center gap-4 group">
                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-[#3B82F6] to-[#10B981] flex items-center justify-center">
                        <Shield className="w-7 h-7 text-white" />
                    </div>
                    <div>
                        <span className="text-2xl font-bold text-white">AltFlex</span>
                        <p className="text-sm text-[#64748B]">Security Platform</p>
                    </div>
                </Link>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-6 space-y-2">
                <p className="text-sm font-semibold text-[#64748B] uppercase tracking-wider px-4 mb-6">
                    Main Menu
                </p>
                {navItems.map((item) => {
                    const isActive = pathname === item.href ||
                        (item.href !== "/dashboard" && pathname.startsWith(item.href));

                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex items-center gap-4 px-4 py-4 rounded-xl text-lg font-medium transition-all duration-200",
                                isActive
                                    ? "bg-gradient-to-r from-[#3B82F6]/20 to-transparent text-white border-l-4 border-[#3B82F6]"
                                    : "text-[#94A3B8] hover:text-white hover:bg-[#1E293B]"
                            )}
                        >
                            <item.icon className={cn(
                                "w-6 h-6",
                                isActive ? "text-[#3B82F6]" : ""
                            )} />
                            {item.title}
                            {isActive && (
                                <motion.div
                                    layoutId="activeNav"
                                    className="ml-auto w-2 h-2 rounded-full bg-[#3B82F6]"
                                />
                            )}
                        </Link>
                    );
                })}
            </nav>

            {/* Status Indicator */}
            <div className="p-6 border-t border-[#1E293B]">
                <div className="glass-card p-5">
                    <div className="flex items-center gap-3 mb-3">
                        <Activity className="w-5 h-5 text-[#10B981]" />
                        <span className="text-base font-medium text-white">API Status</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="w-2.5 h-2.5 rounded-full bg-[#10B981] animate-pulse" />
                        <span className="text-sm text-[#94A3B8]">Connected</span>
                    </div>
                </div>
            </div>

            {/* Back to Home */}
            <div className="p-4">
                <Link
                    href="/"
                    className="flex items-center gap-2 px-3 py-2 text-sm text-[#64748B] hover:text-white transition-colors"
                >
                    <ChevronLeft className="w-4 h-4" />
                    Back to Home
                </Link>
            </div>
        </aside>
    );
}
