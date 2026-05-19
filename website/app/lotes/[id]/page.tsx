import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { fetchLots } from '@/lib/odoo'
import type { Lot } from '@/lib/types'
import FinancingCalc from '@/components/cotizador/FinancingCalc'
import LeadForm from '@/components/cotizador/LeadForm'

type Props = { params: Promise<{ id: string }> }

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params
  try {
    const lots = await fetchLots()
    const lot = lots.find(l => l.id === id)
    if (lot) return { title: `${lot.name} — Cotizar`, description: `${lot.area} m² · $${lot.price.toLocaleString('es-MX')} MXN` }
  } catch {
    // Odoo unavailable — return generic metadata
  }
  return { title: 'Lote' }
}

export const revalidate = 60

export default async function LotDetailPage({ params }: Props) {
  const { id } = await params
  let lots: Lot[]
  try {
    lots = await fetchLots()
  } catch {
    lots = []
  }

  const lot = lots.find(l => l.id === id)
  if (!lot) notFound()

  const details: [string, string][] = [
    ['Superficie', `${lot.area} m²`],
    ['Orientación', lot.facing || '—'],
    ['Sección', lot.section || '—'],
    ['Estado', lot.status === 'disponible' ? 'Disponible' : lot.status === 'apartado' ? 'Apartado' : 'Vendido'],
  ]

  return (
    <div className="pt-24 pb-20">
      <div className="max-w-5xl mx-auto px-6">
        <div className="grid md:grid-cols-2 gap-12 items-start">
          {/* Left column */}
          <div className="flex flex-col gap-6">
            <div>
              <h1
                className="font-bold text-[#FAF8F3]"
                style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-h2)' }}
              >
                {lot.name}
              </h1>
              <p className="text-[#C8A96E] text-2xl font-semibold mt-2">
                ${lot.price.toLocaleString('es-MX')} MXN
              </p>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {details.map(([k, v]) => (
                <div key={k} className="bg-[#2D3340] rounded-xl px-4 py-3">
                  <p className="text-[#FAF8F3]/45 text-xs uppercase tracking-wider">{k}</p>
                  <p className="text-[#FAF8F3] font-medium mt-1 capitalize">{v}</p>
                </div>
              ))}
            </div>
            {lot.status === 'disponible' && <FinancingCalc price={lot.price} />}
          </div>
          {/* Right column */}
          <div className="bg-[#2D3340] rounded-2xl p-6">
            <h2
              className="font-semibold text-[#FAF8F3] text-xl mb-6"
              style={{ fontFamily: 'var(--font-display)' }}
            >
              Quiero información
            </h2>
            <LeadForm lotId={lot.id} lotName={lot.name} />
          </div>
        </div>
      </div>
    </div>
  )
}
