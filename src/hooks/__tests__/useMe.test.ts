import { renderHook, act } from '@testing-library/react'
import { useMe } from '../useMe'

// Mock the API
jest.mock('@/lib/api', () => ({
  apiGet: jest.fn(),
}))

import { apiGet } from '@/lib/api'

describe('useMe Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('returns loading state initially', () => {
    ;(apiGet as jest.Mock).mockResolvedValue({ id: 1, email: 'test@example.com' })
    
    const { result } = renderHook(() => useMe())
    
    expect(result.current.loading).toBe(true)
    expect(result.current.user).toBeNull()
  })

  it('fetches and returns user data', async () => {
    const mockUser = { id: 1, email: 'test@example.com' }
    ;(apiGet as jest.Mock).mockResolvedValue(mockUser)
    
    const { result, waitForNextUpdate } = renderHook(() => useMe())
    
    await waitForNextUpdate()
    
    expect(result.current.loading).toBe(false)
    expect(result.current.user).toEqual(mockUser)
  })

  it('handles API errors gracefully', async () => {
    ;(apiGet as jest.Mock).mockRejectedValue(new Error('API Error'))
    
    const { result, waitForNextUpdate } = renderHook(() => useMe())
    
    await waitForNextUpdate()
    
    expect(result.current.loading).toBe(false)
    expect(result.current.user).toBeNull()
    expect(result.current.error).toBeDefined()
  })
})
