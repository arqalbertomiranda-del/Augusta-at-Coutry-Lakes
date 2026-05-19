const stats = [
  { value: '127', label: 'Lotes exclusivos' },
  { value: '18 hoyos', label: 'Campo Greg Letsche' },
  { value: '100%', label: 'Privada cerrada' },
  { value: 'Mérida', label: 'Country Lakes, Yucatán' },
]

export default function StatsBar() {
  return (
    <div className="bg-[#C8A96E]/10 border-y border-[#C8A96E]/20 py-8">
      <div className="max-w-7xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
        {stats.map(s => (
          <div key={s.label}>
            <p className="text-2xl font-bold text-[#C8A96E]" style={{ fontFamily: 'var(--font-display)' }}>{s.value}</p>
            <p className="text-[#FAF8F3]/55 text-sm mt-1">{s.label}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
