<template>
  <section class="page-stack">
    <header class="page-header">
      <div class="page-header__copy">
        <p class="page-header__eyebrow">Разбор теста</p>
        <h1 class="page-header__title">{{ review?.test.title || 'Разбор теста' }}</h1>
        <p class="page-header__text">
          Здесь собраны ваши ответы, правильные варианты и итог по каждому вопросу.
        </p>
      </div>

      <div class="page-header__actions">
        <RouterLink class="button button--secondary" :to="`/courses/${courseId}`">К курсу</RouterLink>
      </div>
    </header>

    <div v-if="error" class="notice notice--error">{{ error }}</div>
    <div v-if="loading" class="notice">Загружаем разбор...</div>

    <template v-if="review">
      <section class="screen-surface screen-surface--dark">
        <div class="screen-surface__body screen-hero">
          <div class="screen-hero__copy">
            <span class="pill">Разбор</span>
            <h2 class="screen-hero__title">{{ review.test.title }}</h2>
          </div>
          <div class="review-scoreboard">
            <span class="pill">ответов {{ review.attempts.length }}</span>
            <strong>{{ correctCount }}</strong>
            <span>верных</span>
          </div>
        </div>
      </section>

      <section class="review-grid">
        <aside class="card review-rail">
          <div class="card__body review-rail__body">
            <button
              v-for="(question, index) in review.test.questions"
              :key="question.id"
              class="review-rail__step"
              :class="attemptByQuestion(question.id)?.is_correct ? 'review-rail__step--correct' : 'review-rail__step--wrong'"
              type="button"
              @click="currentQuestionIndex = index"
            >
              {{ index + 1 }}
            </button>
          </div>
        </aside>

        <article v-if="currentQuestion" class="card review-card">
          <div class="card__body">
            <div class="split review-card__head">
              <span class="pill">{{ currentQuestionIndex + 1 }} / {{ review.test.questions.length }}</span>
              <span class="pill" :class="attemptTone(currentQuestion.id)">{{ attemptLabel(currentQuestion.id) }}</span>
            </div>

            <h2 class="review-card__title">{{ currentQuestion.prompt }}</h2>

            <div class="review-options">
              <div
                v-for="option in currentQuestion.options"
                :key="option.id"
                class="review-option"
                :class="optionClass(currentQuestion.id, option.id)"
              >
                <div class="review-option__head">
                  <span>{{ option.text }}</span>
                  <span v-if="option.is_correct" class="pill pill--success">верный вариант</span>
                </div>
              </div>
            </div>
          </div>
        </article>
      </section>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { api, ApiError } from '@/api/client'
import type { TestReviewResponse } from '@/api/types'

const props = defineProps<{ courseId: string; testId: string }>()
const courseId = computed(() => Number(props.courseId))
const testId = computed(() => Number(props.testId))

const review = ref<TestReviewResponse | null>(null)
const loading = ref(false)
const error = ref('')
const currentQuestionIndex = ref(0)

const currentQuestion = computed(() => review.value?.test.questions[currentQuestionIndex.value] ?? null)
const correctCount = computed(() => review.value?.attempts.filter((item) => item.is_correct).length ?? 0)

function attemptByQuestion(questionId: number) {
  return review.value?.attempts.find((item) => item.question_id === questionId) ?? null
}

function attemptLabel(questionId: number) {
  const attempt = attemptByQuestion(questionId)
  if (!attempt) {
    return 'без ответа'
  }
  return attempt.is_correct ? 'верно' : 'ошибка'
}

function attemptTone(questionId: number) {
  const attempt = attemptByQuestion(questionId)
  if (!attempt) {
    return 'pill--warning'
  }
  return attempt.is_correct ? 'pill--success' : 'pill--danger'
}

function optionClass(questionId: number, optionId: number) {
  const attempt = attemptByQuestion(questionId)
  const isSelected = selectedOptionIds(questionId).includes(optionId)
  const isCorrect = review.value?.test.questions
    .find((question) => question.id === questionId)
    ?.options.find((option) => option.id === optionId)?.is_correct

  return {
    'review-option--selected': isSelected,
    'review-option--correct': Boolean(isCorrect),
    'review-option--incorrect': Boolean(isSelected && !isCorrect),
  }
}

function selectedOptionIds(questionId: number) {
  const attempt = attemptByQuestion(questionId)
  if (!attempt) {
    return []
  }
  return attempt.selected_option_ids
}

async function loadReview() {
  loading.value = true
  error.value = ''
  try {
    review.value = await api.getTestReview(courseId.value, testId.value)
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось загрузить разбор.'
  } finally {
    loading.value = false
  }
}

onMounted(loadReview)
</script>

<style scoped>
.review-scoreboard {
  min-width: 180px;
  display: grid;
  gap: 8px;
  justify-items: end;
  text-align: right;
}

.review-scoreboard strong {
  font-size: 58px;
  line-height: 0.95;
}

.review-scoreboard span:last-child {
  color: rgba(255, 255, 255, 0.72);
}

.review-grid {
  display: grid;
  grid-template-columns: 94px minmax(0, 1fr);
  gap: 18px;
}

.review-rail__body {
  display: grid;
  gap: 10px;
}

.review-rail__step {
  width: 100%;
  height: 50px;
  border: 0;
  border-radius: 16px;
  color: white;
  font-weight: 800;
}

.review-rail__step--correct {
  background: var(--brand);
}

.review-rail__step--wrong {
  background: var(--danger);
}

.review-card__head {
  margin-bottom: 18px;
}

.review-card__title {
  margin: 0;
  font-size: clamp(24px, 3vw, 36px);
  line-height: 1.14;
}

.review-options {
  display: grid;
  gap: 12px;
  margin-top: 24px;
}

.review-option {
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.76);
}

.review-option--selected {
  border-color: rgba(17, 97, 73, 0.24);
}

.review-option--correct {
  background: rgba(17, 97, 73, 0.08);
}

.review-option--incorrect {
  background: rgba(194, 65, 45, 0.08);
}

.review-option__head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

@media (max-width: 900px) {
  .review-grid {
    grid-template-columns: 1fr;
  }

  .review-rail__body {
    grid-template-columns: repeat(auto-fit, minmax(52px, 1fr));
  }
}

@media (max-width: 720px) {
  .review-scoreboard {
    justify-items: start;
    text-align: left;
  }
}
</style>
