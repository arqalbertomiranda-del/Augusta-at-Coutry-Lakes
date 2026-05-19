import Link from 'next/link'
import StatsBar from '@/components/ui/StatsBar'

export default function Home() {
  return (
    <>
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
        <div className="absolute inset-0 bg-gradient-to-b from-[#0A0E1A] via-[#0A0E1A]/85 to-[#0A0E1A]" />
        <div className="relative z-10 text-center max-w-4xl mx-auto px-6 py-20">
          <p className="text-[#C8A96E] text-sm tracking-[0.25em] uppercase mb-6 font-medium">Country Lakes · Mérida, Yucatán</p>
          <h1
            className="font-bold text-[#FAF8F3] leading-tight mb-6"
            style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-hero)' }}
          >
            La privada más exclusiva<br />frente al campo de golf
          </h1>
          <p className="text-[#FAF8F3]/70 text-lg max-w-2xl mx-auto mb-10 leading-relaxed">
            Augusta at Country Lakes — lotes residenciales de lujo con vista directa al campo de 18 hoyos diseñado por Greg Letsche. El único desarrollo de su tipo en Latinoamérica.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/lotes"
              className="px-8 py-4 bg-[#C8A96E] text-[#0A0E1A] font-semibold rounded-full hover:bg-[#C8A96E]/90 transition-colors text-base"
            >
              Ver disponibilidad
            </Link>
            <Link
              href="/contacto"
              className="px-8 py-4 border border-[#C8A96E]/40 text-[#C8A96E] font-semibold rounded-full hover:border-[#C8A96E] transition-colors text-base"
            >
              Hablar con un asesor
            </Link>
          </div>
        </div>
      </section>
      <StatsBar />
    </>
  )
}
