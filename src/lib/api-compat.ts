// Compatibility layer for apiCall - maps to apiGet for GET requests
import { apiGet, apiPost } from '@/lib/api'

export async function apiCall(path: string, options?: { method?: string; [key: string]: any }) {
  const method = options?.method || 'GET'
  
  if (method === 'GET') {
    return await apiGet(path)
  } else if (method === 'POST') {
    const { method, ...data } = options || {}
    return await apiPost(path, data)
  } else {
    throw new Error(`Unsupported method: ${method}`)
  }
}
