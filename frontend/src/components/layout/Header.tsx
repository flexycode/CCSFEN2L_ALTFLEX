"use client";

import { Bell, Search, User } from "lucide-react";

interface HeaderProps {
    title: string;
    subtitle?: string;
}

export function Header({ title, subtitle }: HeaderProps) {
    return (
        <header className="h-16 border-b border-[#1E293B] bg-[#0A0F1C]/80 backdrop-blur-xl flex items-center justify-between px-8 sticky top-0 z-40">
            {/* Title */}
            <div>
                <h1 className="text-xl font-bold text-white">{title}</h1>
                {subtitle && (
                    <p className="text-sm text-[#64748B]">{subtitle}</p>
                )}
            </div>

            {/* Actions */}
            <div className="flex items-center gap-4">
                {/* Search */}
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#64748B]" />
                    <input
                        type="text"
                        placeholder="Search..."
                        className="w-64 h-10 pl-10 pr-4 bg-[#1E293B] border border-[#334155] rounded-xl text-sm text-white placeholder-[#64748B] focus:outline-none focus:border-[#3B82F6] transition-colors"
                    />
                </div>

                {/* Notifications */}
                <button className="relative w-10 h-10 rounded-xl bg-[#1E293B] border border-[#334155] flex items-center justify-center hover:border-[#3B82F6] transition-colors">
                    <Bell className="w-4 h-4 text-[#94A3B8]" />
                    <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-[#EF4444]" />
                </button>

                {/* User Avatar */}
                <button className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#3B82F6] to-[#10B981] flex items-center justify-center">
                    <User className="w-5 h-5 text-white" />
                </button>
            </div>
        </header>
    );
}
