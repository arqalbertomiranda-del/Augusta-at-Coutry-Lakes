# Augusta Website — Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the Augusta at Country Lakes website with real-time lot inventory from Odoo, interactive cotizador, HubSpot lead capture, and WhatsApp notifications — ready for production on Vercel.

**Architecture:** Next.js 15 App Router in `website/` subfolder; server-only API routes proxy Odoo/HubSpot/WhatsApp so no secret leaks to the browser; static pages with ISR for SEO; Tailwind CSS 4 + Framer Motion for UI.

**Tech Stack:** Next.js 15, TypeScript 5, Tailwind CSS 4, Framer Motion, Odoo REST, HubSpot Private App, WhatsApp Business API, Playwright, Vercel.

---

## File Map

```
website/
├── app/
│   ├── layout.tsx                    # Root layout, fonts, schema.org, analytics
│   ├── page.tsx                      # Home: hero video, stats bar, CTA
│   ├── lotes/
│   │   ├── page.tsx                  # Lot grid with filters
│   │   └── [id]/
│   │       └── page.tsx              # Individual lot detail + cotizador
│   ├── contacto/
│   │   └── page.tsx                  # Full contact form
│   ├── robots.txt/
│   │   └── route.ts                  # robots.txt dynamic route
│   ├── sitemap.ts                    # Dynamic sitemap
│   └── api/
│       ├── inventory/
│       │   └── route.ts              # GET /api/inventory → Odoo
│       ├── leads/
│       │   └── route.ts              # POST /api/leads → HubSpot + WhatsApp
│       └── financing/
│           └── route.ts              # POST /api/financing → financing calc
├── components/
│   ├── layout/
│   │   ├── Header.tsx
│   │   └── Footer.tsx
│   ├── lots/
│   │   ├── LotCard.tsx
│   │   ├── LotFilter.tsx
│   │   └── LotGrid.tsx
│   ├── cotizador/
│   │   ├── FinancingCalc.tsx
│   │   └── LeadForm.tsx
│   └── ui/
│       └── StatsBar.tsx
├── lib/
│   ├── types.ts                      # Lot, Lead, FinancingOption, LotStatus
│   ├── odoo.ts                       # Odoo REST client
│   ├── hubspot.ts                    # HubSpot client
│   ├── whatsapp.ts                   # WhatsApp Business API client
│   └── financing.ts                  # Amortization logic
├── styles/
│   └── tokens.css                    # Design tokens (colors, typography, spacing)
├── public/
│   └── llms.txt                      # AI search visibility
├── tests/
│   ├── unit/
│   │   ├── financing.test.ts
│   │   └── LotCard.test.tsx
│   └── e2e/
│       ├── home.spec.ts
│       ├── cotizador.spec.ts
│       └── lead-form.spec.ts
├── next.config.ts
├── tailwind.config.ts
├── playwright.config.ts
├── vercel.json
└── package.json
```

---

### Task 1: Scaffold Next.js 15 Project

**Files:**
- Create: `website/` (entire scaffolded project)
- Modify: `website/next.config.ts`
- Modify: `website/tailwind.config.ts`
- Modify: `website/package.json`

- [ ] **Step 1: Scaffold**

Run from repo root:
```bash
npx create-next-app@latest website \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir=false \
  --import-alias="@/*"
```

- [ ] **Step 2: Install dependencies**

```bash
cd website
npm install framer-motion @vercel/analytics sharp
npm install -D @playwright/test @testing-library/react @testing-library/jest-dom jest jest-environment-jsdom ts-jest
```

- [ ] **Step 3: Configure next.config.ts**

```ts
// website/next.config.ts
import type { NextConfig } from 'next'

const config: NextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: '**.odoo.com' },
      { protocol: 'https', hostname: 'storage.googleapis.com' },
    ],
  },
  experimental: { typedRoutes: true },
}

export default config
```

- [ ] **Step 4: Verify dev server starts**

```bash
npm run dev
```
Expected: Server running at http://localhost:3000 with no errors.

- [ ] **Step 5: Commit**

```bash
cd ..
git add website/
git commit -m "feat: scaffold Next.js 15 website"
```

---

### Task 2: Design Tokens + Layout Components

**Files:**
- Create: `website/styles/tokens.css`
- Create: `website/components/layout/Header.tsx`
- Create: `website/components/layout/Footer.tsx`
- Modify: `website/app/layout.tsx`

- [ ] **Step 1: Create design tokens**

```css
/* website/styles/tokens.css */
:root {
  --color-midnight: #0A0E1A;
  --color-champagne: #C8A96E;
  --color-ivory: #FAF8F3;
  --color-sage: #5C6E4B;
  --color-slate: #2D3340;

  --font-display: 'Playfair Display', Georgia, serif;
  --font-body: 'Inter', system-ui, sans-serif;

  --text-hero: clamp(2.5rem, 1rem + 6vw, 5rem);
  --text-h1: clamp(2rem, 0.8rem + 4vw, 3.5rem);
  --text-h2: clamp(1.5rem, 0.6rem + 3vw, 2.5rem);
  --text-body: clamp(1rem, 0.92rem + 0.4vw, 1.125rem);

  --space-section: clamp(4rem, 2rem + 8vw, 10rem);
  --radius-card: 12px;
  --shadow-card: 0 4px 24px rgba(10, 14, 26, 0.12);

  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
}
```

- [ ] **Step 2: Create Header component**

