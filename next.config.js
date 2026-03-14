/** @type {import('next').NextConfig} */

const nextConfig = {
  // Use standalone output for production Docker builds, but not for development
  // In development, this causes module resolution issues with CSS imports
  output: process.env.NODE_ENV === 'production' ? 'standalone' : undefined,

  // Image optimization
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.skillforge.com',
      },
      {
        protocol: 'https',
        hostname: 'res.cloudinary.com',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
      },
      {
        protocol: 'http',
        hostname: '127.0.0.1',
      },
    ],
    formats: ['image/avif', 'image/webp'],
  },

  // Enable React strict mode for development
  reactStrictMode: true,

  // Disable telemetry
  typescript: {
    tsconfigPath: './tsconfig.json',
  },

  // Proper headers for security and performance
  headers: async () => {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
