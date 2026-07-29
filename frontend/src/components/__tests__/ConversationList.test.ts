import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ConversationList from '../ConversationList.vue'

const toolCall = {
  type: 'tool_call', id: '2', timestamp: '2026-01-01T00:00:01Z',
  tool_call_id: 'tc1', tool_name: 'read_file', arguments: {},
}
const toolResult = {
  type: 'tool_result', id: '3', timestamp: '2026-01-01T00:00:02Z',
  tool_call_id: 'tc1', content: 'file contents', truncated: false,
}
const userMsg = {
  type: 'user_message', id: '1', timestamp: '2026-01-01T00:00:00Z', content: 'hi',
}

describe('ConversationList', () => {
  it('shows ThinkingItem when loading', () => {
    const wrapper = mount(ConversationList, { props: { items: [], loading: true } })
    expect(wrapper.findComponent({ name: 'ThinkingItem' }).exists()).toBe(true)
  })

  it('hides empty state when loading', () => {
    const wrapper = mount(ConversationList, { props: { items: [], loading: true } })
    expect(wrapper.find('.empty').exists()).toBe(false)
  })

  it('shows empty state when idle and no items', () => {
    const wrapper = mount(ConversationList, { props: { items: [], loading: false } })
    expect(wrapper.find('.empty').exists()).toBe(true)
  })

  it('renders ToolCallItem as pending when no result yet', () => {
    const wrapper = mount(ConversationList, { props: { items: [toolCall as any], loading: false } })
    const tc = wrapper.findComponent({ name: 'ToolCallItem' })
    expect(tc.exists()).toBe(true)
    expect(tc.props('status')).toBe('pending')
  })

  it('marks ToolCallItem success when result present', () => {
    const wrapper = mount(ConversationList, {
      props: { items: [toolCall as any, toolResult as any], loading: false },
    })
    const tc = wrapper.findComponent({ name: 'ToolCallItem' })
    expect(tc.props('status')).toBe('success')
  })
})
