import { useRouter } from 'vue-router'
import { ENDPOINTS } from '@/constants/endpoints'

export function useSession() {
    const router = useRouter()

    async function createSession() {
      const response = await fetch(ENDPOINTS.sessions.create, { method: 'POST' })
      if (!response.ok) {
        console.error('Failed to create session:', response.status)
        return
      }
      const data = await response.json()
      await router.push(`/chat/${data.session_id}`)
    }

    return { createSession }
}
