import { NextRequest, NextResponse } from 'next/server'
import { calculateMonthlyPayment } from '@/lib/financing'
import type { FinancingOption } from '@/lib/types'

export const runtime = 'nodejs'

const PLANS = [
  { label: 'Contado (5% desc.)', months: 1, discount: 0.05 },
  { label: '12 meses', months: 12, annualRate: 0.10 },
  { label: '36 meses', months: 36, annualRate: 0.12 },
  { label: '60 meses', months: 60, annualRate: 0.14 },
  { label: '120 meses', months: 120, annualRate: 0.15 },
] as const

export async function POST(req: NextRequest) {
  let price: number
  try {
    const body = await req.json() as { price?: unknown }
    price = Number(body.price)
  } catch {
    return NextResponse.json({ error: 'Cuerpo de solicitud inválido' }, { status: 400 })
  }

  if (!Number.isFinite(price) || price <= 0 || price > 1_000_000_000) {
    return NextResponse.json({ error: 'Precio fuera de rango (debe ser entre 1 y 1,000,000,000)' }, { status: 400 })
  }

  let options: FinancingOption[]
  try {
    options = PLANS.map(plan => {
      const annualRate = 'discount' in plan ? 0 : plan.annualRate
      const principal = 'discount' in plan ? price * (1 - plan.discount) : price
      const months = plan.months
      return {
        label: plan.label,
        months,
        annualRate,
        monthlyPayment: calculateMonthlyPayment({ principal, annualRate, months }),
      }
    })
  } catch (err) {
    console.error('[POST /api/financing]', err)
    return NextResponse.json({ error: 'Error calculando opciones de financiamiento' }, { status: 500 })
  }
  return NextResponse.json({ options })
}
