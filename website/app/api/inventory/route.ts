import { NextResponse } from 'next/server'
import { fetchLots } from '@/lib/odoo'

export const runtime = 'nodejs'
export const revalidate = 60

export async function GET() {
  try {
    const lots = await fetchLots()
    return NextResponse.json({ lots })
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Error desconocido'
    console.error('[GET /api/inventory]', err)
    return NextResponse.json({ lots: [], error: message }, { status: 500 })
  }
}
