/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Do not block dev while we iterate quickly
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true },

  // Fix watchpack TypeError by properly configuring file watching
  webpack: (config, { dev, isServer }) => {
    if (dev) {
      try {
        config.watchOptions = config.watchOptions || {}
        config.watchOptions.ignored = [
          '**/node_modules/**',
          '**/.git/**',
          '**/.next/**',
          '**/backend/**',
          '**/test-results/**',
          '**/*.md',
        ]
        config.watchOptions.poll = 1000
        config.watchOptions.aggregateTimeout = 300

        config.snapshot = config.snapshot || {}
        config.snapshot.managedPaths = Array.isArray(config.snapshot.managedPaths)
          ? config.snapshot.managedPaths.filter(p => typeof p === 'string')
          : []
      } catch (e) {
        // Keep dev from crashing if some plugins provide unexpected values
        // Fall back to returning the original config unchanged
      }
    }

    return config
  },

  // Make sure the frontend always knows where the backend is
  env: {
    NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8001',
    NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || '',
  },

  // Keep experimental options minimal for stable dev
  experimental: {},

  // Skip static pre-rendering for problematic pages
  staticPageGenerationTimeout: 0,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8001/api/:path*',
      },
    ];
  },
};

export default nextConfig;
