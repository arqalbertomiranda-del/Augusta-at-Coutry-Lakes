import type { Lead } from './types'

const TOKEN = process.env.WHATSAPP_API_TOKEN
const PHONE_ID = process.env.WHATSAPP_PHONE_ID
const SALES_NUMBER = process.env.WHATSAPP_SALES_NUMBER

export async function notifySales(lead: Lead, lotId?: string): Promise<void> {
  if (!TOKEN || !PHONE_ID || !SALES_NUMBER) return

  const text = [
    '🏌️ *Nuevo lead Augusta*',
    `Nombre: ${lead.firstName} ${lead.lastName}`,
    `Tel: ${lead.phone}`,
    `Email: ${lead.email}`,
    (lotId ?? lead.lotId) ? `Lote: ${lotId ?? lead.lotId}` : '',
    lead.message ? `Mensaje: ${lead.message}` : '',
  ].filter(Boolean).join('\n')

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 8_000)

  try {
    const res = await fetch(`https://graph.facebook.com/v20.0/${PHONE_ID}/messages`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${TOKEN}`,
        'Content-Type': 'application/json',
      },
      signal: controller.signal,
      body: JSON.stringify({
        messaging_product: 'whatsapp',
        to: SALES_NUMBER,
        type: 'text',
        text: { body: text },
      }),
    })

    if (!res.ok) {
      const body = await res.text()
      console.error(`WhatsApp notification failed (${res.status}):`, body)
    }
  } catch (err) {
    console.error('WhatsApp notification error:', err)
  } finally {
    clearTimeout(timeoutId)
  }
}
