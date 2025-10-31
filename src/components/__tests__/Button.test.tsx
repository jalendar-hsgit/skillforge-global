import { render, screen } from '@testing-library/react'
import Button from '../Button'

describe('Button Component', () => {
  it('renders button with text', () => {
    render(<Button>Click Me</Button>)
    expect(screen.getByText('Click Me')).toBeInTheDocument()
  })

  it('calls onClick handler when clicked', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click</Button>)
    
    screen.getByText('Click').click()
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('applies primary variant styles', () => {
    render(<Button variant="primary">Primary</Button>)
    const button = screen.getByText('Primary')
    expect(button).toHaveClass('bg-gradient-to-r')
  })

  it('disables button when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>)
    const button = screen.getByText('Disabled')
    expect(button).toBeDisabled()
  })
})
