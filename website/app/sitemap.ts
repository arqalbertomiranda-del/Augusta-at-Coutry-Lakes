import type { MetadataRoute } from 'next'

const BASE = 'https://augustacountrylakes.mx'

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: BASE,                  lastModified: new Date(), changeFrequency: 'daily',   priority: 1 },
    { url: `${BASE}/lotes`,       lastModified: new Date(), changeFrequency: 'hourly',  priority: 0.9 },
    { url: `${BASE}/contacto`,    lastModified: new Date(), changeFrequency: 'monthly', priority: 0.7 },
  ]
}
