'use client'
import { useState } from 'react'
import type { Lot, LotStatus, FilterValue } from '@/lib/types'
import LotCard from './LotCard'
import LotFilter from './LotFilter'

export default function LotGrid({ lots }: { lots: Lot[] }) {
  const [filter, setFilter] = useState<FilterValue>('all')
  const visible = filter === 'all' ? lots : lots.filter(l => l.status === filter)

  return (
    <div className="flex flex-col gap-8">
      <LotFilter value={filter} onChange={setFilter} />
      {visible.length === 0 ? (
        <p className="text-[#FAF8F3]/40 text-center py-16">No hay lotes en esta categoría.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {visible.map(lot => <LotCard key={lot.id} lot={lot} />)}
        </div>
      )}
    </div>
  )
}
