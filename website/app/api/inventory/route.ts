import { NextResponse } from 'next/server'
import { fetchLots } from '@/lib/odoo'

export const runtime = 'nodejs'
export const revalidate = 60

export async function GET() {
  try {
    const lots = await fetchLots()
    return NextResponse.json({ lots })
  } catch (err) {
    console.error('[GET /api/inventory]', err)
    return NextResponse.json({ lots: [], error: 'Error obteniendo inventario' }, { status: 500 })
  }
}
