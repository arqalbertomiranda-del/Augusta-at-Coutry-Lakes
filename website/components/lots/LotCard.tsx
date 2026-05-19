import Link from 'next/link'
import type { Lot } from '@/lib/types'

const statusConfig = {
  disponible: { label: 'Disponible', className: 'bg-emerald-900/40 text-emerald-300' },
  apartado:   { label: 'Apartado',   className: 'bg-amber-900/40 text-amber-300' },
  vendido:    { label: 'Vendido',    className: 'bg-red-900/40 text-red-300' },
} satisfies Record<string, { label: string; className: string }>

export default function LotCard({ lot }: { lot: Lot }) {
  const config = statusConfig[lot.status]

  return (
    <article className="bg-[#2D3340] rounded-xl overflow-hidden flex flex-col shadow-lg">
      <div className="bg-[#0A0E1A] h-44 flex items-center justify-center text-[#C8A96E]/20 text-6xl select-none">
        ⛳
      </div>
      <div className="p-5 flex flex-col gap-3 flex-1">
        <div className="flex justify-between items-start gap-2">
          <h3 className="font-semibold text-[#FAF8F3] leading-snug" style={{ fontFamily: 'var(--font-display)' }}>
            {lot.name}
          </h3>
          <span className={`shrink-0 text-xs px-2 py-1 rounded-full font-medium ${config.className}`}>
            {config.label}
          </span>
        </div>
        <div className="text-[#FAF8F3]/55 text-sm flex gap-4">
          <span>{lot.area} m²</span>
          {lot.facing && <span>{lot.facing}</span>}
          {lot.section && <span>Sec. {lot.section}</span>}
        </div>
        <p className="text-[#C8A96E] text-xl font-semibold">
          ${lot.price.toLocaleString('es-MX')} MXN
        </p>
        {lot.status === 'disponible' && (
          <Link
            href={`/lotes/${lot.id}`}
            className="mt-auto text-center px-4 py-2.5 bg-[#C8A96E] text-[#0A0E1A] text-sm font-semibold rounded-full hover:bg-[#C8A96E]/90 transition-colors"
          >
            Ver detalles y cotizar
          </Link>
        )}
      </div>
    </article>
  )
}
