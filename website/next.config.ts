import type { NextConfig } from 'next'

const config: NextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: '**.odoo.com' },
      { protocol: 'https', hostname: 'storage.googleapis.com' },
    ],
  },
  typedRoutes: true,
}

export default config
