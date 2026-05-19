import { calculateMonthlyPayment, buildAmortizationSchedule } from '@/lib/financing'

describe('calculateMonthlyPayment', () => {
  it('calculates correct monthly payment for standard loan', () => {
    const result = calculateMonthlyPayment({ principal: 1_000_000, annualRate: 0.12, months: 120 })
    expect(result).toBeCloseTo(14_347, 0)
  })

  it('returns principal divided by months when rate is 0', () => {
    const result = calculateMonthlyPayment({ principal: 600_000, annualRate: 0, months: 60 })
    expect(result).toBeCloseTo(10_000, 0)
  })
})

describe('buildAmortizationSchedule', () => {
  it('returns array of length equal to months', () => {
    const schedule = buildAmortizationSchedule({ principal: 500_000, annualRate: 0.10, months: 12 })
    expect(schedule).toHaveLength(12)
  })

  it('last entry has near-zero remaining balance', () => {
    const schedule = buildAmortizationSchedule({ principal: 500_000, annualRate: 0.10, months: 12 })
    expect(schedule[11].balance).toBeCloseTo(0, 0)
  })
})