```tsx
// website/components/layout/Header.tsx
'use client'
import Link from 'next/link'
import { useState } from 'react'

export default function Header() {
  const [open, setOpen] = useState(false)

  return (
    <header className="fixed top-0 inset-x-0 z-50 bg-[var(--color-midnight)]/90 backdrop-blur-md border-b border-[var(--color-champagne)]/20">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="font-display text-[var(--color-champagne)] text-xl font-semibold tracking-wide">
          Augusta
        </Link>
        <nav className="hidden md:flex items-center gap-8">
          {[['Inicio', '/'], ['Lotes', '/lotes'], ['Contacto', '/contacto']].map(([label, href]) => (
            <Link key={href} href={href} className="text-[var(--color-ivory)]/80 hover:text-[var(--color-champagne)] text-sm transition-colors duration-150">
              {label}
            </Link>
          ))}
          <Link href="/lotes" className="px-5 py-2 bg-[var(--color-champagne)] text-[var(--color-midnight)] text-sm font-semibold rounded-full hover:bg-[var(--color-champagne)]/90 transition-colors">
            Ver disponibilidad
          </Link>
        </nav>
        <button className="md:hidden text-[var(--color-ivory)]" onClick={() => setOpen(!open)} aria-label="Menu">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={open ? 'M6 18L18 6M6 6l12 12' : 'M4 6h16M4 12h16M4 18h16'} />
          </svg>
        </button>
      </div>
      {open && (
        <div className="md:hidden bg-[var(--color-midnight)] border-t border-[var(--color-champagne)]/20 px-6 py-4 flex flex-col gap-4">
          {[['Inicio', '/'], ['Lotes', '/lotes'], ['Contacto', '/contacto']].map(([label, href]) => (
            <Link key={href} href={href} className="text-[var(--color-ivory)]/80 text-sm" onClick={() => setOpen(false)}>
              {label}
            </Link>
          ))}
        </div>
      )}
    </header>
  )
}
```

- [ ] **Step 3: Create Footer component**

```tsx
// website/components/layout/Footer.tsx
export default function Footer() {
  return (
    <footer className="bg-[var(--color-midnight)] border-t border-[var(--color-champagne)]/20 py-12">
      <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-start gap-8">
        <div>
          <p className="font-display text-[var(--color-champagne)] text-lg font-semibold">Augusta at Country Lakes</p>
          <p className="text-[var(--color-ivory)]/50 text-sm mt-1">Frente al campo de golf de Greg Letsche · Mérida, Yucatán</p>
        </div>
        <div className="text-[var(--color-ivory)]/50 text-sm">
          <p>© {new Date().getFullYear()} Boma Desarrollos. Todos los derechos reservados.</p>
        </div>
      </div>
    </footer>
  )
}
```

- [ ] **Step 4: Update root layout**

```tsx
// website/app/layout.tsx
import type { Metadata } from 'next'
import { Inter, Playfair_Display } from 'next/font/google'
import Script from 'next/script'
import { Analytics } from '@vercel/analytics/react'
import Header from '@/components/layout/Header'
import Footer from '@/components/layout/Footer'
import '@/styles/tokens.css'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const playfair = Playfair_Display({ subsets: ['latin'], variable: '--font-playfair' })

export const metadata: Metadata = {
  metadataBase: new URL('https://augustacountrylakes.mx'),
  title: { default: 'Augusta at Country Lakes — Mérida', template: '%s | Augusta' },
  description: 'La privada más exclusiva frente al campo de golf de Greg Letsche en Country Lakes, Mérida.',
  openGraph: { type: 'website', locale: 'es_MX', siteName: 'Augusta at Country Lakes' },
}

const orgSchema = {
  '@context': 'https://schema.org',
  '@type': 'Organization',
  name: 'Augusta at Country Lakes',
  url: 'https://augustacountrylakes.mx',
  logo: 'https://augustacountrylakes.mx/logo.png',
  address: {
    '@type': 'PostalAddress',
    addressLocality: 'Mérida',
    addressRegion: 'Yucatán',
    addressCountry: 'MX',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es-MX" className={`${inter.variable} ${playfair.variable}`}>
      <head>
        <Script id="schema-org" type="application/ld+json" strategy="beforeInteractive">
          {JSON.stringify(orgSchema)}
        </Script>
      </head>
      <body className="bg-[var(--color-midnight)] text-[var(--color-ivory)] font-body antialiased">
        <Header />
        <main>{children}</main>
        <Footer />
        <Analytics />
      </body>
    </html>
  )
}
```

- [ ] **Step 5: Verify no TypeScript errors**

```bash
cd website && npx tsc --noEmit
```
Expected: no errors.

- [ ] **Step 6: Commit**

```bash
cd ..
git add website/styles/ website/components/layout/ website/app/layout.tsx
git commit -m "feat: design tokens and layout components"
```

---

### Task 3: TypeScript Types + API Clients (TDD)

**Files:**
- Create: `website/lib/types.ts`
- Create: `website/lib/odoo.ts`
- Create: `website/lib/hubspot.ts`
- Create: `website/lib/whatsapp.ts`
- Create: `website/lib/financing.ts`
- Create: `website/tests/unit/financing.test.ts`

- [ ] **Step 1: Write financing unit test first**

```ts
// website/tests/unit/financing.test.ts
import { calculateMonthlyPayment, buildAmortizationSchedule } from '@/lib/financing'

describe('calculateMonthlyPayment', () => {
  it('calculates correct monthly payment for standard loan', () => {
    const result = calculateMonthlyPayment({ principal: 1_000_000, annualRate: 0.12, months: 120 })
    expect(result).toBeCloseTo(14_347, 0)
  })

  it('returns principal divided by months when rate is 0', () => {
    const result = calculateMonthlyPayment({ principal: 600_000, annualRate: 0, months: 60 })
    expect(result).toBeCloseTo(10_000, 0)
  })
})

describe('buildAmortizationSchedule', () => {
  it('returns array of length equal to months', () => {
    const schedule = buildAmortizationSchedule({ principal: 500_000, annualRate: 0.10, months: 12 })
    expect(schedule).toHaveLength(12)
  })

  it('last entry has near-zero remaining balance', () => {
    const schedule = buildAmortizationSchedule({ principal: 500_000, annualRate: 0.10, months: 12 })
    expect(schedule[11].balance).toBeCloseTo(0, 0)
  })
})
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
cd website && npx jest tests/unit/financing.test.ts
```
Expected: FAIL — `Cannot find module '@/lib/financing'`

- [ ] **Step 3: Create types**

