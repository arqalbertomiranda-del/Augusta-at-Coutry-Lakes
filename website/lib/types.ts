export type LotStatus = 'disponible' | 'apartado' | 'vendido'

export interface Lot {
  id: string
  name: string
  area: number
  price: number
  status: LotStatus
  facing: string
  section: string
  imageUrl?: string
}

export interface Lead {
  firstName: string
  lastName: string
  email: string
  phone: string
  message?: string
  lotId?: string
  utmSource?: string
  utmCampaign?: string
}

export interface FinancingInput {
  principal: number
  annualRate: number
  months: number
}

export interface AmortizationRow {
  period: number
  payment: number
  interest: number
  principal: number
  balance: number
}

export interface FinancingOption {
  label: string
  months: number
  annualRate: number
  monthlyPayment: number
}

export type FilterValue = LotStatus | 'all'
