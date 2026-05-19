import type { Lot, LotStatus } from './types'

const BASE_URL = process.env.ODOO_API_URL
const API_KEY = process.env.ODOO_API_KEY

export async function fetchLots(): Promise<Lot[]> {
  if (!BASE_URL || !API_KEY) return []

  const res = await fetch(`${BASE_URL}/api/method/augusta.get_lots`, {
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      'Content-Type': 'application/json',
    },
    next: { revalidate: 60 },
  })

  if (!res.ok) throw new Error(`Odoo error: ${res.status}`)

  const data = await res.json() as { result?: unknown[] }
  return (data.result ?? []).map(mapOdooLot)
}

function mapOdooLot(raw: unknown): Lot {
  const r = raw as Record<string, unknown>
  const statusMap: Record<string, LotStatus> = {
    available: 'disponible',
    reserved: 'apartado',
    sold: 'vendido',
  }
  return {
    id: String(r.id ?? ''),
    name: String(r.name ?? ''),
    area: Number(r.area_sqm ?? 0),
    price: Number(r.list_price ?? 0),
    status: statusMap[String(r.state ?? '')] ?? 'disponible',
    facing: String(r.facing ?? ''),
    section: String(r.section ?? ''),
    imageUrl: r.image_url ? String(r.image_url) : undefined,
  }
}