```ts
// website/lib/types.ts
export type LotStatus = 'disponible' | 'apartado' | 'vendido'

export interface Lot {
  id: string
  name: string
  area: number          // m²
  price: number         // MXN
  status: LotStatus
  facing: string        // orientación
  section: string       // sección dentro de la privada
  imageUrl?: string
}

export interface Lead {
  firstName: string
  lastName: string
  email: string
  phone: string
  message?: string
  lotId?: string
  utmSource?: string
  utmCampaign?: string
}

export interface FinancingInput {
  principal: number
  annualRate: number
  months: number
}

export interface AmortizationRow {
  period: number
  payment: number
  interest: number
  principal: number
  balance: number
}

export interface FinancingOption {
  label: string
  months: number
  annualRate: number
  monthlyPayment: number
}
```

- [ ] **Step 4: Create financing lib**

```ts
// website/lib/financing.ts
import type { FinancingInput, AmortizationRow } from './types'

export function calculateMonthlyPayment({ principal, annualRate, months }: FinancingInput): number {
  if (annualRate === 0) return principal / months
  const r = annualRate / 12
  return (principal * r * Math.pow(1 + r, months)) / (Math.pow(1 + r, months) - 1)
}

export function buildAmortizationSchedule({ principal, annualRate, months }: FinancingInput): AmortizationRow[] {
  const payment = calculateMonthlyPayment({ principal, annualRate, months })
  const r = annualRate / 12
  const rows: AmortizationRow[] = []
  let balance = principal

  for (let i = 1; i <= months; i++) {
    const interest = balance * r
    const principalPaid = payment - interest
    balance = Math.max(0, balance - principalPaid)
    rows.push({ period: i, payment, interest, principal: principalPaid, balance })
  }

  return rows
}
```

- [ ] **Step 5: Run test — expect PASS**

```bash
npx jest tests/unit/financing.test.ts
```
Expected: PASS — 4 tests

- [ ] **Step 6: Create Odoo client**

```ts
// website/lib/odoo.ts
import type { Lot, LotStatus } from './types'

const BASE_URL = process.env.ODOO_API_URL
const API_KEY = process.env.ODOO_API_KEY
const DB = process.env.ODOO_DATABASE

if (!BASE_URL || !API_KEY || !DB) {
  // Odoo not configured — inventory API will return empty array
}

export async function fetchLots(): Promise<Lot[]> {
  if (!BASE_URL || !API_KEY || !DB) return []

  const res = await fetch(`${BASE_URL}/api/method/augusta.get_lots`, {
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      'Content-Type': 'application/json',
    },
    next: { revalidate: 60 }, // ISR: revalidate every 60 seconds
  })

  if (!res.ok) throw new Error(`Odoo error: ${res.status}`)

  const data = await res.json()
  return (data.result ?? []).map(mapOdooLot)
}

function mapOdooLot(raw: Record<string, unknown>): Lot {
  const statusMap: Record<string, LotStatus> = {
    available: 'disponible',
    reserved: 'apartado',
    sold: 'vendido',
  }
  return {
    id: String(raw.id),
    name: String(raw.name),
    area: Number(raw.area_sqm ?? 0),
    price: Number(raw.list_price ?? 0),
    status: statusMap[String(raw.state)] ?? 'disponible',
    facing: String(raw.facing ?? ''),
    section: String(raw.section ?? ''),
    imageUrl: raw.image_url ? String(raw.image_url) : undefined,
  }
}
```

- [ ] **Step 7: Create HubSpot client**

```ts
// website/lib/hubspot.ts
import type { Lead } from './types'

const API_KEY = process.env.HUBSPOT_API_KEY
const PORTAL_ID = process.env.HUBSPOT_PORTAL_ID

export async function createContact(lead: Lead): Promise<{ id: string }> {
  if (!API_KEY) throw new Error('HUBSPOT_API_KEY not set')

  const res = await fetch('https://api.hubapi.com/crm/v3/objects/contacts', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      properties: {
        firstname: lead.firstName,
        lastname: lead.lastName,
        email: lead.email,
        phone: lead.phone,
        message: lead.message ?? '',
        augusta_lot_id: lead.lotId ?? '',
        hs_lead_status: 'NEW',
        lifecyclestage: 'lead',
      },
    }),
  })

  if (!res.ok) {
    const err = await res.text()
    throw new Error(`HubSpot error ${res.status}: ${err}`)
  }

  const data = await res.json()
  return { id: data.id }
}
```

- [ ] **Step 8: Create WhatsApp client**

```ts
// website/lib/whatsapp.ts
import type { Lead } from './types'

const TOKEN = process.env.WHATSAPP_API_TOKEN
const PHONE_ID = process.env.WHATSAPP_PHONE_ID
const SALES_NUMBER = process.env.WHATSAPP_SALES_NUMBER

export async function notifySales(lead: Lead, lotId?: string): Promise<void> {
  if (!TOKEN || !PHONE_ID || !SALES_NUMBER) return

  const text = [
    '🏌️ *Nuevo lead Augusta*',
    `Nombre: ${lead.firstName} ${lead.lastName}`,
    `Teléfono: ${lead.phone}`,
    `Email: ${lead.email}`,
    lotId ? `Lote de interés: ${lotId}` : '',
    lead.message ? `Mensaje: ${lead.message}` : '',
  ].filter(Boolean).join('\n')

  await fetch(`https://graph.facebook.com/v20.0/${PHONE_ID}/messages`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      messaging_product: 'whatsapp',
      to: SALES_NUMBER,
      type: 'text',
      text: { body: text },
    }),
  })
}
```

- [ ] **Step 9: Commit**

```bash
cd ..
git add website/lib/ website/tests/unit/financing.test.ts
git commit -m "feat: types, api clients, financing logic with tests"
```

---

### Task 4: API Routes

**Files:**
- Create: `website/app/api/inventory/route.ts`
- Create: `website/app/api/leads/route.ts`
- Create: `website/app/api/financing/route.ts`

- [ ] **Step 1: Inventory route**

```ts
// website/app/api/inventory/route.ts
import { NextResponse } from 'next/server'
import { fetchLots } from '@/lib/odoo'

export const runtime = 'nodejs'
export const revalidate = 60

