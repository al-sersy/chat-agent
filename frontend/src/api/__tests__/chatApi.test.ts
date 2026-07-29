import { describe, it, expect, vi } from 'vitest'
import { streamMessage } from '../chatApi'

function makeStream(chunks: string[]): ReadableStream {
  return new ReadableStream({
    start(controller) {
      for (const chunk of chunks) {
        controller.enqueue(new TextEncoder().encode(chunk))
      }
      controller.close()
    },
  })
}

describe('streamMessage', () => {
  it('yields parsed items and stops on [DONE]', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      body: makeStream([
        'data: {"type":"user_message","id":"1","timestamp":"2026-01-01T00:00:00Z","content":"hi"}\n\n',
        'data: [DONE]\n\n',
      ]),
    }))
    const items = []
    for await (const item of streamMessage('hi')) items.push(item)
    expect(items).toHaveLength(1)
    expect(items[0].type).toBe('user_message')
    vi.unstubAllGlobals()
  })

  it('handles multiple items in one chunk', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      body: makeStream([
        'data: {"type":"user_message","id":"1","timestamp":"2026-01-01T00:00:00Z","content":"hi"}\n\ndata: [DONE]\n\n',
      ]),
    }))
    const items = []
    for await (const item of streamMessage('hi')) items.push(item)
    expect(items).toHaveLength(1)
    vi.unstubAllGlobals()
  })

  it('throws on non-ok response', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
    }))
    await expect(async () => {
      for await (const _ of streamMessage('test')) {}
    }).rejects.toThrow('HTTP 500')
    vi.unstubAllGlobals()
  })
})
