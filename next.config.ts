import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Nothing experimental/invalid here. For dev cross-origin warnings,
  // we rely on the new allowedOrigins setting when needed.
};

export default nextConfig;
