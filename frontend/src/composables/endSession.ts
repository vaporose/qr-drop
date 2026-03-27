import { useRouter } from 'vue-router'
import { ENDPOINTS } from '@/constants/endpoints'

export function useEndSession() {
    const router = useRouter()

    async function endSession(sessionId: string) {
      try {
        const response = await fetch(ENDPOINTS.sessions.end(sessionId), { method: 'DELETE' })
        if (!response.ok) {
          console.error('Failed to end session:', response.status)
          return
        }
        await router.push('/')
      } catch (error) {
        console.error('Error ending session:', error)
      }
    }

    return { endSession }
}
