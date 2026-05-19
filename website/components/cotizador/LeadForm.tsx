'use client'
import { useState } from 'react'

interface FormState {
  firstName: string
  lastName: string
  email: string
  phone: string
  message: string
}

const INITIAL: FormState = { firstName: '', lastName: '', email: '', phone: '', message: '' }

type Status = 'idle' | 'loading' | 'success' | 'error'

export default function LeadForm({ lotId, lotName }: { lotId?: string; lotName?: string }) {
  const [form, setForm] = useState<FormState>(INITIAL)
  const [status, setStatus] = useState<Status>('idle')

  const set = (k: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    setForm(prev => ({ ...prev, [k]: e.target.value }))

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setStatus('loading')
    try {
      const res = await fetch('/api/leads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, lotId }),
      })
      setStatus(res.ok ? 'success' : 'error')
    } catch {
      setStatus('error')
    }
  }

  if (status === 'success') {
    return (
      <div className="bg-emerald-900/30 border border-emerald-500/30 rounded-xl p-6 text-center">
        <p className="text-emerald-300 font-medium">¡Gracias! Un asesor te contactará en menos de 2 minutos.</p>
      </div>
    )
  }

  const inputClass = "w-full bg-[#0A0E1A] border border-[#C8A96E]/20 rounded-lg px-4 py-3 text-sm text-[#FAF8F3] placeholder-[#FAF8F3]/30 focus:outline-none focus:border-[#C8A96E]/60 transition-colors"

  return (
    <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-4">
      {lotName && (
        <p className="text-[#FAF8F3]/55 text-sm">
          Cotizando: <strong className="text-[#C8A96E]">{lotName}</strong>
        </p>
      )}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label htmlFor="firstName" className="sr-only">Nombre</label>
          <input
            id="firstName"
            name="firstName"
            required
            minLength={1}
            maxLength={100}
            autoComplete="given-name"
            placeholder="Nombre"
            value={form.firstName}
            onChange={set('firstName')}
            className={inputClass}
          />
        </div>
        <div>
          <label htmlFor="lastName" className="sr-only">Apellido</label>
          <input
            id="lastName"
            name="lastName"
            required
            minLength={1}
            maxLength={100}
            autoComplete="family-name"
            placeholder="Apellido"
            value={form.lastName}
            onChange={set('lastName')}
            className={inputClass}
          />
        </div>
      </div>
      <div>
        <label htmlFor="email" className="sr-only">Email</label>
        <input
          id="email"
          name="email"
          required
          type="email"
          autoComplete="email"
          placeholder="Email"
          value={form.email}
          onChange={set('email')}
          className={inputClass}
        />
      </div>
      <div>
        <label htmlFor="phone" className="sr-only">Teléfono</label>
        <input
          id="phone"
          name="phone"
          required
          type="tel"
          autoComplete="tel"
          placeholder="Teléfono (ej. +52 999 000 0000)"
          value={form.phone}
          onChange={set('phone')}
          className={inputClass}
        />
      </div>
      <div>
        <label htmlFor="message" className="sr-only">Mensaje</label>
        <textarea
          id="message"
          name="message"
          placeholder="¿Tienes alguna pregunta?"
          value={form.message}
          onChange={set('message')}
          rows={3}
          maxLength={2000}
          className={`${inputClass} resize-none`}
        />
      </div>
      {status === 'error' && (
        <p role="alert" className="text-red-400 text-sm">Hubo un error. Por favor intenta de nuevo.</p>
      )}
      <button
        type="submit"
        disabled={status === 'loading'}
        className="bg-[#C8A96E] text-[#0A0E1A] font-semibold py-3 rounded-full hover:bg-[#C8A96E]/90 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
      >
        {status === 'loading' ? 'Enviando…' : 'Quiero información'}
      </button>
    </form>
  )
}
