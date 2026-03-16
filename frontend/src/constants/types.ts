export type MessageSender = 'self' | 'other' | 'system'

export interface ChatMessage {
  content: string
  created_at?: string
  sender_type: MessageSender
  identity?: {
    display_name: string
    unique_identifier: string
  }
}
