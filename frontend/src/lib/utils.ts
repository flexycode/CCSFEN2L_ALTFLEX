import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Utility function to merge Tailwind CSS classes
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format Ethereum address for display (truncated)
 */
export function formatAddress(address: string, chars = 6): string {
  if (!address) return "";
  return `${address.slice(0, chars + 2)}...${address.slice(-chars)}`;
}

/**
 * Format large numbers with commas
 */
export function formatNumber(num: number): string {
  return new Intl.NumberFormat("en-US").format(num);
}

/**
 * Format currency values
 */
export function formatCurrency(value: number): string {
  if (value >= 1_000_000_000) {
    return `$${(value / 1_000_000_000).toFixed(1)}B`;
  }
  if (value >= 1_000_000) {
    return `$${(value / 1_000_000).toFixed(1)}M`;
  }
  if (value >= 1_000) {
    return `$${(value / 1_000).toFixed(1)}K`;
  }
  return `$${value.toFixed(2)}`;
}

/**
 * Get risk level color class
 */
export function getRiskColor(level: string): string {
  switch (level.toLowerCase()) {
    case "critical":
      return "text-critical-red";
    case "high":
      return "text-warning-amber";
    case "medium":
      return "text-yellow-400";
    case "low":
      return "text-cyber-green";
    case "safe":
    case "minimal":
      return "text-cyber-green";
    default:
      return "text-text-secondary";
  }
}

/**
 * Get risk badge class
 */
export function getRiskBadge(level: string): string {
  switch (level.toLowerCase()) {
    case "critical":
      return "badge-critical";
    case "high":
    case "warning":
      return "badge-warning";
    case "low":
    case "safe":
    case "minimal":
      return "badge-safe";
    default:
      return "badge-safe";
  }
}
