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
    lotId ? `Lote: ${lotId}` : '',
    lead.message ? `Mensaje: ${lead.message}` : '',
  ].filter(Boolean).join('\n')

  await fetch(`https://graph.facebook.com/v20.0/${PHONE_ID}/messages`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      messaging_product: 'whatsapp',
      to: SALES_NUMBER,
      type: 'text',
      text: { body: text },
    }),
  })
}
