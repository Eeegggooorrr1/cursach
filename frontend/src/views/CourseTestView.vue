<template>
  <section class="page-stack">
    <header class="page-header">
      <div class="page-header__copy">
        <p class="page-header__eyebrow">Тест</p>
        <h1 class="page-header__title">{{ test?.title || 'Тест' }}</h1>
        <p class="page-header__text">
          Ответьте на все вопросы и отправьте тест на проверку. После отправки можно сразу открыть разбор.
        </p>
      </div>

      <div class="page-header__actions">
        <RouterLink class="button button--secondary" :to="`/courses/${courseId}`">Назад к курсу</RouterLink>
      </div>
    </header>

    <div v-if="error" class="notice notice--error">{{ error }}</div>
    <div v-if="success" class="notice notice--success">{{ success }}</div>

    <div v-if="!test" class="empty-state">
      Тест не найден в текущей сессии. Вернитесь в курс и создайте его заново.
    </div>

    <template v-else>
      <section class="screen-surface screen-surface--dark">
        <div class="screen-surface__body screen-hero">
          <div class="screen-hero__copy">
            <span class="pill">Прохождение теста</span>
            <h2 class="screen-hero__title">{{ test.title }}</h2>
          </div>
          <div class="test-scoreboard">
            <span class="pill">вопросов {{ test.questions.length }}</span>
            <strong>{{ answeredCount }}</strong>
            <span>отвечено</span>
          </div>
        </div>
      </section>

      <section class="test-screen">
        <aside class="card test-rail">
          <div class="card__body test-rail__body">
            <button
              v-for="(question, index) in test.questions"
              :key="question.id"
              class="test-rail__step"
              :class="stepClass(index, question.id)"
              type="button"
              @click="currentQuestionIndex = index"
            >
              {{ index + 1 }}
            </button>
          </div>
        </aside>

        <article class="card test-question-card">
          <div class="card__body" v-if="currentQuestion">
            <div class="split test-question-card__head">
              <span class="pill">{{ currentQuestionIndex + 1 }} / {{ test.questions.length }}</span>
              <span class="pill">{{ answeredLabel(currentQuestion.id) }}</span>
            </div>

            <h2 class="test-question-card__title">{{ currentQuestion.prompt }}</h2>

            <div class="test-answer-list">
              <label
                v-for="option in currentQuestion.options"
                :key="option.id"
                class="test-answer-option"
                :class="{ 'test-answer-option--selected': isSelected(currentQuestion.id, option.id) }"
              >
                <span>{{ option.text }}</span>
                <input
                  :name="`question-${currentQuestion.id}`"
                  :value="option.id"
                  :type="currentQuestion.is_multiple_choice ? 'checkbox' : 'radio'"
                  :checked="isSelected(currentQuestion.id, option.id)"
                  @change="setAnswer(currentQuestion.id, option.id, currentQuestion.is_multiple_choice, $event)"
                />
              </label>
            </div>

            <div class="test-question-card__actions">
              <button class="button button--secondary" type="button" :disabled="currentQuestionIndex === 0" @click="goPrev">
                Назад
              </button>
              <button
                v-if="currentQuestionIndex < test.questions.length - 1"
                class="button button--secondary"
                type="button"
                @click="goNext"
              >
                Дальше
              </button>
              <button
                v-else
                class="button"
                type="button"
                :disabled="submitting || !allAnswered || Boolean(result)"
                @click="submit"
              >
                {{ submitting ? 'Отправляем...' : result ? 'Тест уже отправлен' : 'Отправить тест' }}
              </button>
            </div>
          </div>
        </article>
      </section>

      <article v-if="result" class="card result-card" @click="goToReview" role="button" tabindex="0">
        <div class="card__body split">
          <div>
            <h2 class="result-card__title">Результат</h2>
            <p class="result-card__hint">Нажмите, чтобы открыть разбор ответов.</p>
          </div>
          <div class="result-card__meta">
            <span class="pill" :class="result.status === 'finished' ? 'pill--success' : ''">{{ formatStatusLabel(result.status) }}</span>
            <strong>{{ formatPercent(result.correct_percentage) }}</strong>
          </div>
        </div>
      </article>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { api, ApiError } from '@/api/client'
import type { TestRead, TestSubmitResponse } from '@/api/types'
import { formatPercent, formatStatusLabel } from '@/utils/format'
import { clearActiveTest, readActiveTest, saveActiveTest } from '@/utils/testCache'

const props = defineProps<{ courseId: string; testId: string }>()
const router = useRouter()
const courseId = computed(() => Number(props.courseId))
const testId = computed(() => Number(props.testId))

const test = ref<TestRead | null>(null)
const selected = reactive<Record<number, number[]>>({})
const currentQuestionIndex = ref(0)
const submitting = ref(false)
const error = ref('')
const success = ref('')
const result = ref<TestSubmitResponse | null>(null)