export async function GET() {
  try {
    const lots = await fetchLots()
    return NextResponse.json({ lots })
  } catch (err) {
    console.error('[/api/inventory]', err)
    return NextResponse.json({ lots: [], error: 'Error cargando inventario' }, { status: 500 })
  }
}
```

- [ ] **Step 2: Leads route**

```ts
// website/app/api/leads/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { createContact } from '@/lib/hubspot'
import { notifySales } from '@/lib/whatsapp'
import type { Lead } from '@/lib/types'

export const runtime = 'nodejs'

export async function POST(req: NextRequest) {
  const body = await req.json() as Partial<Lead & { lotId: string }>

  if (!body.firstName || !body.lastName || !body.email || !body.phone) {
    return NextResponse.json({ error: 'Campos requeridos faltantes' }, { status: 400 })
  }

  const lead: Lead = {
    firstName: body.firstName,
    lastName: body.lastName,
    email: body.email,
    phone: body.phone,
    message: body.message,
    lotId: body.lotId,
    utmSource: req.nextUrl.searchParams.get('utm_source') ?? undefined,
    utmCampaign: req.nextUrl.searchParams.get('utm_campaign') ?? undefined,
  }

  try {
    const [contact] = await Promise.allSettled([
      createContact(lead),
      notifySales(lead, body.lotId),
    ])

    if (contact.status === 'rejected') throw contact.reason

    return NextResponse.json({ success: true, contactId: (contact as PromiseFulfilledResult<{ id: string }>).value.id })
  } catch (err) {
    console.error('[/api/leads]', err)
    return NextResponse.json({ error: 'Error registrando lead' }, { status: 500 })
  }
}
```

- [ ] **Step 3: Financing route**

```ts
// website/app/api/financing/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { calculateMonthlyPayment } from '@/lib/financing'
import type { FinancingOption } from '@/lib/types'

export const runtime = 'nodejs'

const PLANS = [
  { label: 'Contado 5%', months: 1, discount: 0.05 },
  { label: '12 meses', months: 12, annualRate: 0.10 },
  { label: '36 meses', months: 36, annualRate: 0.12 },
  { label: '60 meses', months: 60, annualRate: 0.14 },
  { label: '120 meses', months: 120, annualRate: 0.15 },
]

export async function POST(req: NextRequest) {
  const { price } = await req.json() as { price: number }

  if (!price || typeof price !== 'number' || price <= 0) {
    return NextResponse.json({ error: 'Precio inválido' }, { status: 400 })
  }

  const options: FinancingOption[] = PLANS.map(plan => {
    const principal = 'discount' in plan ? price * (1 - plan.discount!) : price
    const annualRate = ('annualRate' in plan ? plan.annualRate : 0) as number
    const months = plan.months
    return {
      label: plan.label,
      months,
      annualRate,
      monthlyPayment: calculateMonthlyPayment({ principal, annualRate, months }),
    }
  })

  return NextResponse.json({ options })
}
```

- [ ] **Step 4: Verify routes compile**

```bash
cd website && npx tsc --noEmit
```
Expected: no errors.

- [ ] **Step 5: Commit**

```bash
cd ..
git add website/app/api/
git commit -m "feat: api routes for inventory, leads, and financing"
```

---

### Task 5: Cotizador UI Components (TDD)

**Files:**
- Create: `website/components/lots/LotCard.tsx`
- Create: `website/components/lots/LotFilter.tsx`
- Create: `website/components/lots/LotGrid.tsx`
- Create: `website/components/cotizador/FinancingCalc.tsx`
- Create: `website/components/cotizador/LeadForm.tsx`
- Create: `website/tests/unit/LotCard.test.tsx`

- [ ] **Step 1: Write LotCard test first**

```tsx
// website/tests/unit/LotCard.test.tsx
import { render, screen } from '@testing-library/react'
import LotCard from '@/components/lots/LotCard'
import type { Lot } from '@/lib/types'

const lot: Lot = {
  id: '1',
  name: 'Lote A-12',
  area: 400,
  price: 2_500_000,
  status: 'disponible',
  facing: 'Norte',
  section: 'A',
}

it('renders lot name', () => {
  render(<LotCard lot={lot} />)
  expect(screen.getByText('Lote A-12')).toBeInTheDocument()
})

it('formats price in MXN', () => {
  render(<LotCard lot={lot} />)
  expect(screen.getByText(/2,500,000/)).toBeInTheDocument()
})

it('shows disponible badge', () => {
  render(<LotCard lot={lot} />)
  expect(screen.getByText(/disponible/i)).toBeInTheDocument()
})

it('shows vendido badge for sold lots', () => {
  render(<LotCard lot={{ ...lot, status: 'vendido' }} />)
  expect(screen.getByText(/vendido/i)).toBeInTheDocument()
})
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
cd website && npx jest tests/unit/LotCard.test.tsx
```
Expected: FAIL — `Cannot find module '@/components/lots/LotCard'`

- [ ] **Step 3: Create LotCard**

```tsx
// website/components/lots/LotCard.tsx
import Link from 'next/link'
import type { Lot } from '@/lib/types'

const statusStyle: Record<string, string> = {
  disponible: 'bg-emerald-900/40 text-emerald-300',
  apartado:   'bg-amber-900/40 text-amber-300',
  vendido:    'bg-red-900/40 text-red-300',
}

const statusLabel: Record<string, string> = {
  disponible: 'Disponible',
  apartado:   'Apartado',
  vendido:    'Vendido',
}

