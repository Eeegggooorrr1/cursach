import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import PaginationControls from './PaginationControls.vue'

describe('PaginationControls', () => {
  it('renders page summary and disables previous button on the first page', () => {
    const wrapper = mount(PaginationControls, {
      props: {
        total: 30,
        limit: 10,
        offset: 0,
        label: 'Page',
      },
    })

    const buttons = wrapper.findAll('button')

    expect(wrapper.text()).toContain('Page 1')
    expect(buttons[0].attributes('disabled')).toBeDefined()
    expect(buttons[1].attributes('disabled')).toBeUndefined()
  })

  it('renders total summary and emits navigation events', async () => {
    const wrapper = mount(PaginationControls, {
      props: {
        total: 30,
        limit: 10,
        offset: 10,
        label: 'Found',
        summary: 'total',
      },
    })

    const buttons = wrapper.findAll('button')

    expect(wrapper.text()).toContain('Found: 30')
    await buttons[0].trigger('click')
    await buttons[1].trigger('click')

    expect(wrapper.emitted('prev')).toHaveLength(1)
    expect(wrapper.emitted('next')).toHaveLength(1)
  })

  it('disables next button on the last page and both buttons while loading', () => {
    const lastPage = mount(PaginationControls, {
      props: {
        total: 20,
        limit: 10,
        offset: 10,
      },
    })
    expect(lastPage.findAll('button')[1].attributes('disabled')).toBeDefined()

    const loading = mount(PaginationControls, {
      props: {
        total: 20,
        limit: 10,
        offset: 0,
        loading: true,
      },
    })
    expect(loading.findAll('button').every((button) => button.attributes('disabled') !== undefined)).toBe(true)
  })
})
