
import { CONFIG } from './config'

export const ENDPOINTS = {
  sessions: {
    create: `${CONFIG.backendUrl}/sessions`,
    end: (sessionId: string) => `${CONFIG.backendUrl}/sessions/${sessionId}`,
  },
  connections: {
    chat: (sessionId: string) => `${CONFIG.backendWsUrl}/ws/sessions/${sessionId}`,
  }
} as const
