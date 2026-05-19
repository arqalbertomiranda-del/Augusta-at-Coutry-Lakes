'use client'
import { useEffect, useState } from 'react'
import type { FinancingOption } from '@/lib/types'

export default function FinancingCalc({ price }: { price: number }) {
  const [options, setOptions] = useState<FinancingOption[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    setLoading(true)
    setError(false)
    fetch('/api/financing', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ price }),
    })
      .then(r => r.json())
      .then((data: { options?: FinancingOption[] }) => {
        setOptions(data.options ?? [])
        setLoading(false)
      })
      .catch(() => {
        setError(true)
        setLoading(false)
      })
  }, [price])

  if (loading) return <div className="animate-pulse h-36 rounded-xl bg-[#2D3340]" aria-label="Cargando opciones" />
  if (error) return <p className="text-red-400 text-sm">No se pudieron cargar las opciones de financiamiento.</p>

  return (
    <section aria-label="Opciones de financiamiento">
      <h3 className="text-[#C8A96E] font-semibold mb-3" style={{ fontFamily: 'var(--font-display)' }}>
        Opciones de financiamiento
      </h3>
      <div className="flex flex-col gap-2">
        {options.map(opt => (
          <div key={opt.label} className="flex justify-between items-center bg-[#0A0E1A] px-4 py-3 rounded-lg">
            <span className="text-[#FAF8F3]/75 text-sm">{opt.label}</span>
            <span className="text-[#C8A96E] font-semibold text-sm">
              ${opt.monthlyPayment.toLocaleString('es-MX', { maximumFractionDigits: 0 })} /mes
            </span>
          </div>
        ))}
      </div>
    </section>
  )
}
