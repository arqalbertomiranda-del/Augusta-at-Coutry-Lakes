import type { Lead } from './types'

const API_KEY = process.env.HUBSPOT_API_KEY

export async function createContact(lead: Lead): Promise<{ id: string }> {
  if (!API_KEY) throw new Error('HUBSPOT_API_KEY not configured')

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 10_000)

  try {
    const res = await fetch('https://api.hubapi.com/crm/v3/objects/contacts', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${API_KEY}`,
        'Content-Type': 'application/json',
      },
      signal: controller.signal,
      body: JSON.stringify({
        properties: {
          firstname: lead.firstName,
          lastname: lead.lastName,
          email: lead.email,
          phone: lead.phone,
          message: lead.message ?? '',
          augusta_lot_id: lead.lotId ?? '',
          utm_source: lead.utmSource ?? '',
          utm_campaign: lead.utmCampaign ?? '',
          hs_lead_status: 'NEW',
          lifecyclestage: 'lead',
        },
      }),
    })

    if (!res.ok) {
      const body = await res.text()
      console.error(`HubSpot API error (${res.status}):`, body)
      throw new Error(`HubSpot API error (${res.status})`)
    }

    const data = await res.json() as { id: string }
    return { id: data.id }
  } finally {
    clearTimeout(timeoutId)
  }
}
