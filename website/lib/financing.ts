import type { FinancingInput, AmortizationRow } from './types'

export function calculateMonthlyPayment({ principal, annualRate, months }: FinancingInput): number {
  if (principal <= 0 || months <= 0 || annualRate < 0) {
    throw new Error('Invalid financing input: principal and months must be positive, rate must be non-negative')
  }
  if (annualRate === 0) return principal / months
  const r = annualRate / 12
  return (principal * r * Math.pow(1 + r, months)) / (Math.pow(1 + r, months) - 1)
}

export function buildAmortizationSchedule({ principal, annualRate, months }: FinancingInput): AmortizationRow[] {
  const payment = calculateMonthlyPayment({ principal, annualRate, months })
  const r = annualRate / 12
  const rows: AmortizationRow[] = []
  let balance = principal

  for (let i = 1; i <= months; i++) {
    const interest = balance * r
    const principalPaid = payment - interest
    balance = Math.max(0, balance - principalPaid)
    rows.push({ period: i, payment, interest, principal: principalPaid, balance })
  }

  return rows
}
