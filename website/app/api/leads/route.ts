import { NextRequest, NextResponse } from 'next/server'
import { createContact } from '@/lib/hubspot'
import { notifySales } from '@/lib/whatsapp'
import type { Lead } from '@/lib/types'

export const runtime = 'nodejs'

export async function POST(req: NextRequest) {
  let body: Partial<Lead & { lotId: string }>
  try {
    body = await req.json() as Partial<Lead & { lotId: string }>
  } catch {
    return NextResponse.json({ error: 'Cuerpo de solicitud inválido' }, { status: 400 })
  }

  if (!body.firstName || !body.lastName || !body.email || !body.phone) {
    return NextResponse.json({ error: 'Nombre, apellido, email y teléfono son requeridos' }, { status: 400 })
  }

  const lead: Lead = {
    firstName: body.firstName,
    lastName: body.lastName,
    email: body.email,
    phone: body.phone,
    message: body.message,
    lotId: body.lotId,
    utmSource: req.nextUrl.searchParams.get('utm_source') ?? undefined,
    utmCampaign: req.nextUrl.searchParams.get('utm_campaign') ?? undefined,
  }

  try {
    const [contactResult] = await Promise.allSettled([
      createContact(lead),
      notifySales(lead, body.lotId),
    ])

    if (contactResult.status === 'rejected') {
      console.error('[POST /api/leads] HubSpot error:', contactResult.reason)
      return NextResponse.json({ error: 'Error registrando lead en CRM' }, { status: 500 })
    }

    return NextResponse.json({ success: true, contactId: contactResult.value.id })
  } catch (err) {
    console.error('[POST /api/leads]', err)
    return NextResponse.json({ error: 'Error interno del servidor' }, { status: 500 })
  }
}
