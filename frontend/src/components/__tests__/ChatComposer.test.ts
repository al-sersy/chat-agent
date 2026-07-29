import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ChatComposer from '../ChatComposer.vue'

describe('ChatComposer', () => {
  it('emits send with trimmed text on Enter', async () => {
    const wrapper = mount(ChatComposer, { props: { loading: false } })
    await wrapper.find('textarea').setValue('hello')
    await wrapper.find('textarea').trigger('keydown', { key: 'Enter', shiftKey: false })
    expect(wrapper.emitted('send')?.[0]).toEqual(['hello'])
  })

  it('does not emit on Shift+Enter', async () => {
    const wrapper = mount(ChatComposer, { props: { loading: false } })
    await wrapper.find('textarea').setValue('hello')
    await wrapper.find('textarea').trigger('keydown', { key: 'Enter', shiftKey: true })
    expect(wrapper.emitted('send')).toBeFalsy()
  })

  it('clears text on Escape', async () => {
    const wrapper = mount(ChatComposer, { props: { loading: false } })
    await wrapper.find('textarea').setValue('hello')
    await wrapper.find('textarea').trigger('keydown', { key: 'Escape' })
    const el = wrapper.find('textarea').element as HTMLTextAreaElement
    expect(el.value).toBe('')
  })

  it('disables textarea and button when loading', () => {
    const wrapper = mount(ChatComposer, { props: { loading: true } })
    expect((wrapper.find('textarea').element as HTMLTextAreaElement).disabled).toBe(true)
  })

  it('does not emit when message is whitespace', async () => {
    const wrapper = mount(ChatComposer, { props: { loading: false } })
    await wrapper.find('textarea').setValue('   ')
    await wrapper.find('textarea').trigger('keydown', { key: 'Enter', shiftKey: false })
    expect(wrapper.emitted('send')).toBeFalsy()
  })
})
