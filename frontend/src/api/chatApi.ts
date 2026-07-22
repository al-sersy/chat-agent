import type { ConversationItem } from '../models/conversation'

export async function sendMessage(message: string): Promise<ConversationItem[]> {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  })

  if (!response.ok) {
    throw new Error(`Request failed: HTTP ${response.status} ${response.statusText}`)
  }

  const data: { items: ConversationItem[] } = await response.json()
  return data.items
}
