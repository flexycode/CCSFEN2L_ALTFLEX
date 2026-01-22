import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker
  output: 'standalone',

  // Disable telemetry in Docker
  experimental: {
    // Reduce memory usage in containers
  },
};

export default nextConfig;
