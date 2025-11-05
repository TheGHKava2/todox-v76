/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`,
      },
      {
        source: '/ws/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/ws/:path*`,
      },
      {
        source: '/docs',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/docs`,
      },
    ];
  },
};

module.exports = nextConfig;
