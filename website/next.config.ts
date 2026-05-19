import type { NextConfig } from 'next'

const config: NextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: '**.odoo.com' },
      { protocol: 'https', hostname: 'storage.googleapis.com' },
    ],
  },
  // typedRoutes: true,  // re-enable after all pages are created (Tasks 5-6)
}

export default config
