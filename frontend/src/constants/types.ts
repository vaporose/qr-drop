export type MessageSender = 'self' | 'other' | 'system'

export interface ChatMessage {
  text: string
  sender: MessageSender
  identity?: string
}
