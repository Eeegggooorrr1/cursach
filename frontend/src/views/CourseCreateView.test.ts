import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import CourseCreateView from './CourseCreateView.vue'
import {
  COURSE_PROMPT_MAX_LENGTH,
  COURSE_TEXT_MAX_LENGTH,
  COURSE_TITLE_MAX_LENGTH,
  COURSE_TOPIC_MAX_LENGTH,
  COURSE_TOPICS_MAX_COUNT,
} from '@/constants/validation'

vi.mock('vue-router', () => ({
  RouterLink: {
    template: '<a><slot /></a>',
  },
  useRouter: () => ({
    replace: vi.fn(),
  }),
}))

describe('CourseCreateView validation hints', () => {
  it('passes backend text limits to editable fields', () => {
    const wrapper = mount(CourseCreateView)

    expect(wrapper.find('#title').attributes('maxlength')).toBe(String(COURSE_TITLE_MAX_LENGTH))
    expect(wrapper.find('#comment').attributes('maxlength')).toBe(String(COURSE_TEXT_MAX_LENGTH))
    expect(wrapper.find('#prompt').attributes('maxlength')).toBe(String(COURSE_PROMPT_MAX_LENGTH))
    expect(wrapper.find('#topicInput').attributes('maxlength')).toBe(String(COURSE_TOPIC_MAX_LENGTH))
  })

  it('does not allow adding more topics than backend accepts', async () => {
    const wrapper = mount(CourseCreateView)
    const input = wrapper.find<HTMLInputElement>('#topicInput')
    const addButton = wrapper.find('.toolbar button')

    for (let index = 0; index < COURSE_TOPICS_MAX_COUNT; index += 1) {
      await input.setValue(`Topic ${index}`)
      await addButton.trigger('click')
    }

    expect(wrapper.findAll('.chip')).toHaveLength(COURSE_TOPICS_MAX_COUNT)
    expect(addButton.attributes('disabled')).toBeDefined()
  })
})
