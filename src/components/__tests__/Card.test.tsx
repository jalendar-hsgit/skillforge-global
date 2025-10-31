import { render, screen } from '@testing-library/react'
import Card from '../Card'

describe('Card Component', () => {
  it('renders card with title and children', () => {
    render(
      <Card title="Test Card">
        <p>Card Content</p>
      </Card>
    )
    
    expect(screen.getByText('Test Card')).toBeInTheDocument()
    expect(screen.getByText('Card Content')).toBeInTheDocument()
  })

  it('renders without title when not provided', () => {
    render(
      <Card>
        <p>Content Only</p>
      </Card>
    )
    
    expect(screen.getByText('Content Only')).toBeInTheDocument()
  })

  it('applies hover effect classes', () => {
    const { container } = render(<Card>Hover Card</Card>)
    const card = container.firstChild
    expect(card).toHaveClass('hover:shadow-2xl')
  })
})