const currentQuestion = computed(() => test.value?.questions[currentQuestionIndex.value] ?? null)
const answeredCount = computed(() => {
  if (!test.value) {
    return 0
  }
  return test.value.questions.filter((question) => selectedIds(question.id).length > 0).length
})
const allAnswered = computed(() => Boolean(test.value) && answeredCount.value === test.value!.questions.length)
const reviewLink = computed(() => ({
  name: 'course-test-review',
  params: { courseId: courseId.value, testId: testId.value },
}))

onMounted(() => {
  void loadTest()
})

async function loadTest() {
  const cached = readActiveTest(courseId.value, testId.value)
  if (cached) {
    test.value = cached
    return
  }

  try {
    const loaded = await api.getTest(courseId.value, testId.value)
    test.value = loaded
    saveActiveTest(loaded)
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось загрузить тест.'
  }
}

function answeredLabel(questionId: number) {
  return selectedIds(questionId).length > 0 ? 'ответ выбран' : 'ждет ответа'
}

function selectedIds(questionId: number) {
  return selected[questionId] ?? []
}

function isSelected(questionId: number, optionId: number) {
  return selectedIds(questionId).includes(optionId)
}

function stepClass(index: number, questionId: number) {
  return {
    'test-rail__step--active': currentQuestionIndex.value === index,
    'test-rail__step--done': selectedIds(questionId).length > 0 && currentQuestionIndex.value !== index,
  }
}

function setAnswer(questionId: number, optionId: number, isMultiple: boolean, event: Event) {
  if (!isMultiple) {
    selected[questionId] = [optionId]
    return
  }

  const checked = (event.target as HTMLInputElement).checked
  const current = new Set(selectedIds(questionId))
  if (checked) {
    current.add(optionId)
  } else {
    current.delete(optionId)
  }
  selected[questionId] = Array.from(current)
}

function goPrev() {
  currentQuestionIndex.value = Math.max(0, currentQuestionIndex.value - 1)
}

function goNext() {
  if (!test.value) {
    return
  }
  currentQuestionIndex.value = Math.min(test.value.questions.length - 1, currentQuestionIndex.value + 1)
}

function goToReview() {
  if (!result.value) {
    return
  }
  router.push(reviewLink.value)
}

async function submit() {
  if (submitting.value || result.value) {
    return
  }

  if (!test.value) {
    error.value = 'Тест не найден.'
    return
  }

  if (!allAnswered.value) {
    error.value = 'Нужно ответить на все вопросы.'
    return
  }

  const answers = test.value.questions.map((question) => ({
    question_id: question.id,
    selected_option_ids: selectedIds(question.id),
  }))

  submitting.value = true
  error.value = ''
  success.value = ''

  try {
    result.value = await api.submitTest(courseId.value, testId.value, { answers })
    clearActiveTest(courseId.value, testId.value)
    success.value = `Тест отправлен. Статус: ${formatStatusLabel(result.value.status)}.`
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось отправить тест.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.test-scoreboard {
  min-width: 180px;
  display: grid;
  gap: 8px;
  justify-items: end;
  text-align: right;
}

.test-scoreboard strong {
  font-size: 58px;
  line-height: 0.95;
}

.test-scoreboard span:last-child {
  color: rgba(255, 255, 255, 0.72);
}

.test-screen {
  display: grid;
  grid-template-columns: 94px minmax(0, 1fr);
  gap: 18px;
}

.test-rail__body {
  display: grid;
  gap: 10px;
}

.test-rail__step {
  width: 100%;
  height: 50px;
  border: 0;
  border-radius: 16px;
  color: var(--muted);
  background: var(--surface-muted);
  font-weight: 800;
}

.test-rail__step--active {
  color: white;
  background: var(--brand);
}

.test-rail__step--done {
  color: var(--brand-strong);
  background: rgba(17, 97, 73, 0.12);
}

.test-question-card__head {
  margin-bottom: 18px;
}

.test-question-card__title {
  margin: 0;
  font-size: clamp(24px, 3vw, 36px);
  line-height: 1.14;
}

.test-answer-list {
  display: grid;
  gap: 12px;
  margin-top: 24px;
}

.test-answer-option {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.76);
  transition:
    transform 180ms ease,
    border-color 180ms ease,
    background 180ms ease;
}

.test-answer-option--selected {
  border-color: rgba(17, 97, 73, 0.24);
  background: rgba(17, 97, 73, 0.08);
}

.test-answer-option:hover {
  transform: translateY(-2px);
}

.test-question-card__actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 24px;
}

.result-card {
  cursor: pointer;
}

.result-card__title {
  margin: 0;
  font-size: 24px;
}

.result-card__hint {
  margin: 8px 0 0;
  color: var(--muted);
}

.result-card__meta {
  display: grid;
  gap: 10px;
  justify-items: end;
}

.result-card__meta strong {
  font-size: 36px;
}

@media (max-width: 900px) {
  .test-screen {
    grid-template-columns: 1fr;
  }

  .test-rail__body {
    grid-template-columns: repeat(auto-fit, minmax(52px, 1fr));
  }
}

@media (max-width: 720px) {
  .test-scoreboard,
  .result-card__meta {
    justify-items: start;
    text-align: left;
  }
}
</style>
