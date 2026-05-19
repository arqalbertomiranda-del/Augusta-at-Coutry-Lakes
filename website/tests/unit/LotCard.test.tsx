/**
 * @jest-environment jsdom
 */
import React from 'react'
import { render, screen } from '@testing-library/react'
import LotCard from '@/components/lots/LotCard'
import type { Lot } from '@/lib/types'

const lot: Lot = {
  id: '1',
  name: 'Lote A-12',
  area: 400,
  price: 2_500_000,
  status: 'disponible',
  facing: 'Norte',
  section: 'A',
}

it('renders lot name', () => {
  render(<LotCard lot={lot} />)
  expect(screen.getByText('Lote A-12')).toBeInTheDocument()
})

it('formats price in MXN with comma separators', () => {
  render(<LotCard lot={lot} />)
  expect(screen.getByText(/2,500,000/)).toBeInTheDocument()
})

it('shows disponible badge', () => {
  render(<LotCard lot={lot} />)
  expect(screen.getByText(/disponible/i)).toBeInTheDocument()
})

it('shows vendido badge for sold lots', () => {
  render(<LotCard lot={{ ...lot, status: 'vendido' }} />)
  expect(screen.getByText(/vendido/i)).toBeInTheDocument()
})

it('does not show cotizar link for sold lots', () => {
  render(<LotCard lot={{ ...lot, status: 'vendido' }} />)
  expect(screen.queryByRole('link', { name: /cotizar/i })).not.toBeInTheDocument()
})
