import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MessageList from '@/components/MessageList.vue'
import type { ChatMessage } from '@/constants/types'

const selfMessage: ChatMessage = {
  content: 'hello',
  sender_type: 'self',
  identity: { display_name: 'Chrome on Windows', unique_identifier: '123' }
}

const otherMessage: ChatMessage = {
  content: 'hi back',
  sender_type: 'other',
  identity: { display_name: 'Firefox on Mac', unique_identifier: '456' }
}

const systemMessage: ChatMessage = {
  content: 'Connected',
  sender_type: 'system'
}

describe('MessageList', () => {
  it('renders message content', () => {
    const wrapper = mount(MessageList, { props: { messages: [selfMessage] } })
    expect(wrapper.text()).toContain('hello')
  })

  it('applies correct class for self message', () => {
    const wrapper = mount(MessageList, { props: { messages: [selfMessage] } })
    expect(wrapper.find('.message-self').exists()).toBe(true)
  })

  it('applies correct class for other message', () => {
    const wrapper = mount(MessageList, { props: { messages: [otherMessage] } })
    expect(wrapper.find('.message-other').exists()).toBe(true)
  })

  it('applies correct class for system message', () => {
    const wrapper = mount(MessageList, { props: { messages: [systemMessage] } })
    expect(wrapper.find('.message-system').exists()).toBe(true)
  })

  it('renders identity for non-system messages', () => {
    const wrapper = mount(MessageList, { props: { messages: [selfMessage] } })
    expect(wrapper.find('.message-identity').text()).toBe('Chrome on Windows')
  })

  it('does not render message-meta for system messages', () => {
    const wrapper = mount(MessageList, { props: { messages: [systemMessage] } })
    expect(wrapper.find('.message-meta').exists()).toBe(false)
  })

  it('renders multiple messages', () => {
    const wrapper = mount(MessageList, {
      props: { messages: [selfMessage, otherMessage, systemMessage] }
    })
    expect(wrapper.findAll('.message-text')).toHaveLength(3)
  })
})
