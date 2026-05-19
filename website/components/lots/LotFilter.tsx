'use client'
import type { LotStatus } from '@/lib/types'

type FilterValue = LotStatus | 'all'

const options: { value: FilterValue; label: string }[] = [
  { value: 'all',        label: 'Todos' },
  { value: 'disponible', label: 'Disponibles' },
  { value: 'apartado',   label: 'Apartados' },
  { value: 'vendido',    label: 'Vendidos' },
]

export default function LotFilter({ value, onChange }: { value: FilterValue; onChange: (v: FilterValue) => void }) {
  return (
    <div className="flex gap-2 flex-wrap" role="group" aria-label="Filtrar lotes">
      {options.map(opt => (
        <button
          key={opt.value}
          onClick={() => onChange(opt.value)}
          aria-pressed={value === opt.value}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
            value === opt.value
              ? 'bg-[#C8A96E] text-[#0A0E1A]'
              : 'bg-[#2D3340] text-[#FAF8F3]/70 hover:text-[#FAF8F3]'
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  )
}
