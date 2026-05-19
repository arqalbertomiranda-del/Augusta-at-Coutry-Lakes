export default function Footer() {
  return (
    <footer className="bg-[#0A0E1A] border-t border-[#C8A96E]/20 py-12">
      <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-start gap-8">
        <div>
          <p className="text-[#C8A96E] text-lg font-semibold" style={{ fontFamily: 'var(--font-display)' }}>Augusta at Country Lakes</p>
          <p className="text-[#FAF8F3]/50 text-sm mt-1">Frente al campo de golf de Greg Letsche · Mérida, Yucatán</p>
        </div>
        <div className="text-[#FAF8F3]/50 text-sm">
          <p>© {new Date().getFullYear()} Boma Desarrollos. Todos los derechos reservados.</p>
        </div>
      </div>
    </footer>
  )
}
