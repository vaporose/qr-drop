import { describe, it, expect, vi, beforeEach } from 'vitest'
import { withSetup } from '../utils/withSetup'
import { useSession } from '@/composables/useSession'

// Mock vue-router since useRouter() is called inside the composable
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn()
  })
}))

// Mock fetch since the composable calls the backend
const mockFetch = vi.fn()
vi.stubGlobal('fetch', mockFetch)

describe('useSession', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  it('navigates to chat on successful session creation', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ session_id: 'abc123' })
    })

    const { createSession } = withSetup(useSession)
    await createSession()

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/sessions'),
      expect.objectContaining({ method: 'POST' })
    )
  })

  it('logs error on failed session creation', async () => {
    mockFetch.mockResolvedValueOnce({ ok: false, status: 500 })
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    const { createSession } = withSetup(useSession)
    await createSession()

    expect(consoleSpy).toHaveBeenCalled()
    consoleSpy.mockRestore()
  })
})
