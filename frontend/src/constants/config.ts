
const hostIp: string = import.meta.env.VITE_HOST_IP
const protocol: string = import.meta.env.VITE_URL_PROTOCOL

export const CONFIG = {
  backendUrl: `${protocol}://${hostIp}:8000`,
  backendWsUrl: `${protocol === 'https' ? 'wss' : 'ws'}://${hostIp}:8000/ws`,
  frontendUrl: `${protocol}://${hostIp}:5173`,

} as const