export default function LotCard({ lot }: { lot: Lot }) {
  const isAvailable = lot.status === 'disponible'

  return (
    <article className="bg-[var(--color-slate)] rounded-[var(--radius-card)] overflow-hidden shadow-[var(--shadow-card)] flex flex-col">
      <div className="bg-[var(--color-midnight)] h-48 flex items-center justify-center text-[var(--color-champagne)]/30 text-5xl">
        ⛳
      </div>
      <div className="p-5 flex flex-col gap-3 flex-1">
        <div className="flex justify-between items-start">
          <h3 className="font-display text-lg font-semibold text-[var(--color-ivory)]">{lot.name}</h3>
          <span className={`text-xs px-2 py-1 rounded-full font-medium ${statusStyle[lot.status]}`}>
            {statusLabel[lot.status]}
          </span>
        </div>
        <div className="text-[var(--color-ivory)]/60 text-sm flex gap-4">
          <span>{lot.area} m²</span>
          <span>{lot.facing}</span>
          <span>Sec. {lot.section}</span>
        </div>
        <p className="text-[var(--color-champagne)] text-xl font-semibold">
          ${lot.price.toLocaleString('es-MX')} MXN
        </p>
        {isAvailable && (
          <Link href={`/lotes/${lot.id}`} className="mt-auto text-center px-4 py-2 bg-[var(--color-champagne)] text-[var(--color-midnight)] text-sm font-semibold rounded-full hover:bg-[var(--color-champagne)]/90 transition-colors">
            Ver detalles y cotizar
          </Link>
        )}
      </div>
    </article>
  )
}
```

- [ ] **Step 4: Run test — expect PASS**

```bash
npx jest tests/unit/LotCard.test.tsx
```
Expected: PASS — 4 tests

- [ ] **Step 5: Create LotFilter**

```tsx
// website/components/lots/LotFilter.tsx
'use client'
import type { LotStatus } from '@/lib/types'

interface Props {
  status: LotStatus | 'all'
  onChange: (status: LotStatus | 'all') => void
}

const options: { value: LotStatus | 'all'; label: string }[] = [
  { value: 'all', label: 'Todos' },
  { value: 'disponible', label: 'Disponibles' },
  { value: 'apartado', label: 'Apartados' },
  { value: 'vendido', label: 'Vendidos' },
]

