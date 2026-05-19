'use client'
import Link from 'next/link'
import { useState } from 'react'

// Nav items typed as [label, href] — href cast to satisfy typedRoutes
// until /lotes and /contacto pages are created in later tasks
const navItems = [
  ['Inicio', '/'],
  ['Lotes', '/lotes'],
  ['Contacto', '/contacto'],
] as const

export default function Header() {
  const [open, setOpen] = useState(false)

  return (
    <header className="fixed top-0 inset-x-0 z-50 bg-[#0A0E1A]/90 backdrop-blur-md border-b border-[#C8A96E]/20">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="text-[#C8A96E] text-xl font-semibold tracking-wide" style={{ fontFamily: 'var(--font-display)' }}>
          Augusta
        </Link>
        <nav className="hidden md:flex items-center gap-8">
          {navItems.map(([label, href]) => (
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            <Link key={href} href={href as any} className="text-[#FAF8F3]/80 hover:text-[#C8A96E] text-sm transition-colors duration-150">
              {label}
            </Link>
          ))}
          {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
          <Link href={'/lotes' as any} className="px-5 py-2 bg-[#C8A96E] text-[#0A0E1A] text-sm font-semibold rounded-full hover:bg-[#C8A96E]/90 transition-colors">
            Ver disponibilidad
          </Link>
        </nav>
        <button className="md:hidden text-[#FAF8F3]" onClick={() => setOpen(!open)} aria-label="Menu">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={open ? 'M6 18L18 6M6 6l12 12' : 'M4 6h16M4 12h16M4 18h16'} />
          </svg>
        </button>
      </div>
      {open && (
        <div className="md:hidden bg-[#0A0E1A] border-t border-[#C8A96E]/20 px-6 py-4 flex flex-col gap-4">
          {navItems.map(([label, href]) => (
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            <Link key={href} href={href as any} className="text-[#FAF8F3]/80 text-sm" onClick={() => setOpen(false)}>
              {label}
            </Link>
          ))}
        </div>
      )}
    </header>
  )
}
