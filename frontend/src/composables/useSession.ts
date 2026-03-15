import { useRouter } from 'vue-router'
import { CONFIG } from '@/constants/config'

export function useSession() {
    const router = useRouter()

    async function createSession() {
      try {
        const response = await fetch(`${CONFIG.backendUrl}/create-session`, {
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
