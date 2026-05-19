import type { Metadata } from 'next'
import LeadForm from '@/components/cotizador/LeadForm'

export const metadata: Metadata = {
  title: 'Contacto',
  description: 'Habla con un asesor de Augusta at Country Lakes. Respuesta en menos de 2 minutos.',
}

export default function ContactoPage() {
  return (
    <div className="pt-24 pb-20">
      <div className="max-w-lg mx-auto px-6">
        <h1
          className="font-bold text-[#FAF8F3] mb-4"
          style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-h1)' }}
        >
          Contacto
        </h1>
        <p className="text-[#FAF8F3]/55 mb-10 leading-relaxed">
          Un asesor te responderá en menos de 2 minutos durante horario de oficina (Lun–Vie 9am–7pm, Sáb 10am–3pm, hora de Mérida).
        </p>
        <LeadForm />
      </div>
    </div>
  )
}
