import { useRouter } from 'vue-router'
import { ENDPOINTS } from '@/constants/endpoints'

export function useSession() {
    const router = useRouter()

    async function createSession() {
      try {
        const response = await fetch(ENDPOINTS.sessions.create, {
          method: 'POST'
        })
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data = await response.json()
        await router.push(`/chat/${data.session_id}`)
      } catch (error) {
        console.error('Failed to create session:', error)
      }
    }

    return { createSession }
}
