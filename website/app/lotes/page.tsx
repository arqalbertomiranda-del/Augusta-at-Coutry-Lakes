import type { Metadata } from 'next'
import { fetchLots } from '@/lib/odoo'
import type { Lot } from '@/lib/types'
import LotGrid from '@/components/lots/LotGrid'

export const metadata: Metadata = {
  title: 'Lotes disponibles',
  description: 'Consulta los lotes en Augusta at Country Lakes — precios en tiempo real desde Odoo.',
}

export const revalidate = 60

export default async function LotesPage() {
  let lots: Lot[]
  try {
    lots = await fetchLots()
  } catch {
    lots = []
  }

  return (
    <div className="pt-24 pb-20">
      <div className="max-w-7xl mx-auto px-6">
        <div className="mb-10">
          <h1
            className="font-bold text-[#FAF8F3]"
            style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-h1)' }}
          >
            Lotes disponibles
          </h1>
          <p className="text-[#FAF8F3]/55 mt-3 max-w-xl">
            Precios actualizados en tiempo real. Haz clic en cualquier lote para ver detalles y opciones de financiamiento.
          </p>
        </div>
        {lots.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-[#FAF8F3]/40 text-lg">Inventario no disponible en este momento.</p>
            <p className="text-[#FAF8F3]/30 text-sm mt-2">Por favor contáctanos directamente para consultar disponibilidad.</p>
          </div>
        ) : (
          <LotGrid lots={lots} />
        )}
      </div>
    </div>
  )
}
