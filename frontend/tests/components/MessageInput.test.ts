import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MessageInput from '@/components/MessageInput.vue'

describe('MessageInput', () => {
  it('emits send event with input value when button is clicked', async () => {
    const wrapper = mount(MessageInput)
    await wrapper.find('input').setValue('hello')
    await wrapper.find('button').trigger('click')

    expect(wrapper.emitted('send')).toBeTruthy()
    expect(wrapper.emitted('send')![0]).toEqual(['hello'])
  })

  it('emits send event when enter is pressed', async () => {
    const wrapper = mount(MessageInput)
    await wrapper.find('input').setValue('hello')
    await wrapper.find('input').trigger('keyup.enter')

    expect(wrapper.emitted('send')).toBeTruthy()
    expect(wrapper.emitted('send')![0]).toEqual(['hello'])
  })

  it('clears input after sending', async () => {
    const wrapper = mount(MessageInput)
    await wrapper.find('input').setValue('hello')
    await wrapper.find('button').trigger('click')

    expect((wrapper.find('input').element as HTMLInputElement).value).toBe('')
  })

  it('does not emit send event when input is empty', async () => {
    const wrapper = mount(MessageInput)
    await wrapper.find('button').trigger('click')

    expect(wrapper.emitted('send')).toBeFalsy()
  })

  it('does not emit send event when input is only whitespace', async () => {
    const wrapper = mount(MessageInput)
    await wrapper.find('input').setValue('   ')
    await wrapper.find('button').trigger('click')

    expect(wrapper.emitted('send')).toBeFalsy()
  })
})
