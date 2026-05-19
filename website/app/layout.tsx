import type { Metadata } from 'next'
import { Inter, Playfair_Display } from 'next/font/google'
import Script from 'next/script'
import { Analytics } from '@vercel/analytics/react'
import Header from '@/components/layout/Header'
import Footer from '@/components/layout/Footer'
import '@/styles/tokens.css'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const playfair = Playfair_Display({ subsets: ['latin'], variable: '--font-playfair', weight: ['400', '600', '700'] })

export const metadata: Metadata = {
  metadataBase: new URL('https://augustacountrylakes.mx'),
  title: { default: 'Augusta at Country Lakes — Mérida', template: '%s | Augusta' },
  description: 'La privada más exclusiva frente al campo de golf de Greg Letsche en Country Lakes, Mérida.',
  openGraph: { type: 'website', locale: 'es_MX', siteName: 'Augusta at Country Lakes' },
}

const orgSchema = JSON.stringify({
  '@context': 'https://schema.org',
  '@type': 'Organization',
  name: 'Augusta at Country Lakes',
  url: 'https://augustacountrylakes.mx',
  address: {
    '@type': 'PostalAddress',
    addressLocality: 'Mérida',
    addressRegion: 'Yucatán',
    addressCountry: 'MX',
  },
})

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es-MX" className={`${inter.variable} ${playfair.variable}`}>
      <head>
        <Script id="schema-org" type="application/ld+json" strategy="lazyOnload">
          {orgSchema}
        </Script>
      </head>
      <body className="bg-[#0A0E1A] text-[#FAF8F3] antialiased">
        <Header />
        <main>{children}</main>
        <Footer />
        <Analytics />
      </body>
    </html>
  )
}