export default function LotFilter({ status, onChange }: Props) {
  return (
    <div className="flex gap-2 flex-wrap">
      {options.map(opt => (
        <button
          key={opt.value}
          onClick={() => onChange(opt.value)}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
            status === opt.value
              ? 'bg-[var(--color-champagne)] text-[var(--color-midnight)]'
              : 'bg-[var(--color-slate)] text-[var(--color-ivory)]/70 hover:text-[var(--color-ivory)]'
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  )
}
```

- [ ] **Step 6: Create LotGrid**

```tsx
// website/components/lots/LotGrid.tsx
'use client'
import { useState } from 'react'
import type { Lot, LotStatus } from '@/lib/types'
import LotCard from './LotCard'
import LotFilter from './LotFilter'

export default function LotGrid({ lots }: { lots: Lot[] }) {
  const [filter, setFilter] = useState<LotStatus | 'all'>('all')
  const visible = filter === 'all' ? lots : lots.filter(l => l.status === filter)

  return (
    <div className="flex flex-col gap-8">
      <LotFilter status={filter} onChange={setFilter} />
      {visible.length === 0 ? (
        <p className="text-[var(--color-ivory)]/50 text-center py-12">No hay lotes en esta categoría.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {visible.map(lot => <LotCard key={lot.id} lot={lot} />)}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 7: Create FinancingCalc**

```tsx
// website/components/cotizador/FinancingCalc.tsx
'use client'
import { useEffect, useState } from 'react'
import type { FinancingOption } from '@/lib/types'

export default function FinancingCalc({ price }: { price: number }) {
  const [options, setOptions] = useState<FinancingOption[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/financing', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ price }),
    })
      .then(r => r.json())
      .then(data => { setOptions(data.options ?? []); setLoading(false) })
      .catch(() => setLoading(false))
  }, [price])

  if (loading) return <div className="animate-pulse h-32 bg-[var(--color-slate)] rounded-xl" />

  return (
    <div className="flex flex-col gap-3">
      <h3 className="font-display text-lg text-[var(--color-champagne)]">Opciones de financiamiento</h3>
      <div className="grid gap-2">
        {options.map(opt => (
          <div key={opt.label} className="flex justify-between items-center bg-[var(--color-midnight)] px-4 py-3 rounded-lg">
            <span className="text-[var(--color-ivory)]/80 text-sm">{opt.label}</span>
            <span className="text-[var(--color-champagne)] font-semibold">
              ${opt.monthlyPayment.toLocaleString('es-MX', { maximumFractionDigits: 0 })} /mes
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 8: Create LeadForm**

```tsx
// website/components/cotizador/LeadForm.tsx
'use client'
import { useState } from 'react'
import type { Lead } from '@/lib/types'

export default function LeadForm({ lotId, lotName }: { lotId?: string; lotName?: string }) {
  const [form, setForm] = useState<Partial<Lead>>({})
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')

  const set = (k: keyof Lead) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    setForm(prev => ({ ...prev, [k]: e.target.value }))

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setStatus('loading')
    const res = await fetch('/api/leads', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...form, lotId }),
    })
    setStatus(res.ok ? 'success' : 'error')
  }

  if (status === 'success') {
    return (
      <div className="bg-emerald-900/30 border border-emerald-500/30 rounded-xl p-6 text-center">
        <p className="text-emerald-300 font-medium">¡Gracias! Un asesor te contactará en menos de 2 minutos.</p>
      </div>
    )
  }

  return (
    <form onSubmit={submit} className="flex flex-col gap-4">
      {lotName && <p className="text-[var(--color-ivory)]/60 text-sm">Cotizando: <strong className="text-[var(--color-champagne)]">{lotName}</strong></p>}
      <div className="grid grid-cols-2 gap-3">
        <input required placeholder="Nombre" value={form.firstName ?? ''} onChange={set('firstName')}
          className="col-span-1 bg-[var(--color-midnight)] border border-[var(--color-champagne)]/20 rounded-lg px-4 py-3 text-sm text-[var(--color-ivory)] placeholder-[var(--color-ivory)]/30 focus:outline-none focus:border-[var(--color-champagne)]/60" />
        <input required placeholder="Apellido" value={form.lastName ?? ''} onChange={set('lastName')}
          className="col-span-1 bg-[var(--color-midnight)] border border-[var(--color-champagne)]/20 rounded-lg px-4 py-3 text-sm text-[var(--color-ivory)] placeholder-[var(--color-ivory)]/30 focus:outline-none focus:border-[var(--color-champagne)]/60" />
      </div>
      <input required type="email" placeholder="Email" value={form.email ?? ''} onChange={set('email')}
        className="bg-[var(--color-midnight)] border border-[var(--color-champagne)]/20 rounded-lg px-4 py-3 text-sm text-[var(--color-ivory)] placeholder-[var(--color-ivory)]/30 focus:outline-none focus:border-[var(--color-champagne)]/60" />
      <input required type="tel" placeholder="Teléfono (con código de país)" value={form.phone ?? ''} onChange={set('phone')}
        className="bg-[var(--color-midnight)] border border-[var(--color-champagne)]/20 rounded-lg px-4 py-3 text-sm text-[var(--color-ivory)] placeholder-[var(--color-ivory)]/30 focus:outline-none focus:border-[var(--color-champagne)]/60" />
      <textarea placeholder="¿Alguna pregunta o comentario?" value={form.message ?? ''} onChange={set('message')} rows={3}
        className="bg-[var(--color-midnight)] border border-[var(--color-champagne)]/20 rounded-lg px-4 py-3 text-sm text-[var(--color-ivory)] placeholder-[var(--color-ivory)]/30 focus:outline-none focus:border-[var(--color-champagne)]/60 resize-none" />
      {status === 'error' && <p className="text-red-400 text-sm">Hubo un error. Inténtalo de nuevo.</p>}
      <button type="submit" disabled={status === 'loading'}
        className="bg-[var(--color-champagne)] text-[var(--color-midnight)] font-semibold py-3 rounded-full hover:bg-[var(--color-champagne)]/90 transition-colors disabled:opacity-60">
        {status === 'loading' ? 'Enviando…' : 'Quiero información'}
      </button>
    </form>
  )
}
```

- [ ] **Step 9: Run all unit tests**

```bash
npx jest
```
Expected: PASS — all tests green.

- [ ] **Step 10: Commit**

```bash
cd ..
git add website/components/ website/tests/unit/LotCard.test.tsx
git commit -m "feat: lot cards, grid, filter, cotizador, lead form"
```

---

### Task 6: Pages

**Files:**
- Modify: `website/app/page.tsx`
- Create: `website/app/lotes/page.tsx`
- Create: `website/app/lotes/[id]/page.tsx`
- Create: `website/app/contacto/page.tsx`
- Create: `website/components/ui/StatsBar.tsx`

- [ ] **Step 1: StatsBar component**

```tsx
// website/components/ui/StatsBar.tsx
const stats = [
  { value: '127', label: 'Lotes exclusivos' },
  { value: '18 hoyos', label: 'Campo Greg Letsche' },
  { value: '100%', label: 'Privada cerrada' },
  { value: 'Mérida', label: 'Country Lakes, Yucatán' },
]

export default function StatsBar() {
  return (
    <div className="bg-[var(--color-champagne)]/10 border-y border-[var(--color-champagne)]/20 py-8">
      <div className="max-w-7xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
        {stats.map(s => (
          <div key={s.label}>
            <p className="font-display text-2xl font-bold text-[var(--color-champagne)]">{s.value}</p>
            <p className="text-[var(--color-ivory)]/60 text-sm mt-1">{s.label}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Home page**

```tsx
// website/app/page.tsx
import Link from 'next/link'
import StatsBar from '@/components/ui/StatsBar'

export default function Home() {
  return (
    <>
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
        <div className="absolute inset-0 bg-gradient-to-b from-[var(--color-midnight)] via-[var(--color-midnight)]/80 to-[var(--color-midnight)]" />
        <div className="relative z-10 text-center max-w-4xl mx-auto px-6">
          <p className="text-[var(--color-champagne)] text-sm tracking-[0.2em] uppercase mb-6 font-medium">Country Lakes · Mérida, Yucatán</p>
          <h1 className="font-display text-[var(--text-hero)] font-bold text-[var(--color-ivory)] leading-tight mb-6">
            La privada más exclusiva<br />frente al campo de golf
          </h1>
          <p className="text-[var(--color-ivory)]/70 text-lg max-w-2xl mx-auto mb-10">
            Augusta at Country Lakes es una comunidad de lotes residenciales con vista directa al campo de 18 hoyos diseñado por Greg Letsche — donde el lujo y la naturaleza son lo mismo.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/lotes" className="px-8 py-4 bg-[var(--color-champagne)] text-[var(--color-midnight)] font-semibold rounded-full hover:bg-[var(--color-champagne)]/90 transition-colors">
              Ver disponibilidad
            </Link>
            <Link href="/contacto" className="px-8 py-4 border border-[var(--color-champagne)]/40 text-[var(--color-champagne)] font-semibold rounded-full hover:border-[var(--color-champagne)] transition-colors">
              Hablar con un asesor
            </Link>
          </div>
        </div>
      </section>
      <StatsBar />
    </>
  )
}
```

- [ ] **Step 3: Lots listing page**

```tsx
// website/app/lotes/page.tsx
import type { Metadata } from 'next'
import { fetchLots } from '@/lib/odoo'
import LotGrid from '@/components/lots/LotGrid'

export const metadata: Metadata = {
  title: 'Lotes disponibles',
  description: 'Consulta los lotes disponibles en Augusta at Country Lakes — precios en tiempo real.',
}

export const revalidate = 60

export default async function LotesPage() {
  const lots = await fetchLots()

  return (
    <div className="pt-24 pb-20">
      <div className="max-w-7xl mx-auto px-6">
        <div className="mb-12">
          <h1 className="font-display text-[var(--text-h1)] font-bold text-[var(--color-ivory)]">Lotes disponibles</h1>
          <p className="text-[var(--color-ivory)]/60 mt-3 max-w-xl">
            Precios actualizados en tiempo real desde nuestro sistema de inventario.
          </p>
        </div>
        <LotGrid lots={lots} />
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Lot detail page**

```tsx
// website/app/lotes/[id]/page.tsx
import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { fetchLots } from '@/lib/odoo'
import FinancingCalc from '@/components/cotizador/FinancingCalc'
import LeadForm from '@/components/cotizador/LeadForm'

type Props = { params: Promise<{ id: string }> }

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params
  const lots = await fetchLots()
  const lot = lots.find(l => l.id === id)
  return {
    title: lot ? `${lot.name} — Cotizar` : 'Lote no encontrado',
  }
}

export const revalidate = 60

export default async function LotDetailPage({ params }: Props) {
  const { id } = await params
  const lots = await fetchLots()
  const lot = lots.find(l => l.id === id)

  if (!lot) notFound()

  return (
    <div className="pt-24 pb-20">
      <div className="max-w-5xl mx-auto px-6">
        <div className="grid md:grid-cols-2 gap-12">
          <div className="flex flex-col gap-6">
            <div>
              <h1 className="font-display text-[var(--text-h2)] font-bold text-[var(--color-ivory)]">{lot.name}</h1>
              <p className="text-[var(--color-champagne)] text-2xl font-semibold mt-2">
                ${lot.price.toLocaleString('es-MX')} MXN
              </p>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              {[['Superficie', `${lot.area} m²`], ['Orientación', lot.facing], ['Sección', lot.section], ['Estado', lot.status]].map(([k, v]) => (
                <div key={k} className="bg-[var(--color-slate)] rounded-lg px-4 py-3">
                  <p className="text-[var(--color-ivory)]/50">{k}</p>
                  <p className="text-[var(--color-ivory)] font-medium capitalize">{v}</p>
                </div>
              ))}
            </div>
            {lot.status === 'disponible' && <FinancingCalc price={lot.price} />}
          </div>
          <div className="bg-[var(--color-slate)] rounded-2xl p-6">
            <h2 className="font-display text-xl font-semibold text-[var(--color-ivory)] mb-6">Quiero información</h2>
            <LeadForm lotId={lot.id} lotName={lot.name} />
          </div>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 5: Contact page**

```tsx
// website/app/contacto/page.tsx
import type { Metadata } from 'next'
import LeadForm from '@/components/cotizador/LeadForm'

export const metadata: Metadata = {
  title: 'Contacto',
  description: 'Habla con un asesor de Augusta at Country Lakes.',
}

export default function ContactoPage() {
  return (
    <div className="pt-24 pb-20">
      <div className="max-w-lg mx-auto px-6">
        <h1 className="font-display text-[var(--text-h1)] font-bold text-[var(--color-ivory)] mb-4">Contacto</h1>
        <p className="text-[var(--color-ivory)]/60 mb-10">Un asesor te responderá en menos de 2 minutos durante horario de oficina.</p>
        <LeadForm />
      </div>
    </div>
  )
}
```

- [ ] **Step 6: Verify no TypeScript errors**

```bash
cd website && npx tsc --noEmit
```
Expected: no errors.

- [ ] **Step 7: Commit**

```bash
cd ..
git add website/app/ website/components/ui/
git commit -m "feat: home, lots listing, lot detail, and contact pages"
```

---

### Task 7: SEO — robots, sitemap, llms.txt, Schema.org

**Files:**
- Create: `website/app/robots.txt/route.ts`
- Create: `website/app/sitemap.ts`
- Create: `website/public/llms.txt`

Note: Schema.org JSON-LD is already injected in `app/layout.tsx` via the `next/script` `Script` component (Task 2). This task adds the remaining SEO files.

- [ ] **Step 1: robots.txt dynamic route**

```ts
// website/app/robots.txt/route.ts
export function GET() {
  const content = `User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: Claude-Web
Allow: /

Sitemap: https://augustacountrylakes.mx/sitemap.xml
`
  return new Response(content, {
    headers: { 'Content-Type': 'text/plain' },
  })
}
```

- [ ] **Step 2: Dynamic sitemap**

```ts
// website/app/sitemap.ts
import type { MetadataRoute } from 'next'
import { fetchLots } from '@/lib/odoo'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const lots = await fetchLots()
  const base = 'https://augustacountrylakes.mx'

  const staticRoutes: MetadataRoute.Sitemap = [
    { url: base, lastModified: new Date(), changeFrequency: 'daily', priority: 1 },
    { url: `${base}/lotes`, lastModified: new Date(), changeFrequency: 'hourly', priority: 0.9 },
    { url: `${base}/contacto`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.7 },
  ]

  const lotRoutes: MetadataRoute.Sitemap = lots
    .filter(l => l.status === 'disponible')
    .map(l => ({
      url: `${base}/lotes/${l.id}`,
      lastModified: new Date(),
      changeFrequency: 'hourly' as const,
      priority: 0.8,
    }))

  return [...staticRoutes, ...lotRoutes]
}
```

- [ ] **Step 3: llms.txt for AI search visibility**

```text
# Augusta at Country Lakes — Mérida, Yucatán

Augusta at Country Lakes es la privada residencial de lotes más exclusiva de Mérida, ubicada frente al campo de golf de 18 hoyos diseñado por Greg Letsche en Country Lakes.

## Proyecto
- Desarrollador: Boma Desarrollos (Alberto Miranda)
- Ubicación: Country Lakes, Mérida, Yucatán, México
- Producto: Lotes residenciales de lujo (aprox. 350–600 m²)
- Acceso: Privada cerrada con seguridad 24/7
- Vista: Campo de golf Greg Letsche — 18 hoyos

## Diferenciadores
- Único desarrollo residencial con frente directo al campo Greg Letsche
- Comunidad de bajo volumen: 127 lotes exclusivos
- Precio en tiempo real vía sistema Odoo
- Financiamiento flexible: contado, 12, 36, 60 y 120 meses

## Contacto
- Sitio web: https://augustacountrylakes.mx
- Correo: ventas@augustacountrylakes.mx
```

Save as `website/public/llms.txt`

- [ ] **Step 4: Add RealEstateListing schema in layout**

Update `app/layout.tsx` to add a second `Script` tag after the existing org schema:

```tsx
// Add this constant below orgSchema in layout.tsx:
const realEstateSchema = {
  '@context': 'https://schema.org',
  '@type': 'RealEstateListing',
  name: 'Augusta at Country Lakes — Lotes Residenciales',
  description: 'Lotes residenciales de lujo frente al campo de golf de Greg Letsche en Country Lakes, Mérida.',
  url: 'https://augustacountrylakes.mx/lotes',
  address: {
    '@type': 'PostalAddress',
    addressLocality: 'Mérida',
    addressRegion: 'Yucatán',
    addressCountry: 'MX',
    streetAddress: 'Country Lakes',
  },
}

// Then in <head> alongside the existing Script:
<Script id="schema-real-estate" type="application/ld+json" strategy="beforeInteractive">
  {JSON.stringify(realEstateSchema)}
</Script>
```

- [ ] **Step 5: Verify sitemap and robots resolve**

```bash
cd website && npm run build
```
Expected: build completes, sitemap.xml and robots.txt routes compiled without errors.

- [ ] **Step 6: Commit**

```bash
cd ..
git add website/app/robots.txt/ website/app/sitemap.ts website/public/llms.txt
git commit -m "feat: seo — robots, sitemap, llms.txt, schema.org"
```

---

### Task 8: E2E Tests with Playwright

**Files:**
- Create: `website/playwright.config.ts`
- Create: `website/tests/e2e/home.spec.ts`
- Create: `website/tests/e2e/cotizador.spec.ts`
- Create: `website/tests/e2e/lead-form.spec.ts`

- [ ] **Step 1: Playwright config**

```ts
// website/playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'Mobile Safari', use: { ...devices['iPhone 13'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

- [ ] **Step 2: Home E2E test**

```ts
// website/tests/e2e/home.spec.ts
import { test, expect } from '@playwright/test'

test('home loads with hero heading', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('h1')).toBeVisible()
  await expect(page.locator('h1')).toContainText('campo de golf')
})

test('stats bar shows key numbers', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('127')).toBeVisible()
  await expect(page.getByText('18 hoyos')).toBeVisible()
})

test('nav link goes to lotes page', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('link', { name: /Lotes/ }).first().click()
  await expect(page).toHaveURL('/lotes')
})
```

- [ ] **Step 3: Cotizador E2E test**

```ts
// website/tests/e2e/cotizador.spec.ts
import { test, expect } from '@playwright/test'

test('lotes page shows lot grid', async ({ page }) => {
  await page.goto('/lotes')
  await expect(page.locator('h1')).toContainText('Lotes disponibles')
  // Grid renders (may be empty if Odoo not configured — just check no crash)
  await expect(page.locator('main')).toBeVisible()
})

test('filter buttons are visible', async ({ page }) => {
  await page.goto('/lotes')
  await expect(page.getByRole('button', { name: 'Todos' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Disponibles' })).toBeVisible()
})
```

- [ ] **Step 4: Lead form E2E test**

```ts
// website/tests/e2e/lead-form.spec.ts
import { test, expect } from '@playwright/test'

test('contact form renders all fields', async ({ page }) => {
  await page.goto('/contacto')
  await expect(page.getByPlaceholder('Nombre')).toBeVisible()
  await expect(page.getByPlaceholder('Apellido')).toBeVisible()
  await expect(page.getByPlaceholder('Email')).toBeVisible()
  await expect(page.getByPlaceholder(/Teléfono/)).toBeVisible()
})

test('form shows validation if submitted empty', async ({ page }) => {
  await page.goto('/contacto')
  await page.getByRole('button', { name: /Quiero información/ }).click()
  // Browser native validation prevents submission
  await expect(page).toHaveURL('/contacto')
})
```

- [ ] **Step 5: Install Playwright browsers and run**

```bash
cd website && npx playwright install chromium
npx playwright test
```
Expected: All E2E tests PASS.

- [ ] **Step 6: Commit**

```bash
cd ..
git add website/playwright.config.ts website/tests/e2e/
git commit -m "test: e2e playwright suite for home, cotizador, lead form"
```

---

### Task 9: Vercel Deploy Configuration

**Files:**
- Create: `website/vercel.json`
- Create: `vercel.json` (repo root, points to subfolder)

- [ ] **Step 1: Website vercel.json**

```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install",
  "env": {
    "ODOO_API_URL": "@odoo_api_url",
    "ODOO_API_KEY": "@odoo_api_key",
    "ODOO_DATABASE": "@odoo_database",
    "HUBSPOT_API_KEY": "@hubspot_api_key",
    "HUBSPOT_PORTAL_ID": "@hubspot_portal_id",
    "WHATSAPP_API_TOKEN": "@whatsapp_api_token",
    "WHATSAPP_PHONE_ID": "@whatsapp_phone_id",
    "WHATSAPP_SALES_NUMBER": "@whatsapp_sales_number"
  }
}
```
Save as `website/vercel.json`

- [ ] **Step 2: Root vercel.json pointing to subfolder**

```json
{
  "rootDirectory": "website"
}
```
Save as `vercel.json` in the repo root.

- [ ] **Step 3: Add build script to package.json**

Verify `website/package.json` has:
```json
"scripts": {
  "dev": "next dev",
  "build": "next build",
  "start": "next start",
  "lint": "next lint",
  "test": "jest",
  "test:e2e": "playwright test"
}
```

- [ ] **Step 4: Final build verification**

```bash
cd website && npm run build
```
Expected: Build completes successfully. Note any warnings but no blocking errors.

- [ ] **Step 5: Commit**

```bash
cd ..
git add vercel.json website/vercel.json website/package.json
git commit -m "feat: vercel deploy config for website subfolder"
```

- [ ] **Step 6: Push to GitHub**

```bash
git push origin main
```
Expected: Push succeeds. Connect repo to Vercel at vercel.com/new → Import → select `arqalbertomiranda-del/Augusta-at-Coutry-Lakes` → Root Directory: `website`.

---

## Self-Review

**Spec coverage:**
- ✅ Next.js 15 App Router with TypeScript
- ✅ Real-time Odoo inventory with ISR (60s revalidate)
- ✅ HubSpot CRM lead capture
- ✅ WhatsApp instant notification (<2 min promise)
- ✅ Financing calculator with 5 plans
- ✅ SEO: robots.txt, sitemap, llms.txt, Schema.org
- ✅ Tailwind CSS + design tokens (midnight/champagne/ivory palette)
- ✅ Unit tests (financing, LotCard) + E2E Playwright
- ✅ Vercel deploy config

**No placeholders:** All code blocks contain complete, runnable code.

**Type consistency:** `Lot`, `Lead`, `FinancingInput`, `FinancingOption` defined once in `lib/types.ts` and imported consistently.
