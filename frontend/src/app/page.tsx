"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import {
  Shield,
  Activity,
  Search,
  Database,
  Zap,
  Lock,
  ChevronRight,
  Github,
  ExternalLink
} from "lucide-react";

// =============================================================================
// Animation Variants
// =============================================================================

const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6 }
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
};

// =============================================================================
// Component: Animated Counter
// =============================================================================

function AnimatedCounter({ value, suffix = "" }: { value: number; suffix?: string }) {
  return (
    <motion.span
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="tabular-nums"
    >
      {value.toLocaleString()}{suffix}
    </motion.span>
  );
}

// =============================================================================
// Component: Feature Card
// =============================================================================

function FeatureCard({
  icon: Icon,
  title,
  description
}: {
  icon: React.ElementType;
  title: string;
  description: string;
}) {
  return (
    <motion.div
      variants={fadeInUp}
      className="glass-card glass-card-hover p-6 transition-all duration-300"
    >
      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#3B82F6] to-[#2563EB] flex items-center justify-center mb-4">
        <Icon className="w-6 h-6 text-white" />
      </div>
      <h3 className="text-xl font-bold text-white mb-2">{title}</h3>
      <p className="text-[#94A3B8] leading-relaxed">{description}</p>
    </motion.div>
  );
}

// =============================================================================
// Component: Stat Card
// =============================================================================

function StatCard({ value, label, suffix = "" }: { value: number; label: string; suffix?: string }) {
  return (
    <motion.div
      variants={fadeInUp}
      className="text-center"
    >
      <div className="text-4xl md:text-5xl font-bold text-white mb-2">
        <AnimatedCounter value={value} suffix={suffix} />
      </div>
      <div className="text-[#64748B] text-sm uppercase tracking-wider">{label}</div>
    </motion.div>
  );
}

// =============================================================================
// Main Landing Page
// =============================================================================

export default function LandingPage() {
  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated Grid Background */}
      <div className="grid-background" />

      {/* Gradient Orbs */}
      <div className="fixed top-[-20%] right-[-10%] w-[600px] h-[600px] rounded-full bg-[#3B82F6] opacity-[0.03] blur-[120px] pointer-events-none" />
      <div className="fixed bottom-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full bg-[#10B981] opacity-[0.03] blur-[120px] pointer-events-none" />

      {/* Navigation */}
      <nav className="relative z-10 py-3 px-4 lg:px-8">
        <div className="max-w-[1900px] mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#3B82F6] to-[#10B981] flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white">AltFlex</span>
          </Link>

          <div className="hidden md:flex items-center gap-8">
            <Link href="#features" className="text-[#94A3B8] hover:text-white transition-colors">
              Features
            </Link>
            <Link href="#stats" className="text-[#94A3B8] hover:text-white transition-colors">
              Statistics
            </Link>
            <a
              href="https://github.com/flexycode/CCSFEN2L_ALTFLEX"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[#94A3B8] hover:text-white transition-colors flex items-center gap-2"
            >
              <Github className="w-4 h-4" />
              GitHub
            </a>
          </div>

          <Link
            href="/dashboard"
            className="btn-primary flex items-center gap-2"
          >
            Launch Dashboard
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 pt-12 pb-16 px-4 lg:px-8">
        <div className="max-w-[1900px] mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#1E293B] border border-[#334155] mb-8">
              <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse" />
              <span className="text-sm text-[#94A3B8]">Powered by AI & Machine Learning</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
              AI-Powered{" "}
              <span className="bg-gradient-to-r from-[#3B82F6] via-[#8B5CF6] to-[#10B981] bg-clip-text text-transparent animate-gradient">
                Forensic Framework
              </span>
              <br />
              for Web3 Security
            </h1>

            {/* Subtitle */}
            <p className="text-xl text-[#94A3B8] max-w-3xl mx-auto mb-12 leading-relaxed">
              Detect and analyze security exploits in cross-chain bridges and DeFi protocols
              with advanced machine learning anomaly detection and blockchain forensic analysis.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/dashboard"
                className="btn-primary text-lg px-8 py-4 flex items-center gap-2"
              >
                <Activity className="w-5 h-5" />
                Start Analyzing
              </Link>
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-secondary text-lg px-8 py-4 flex items-center gap-2"
              >
                <ExternalLink className="w-5 h-5" />
                API Documentation
              </a>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
      <section id="stats" className="relative z-10 py-12 px-4 lg:px-8">
        <div className="max-w-[1900px] mx-auto">
          <motion.div
            variants={staggerContainer}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="glass-card p-8 lg:p-10"
          >
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              <StatCard value={406} label="Tracked Losses" suffix="M+" />
              <StatCard value={5} label="Known Exploits" />
              <StatCard value={159} label="Unit Tests" />
              <StatCard value={12} label="API Endpoints" />
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative z-10 py-12 px-4 lg:px-8">
        <div className="max-w-[1900px] mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-10"
          >
            <h2 className="text-4xl font-bold text-white mb-4">
              Enterprise-Grade Security Features
            </h2>
            <p className="text-[#94A3B8] text-lg max-w-2xl mx-auto">
              Comprehensive tools for detecting, analyzing, and preventing DeFi exploits
            </p>
          </motion.div>

          <motion.div
            variants={staggerContainer}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="grid md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            <FeatureCard
              icon={Search}
              title="Transaction Analysis"
              description="Deep analysis of transactions with rule-based detection and ML-powered anomaly scoring"
            />
            <FeatureCard
              icon={Shield}
              title="Address Verification"
              description="5-layer verification including format, checksum, on-chain, and behavioral analysis"
            />
            <FeatureCard
              icon={Database}
              title="Exploit Database"
              description="Comprehensive database of known exploits with attacker addresses and attack patterns"
            />
            <FeatureCard
              icon={Zap}
              title="Real-time Detection"
              description="Instant risk assessment with sub-second response times for live monitoring"
            />
            <FeatureCard
              icon={Activity}
              title="Behavioral Analysis"
              description="Velocity scoring, funding patterns, and sybil detection for suspicious behavior"
            />
            <FeatureCard
              icon={Lock}
              title="API Security"
              description="Rate limiting, API key authentication, and comprehensive audit logging"
            />
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 py-16 px-4 lg:px-8">
        <div className="max-w-[1400px] mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="glass-card p-8 lg:p-10"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Ready to Secure Your Protocol?
            </h2>
            <p className="text-[#94A3B8] text-lg mb-8">
              Start detecting vulnerabilities and protecting your DeFi assets today
            </p>
            <Link
              href="/dashboard"
              className="btn-primary text-lg px-10 py-4 inline-flex items-center gap-2"
            >
              Launch Dashboard
              <ChevronRight className="w-5 h-5" />
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 py-6 px-4 lg:px-8 border-t border-[#1E293B]">
        <div className="max-w-[1900px] mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#3B82F6] to-[#10B981] flex items-center justify-center">
              <Shield className="w-4 h-4 text-white" />
            </div>
            <span className="text-[#94A3B8]">
              AltFlex © 2026 — AI-Powered Security Framework
            </span>
          </div>
          <div className="flex items-center gap-6">
            <a
              href="https://github.com/flexycode/CCSFEN2L_ALTFLEX"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[#64748B] hover:text-white transition-colors"
            >
              <Github className="w-5 h-5" />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
