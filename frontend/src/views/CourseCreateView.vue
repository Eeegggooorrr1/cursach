<template>
  <section class="page-stack">
    <header class="page-header">
      <div class="page-header__copy">
        <p class="page-header__eyebrow">Новый курс</p>
        <h1 class="page-header__title">Собрать основу курса</h1>
        <p class="page-header__text">
          Сначала задаем тему, описание и направления, а структуру курса дальше соберет backend.
        </p>
      </div>

      <div class="page-header__actions">
        <RouterLink class="button button--secondary" to="/courses">Отмена</RouterLink>
      </div>
    </header>

    <div v-if="error" class="notice notice--error">{{ error }}</div>
    <div v-if="success" class="notice notice--success">{{ success }}</div>

    <article class="card">
      <div class="card__body">
        <form class="form-grid" @submit.prevent="submit">
          <div class="field">
            <label class="field__label" for="title">Название</label>
            <input id="title" v-model.trim="form.title" class="input" type="text" required />
          </div>

          <div class="field">
            <label class="field__label" for="comment">Описание курса</label>
            <textarea
              id="comment"
              v-model.trim="form.comment"
              class="textarea"
              placeholder="Что это за курс и для кого он нужен"
            ></textarea>
          </div>

          <div class="field">
            <label class="field__label" for="prompt">Указание для генерации</label>
            <textarea
              id="prompt"
              v-model.trim="form.prompt"
              class="textarea"
              placeholder="Например: больше практики, меньше определений"
            ></textarea>
          </div>

          <div class="form-grid form-grid--2">
            <div class="field">
              <label class="field__label" for="initialDifficulty">Стартовая сложность</label>
              <select id="initialDifficulty" v-model.number="form.initial_difficulty" class="select">
                <option :value="0">Базовая</option>
                <option :value="1">Средняя</option>
                <option :value="2">Продвинутая</option>
              </select>
            </div>

            <label class="checkbox-field">
              <input v-model="form.is_public" type="checkbox" />
              <span>
                <strong>Публичный курс</strong>
                <small>Появится в каталоге, и его смогут добавить другие пользователи.</small>
              </span>
            </label>
          </div>

          <div class="field">
            <label class="field__label" for="topicInput">Темы курса</label>
            <div class="toolbar">
              <input
                id="topicInput"
                v-model.trim="topicInput"
                class="input"
                type="text"
                placeholder="Например: SQLAlchemy"
                @keydown.enter.prevent="addTopic"
              />
              <button class="button button--secondary" type="button" @click="addTopic">Добавить</button>
            </div>
            <div v-if="topics.length" class="chips">
              <span v-for="topic in topics" :key="topic" class="chip">
                {{ topic }}
                <button class="chip__remove" type="button" @click="removeTopic(topic)">x</button>
              </span>
            </div>
          </div>

          <div class="actions">
            <button class="button" type="submit" :disabled="loading || topics.length === 0">
              {{ loading ? 'Создаем...' : 'Создать курс' }}
            </button>
          </div>
        </form>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { api, ApiError } from '@/api/client'
import type { DifficultyLevel } from '@/api/types'

const router = useRouter()

const loading = ref(false)
const error = ref('')
const success = ref('')
const topicInput = ref('')
const topics = ref<string[]>([])
const form = reactive({
  title: '',
  comment: '',
  prompt: '',
  initial_difficulty: 0 as DifficultyLevel,
  is_public: false,
})

const payload = computed(() => ({
  title: form.title,
  comment: form.comment ? form.comment : null,
  prompt: form.prompt ? form.prompt : null,
  topics: topics.value,
  initial_difficulty: form.initial_difficulty,
  is_public: form.is_public,
}))

function addTopic() {
  const value = topicInput.value.trim()
  if (!value) {
    return
  }

  const normalized = value.toLowerCase()
  if (!topics.value.some((topic) => topic.toLowerCase() === normalized)) {
    topics.value = [...topics.value, value]
  }
  topicInput.value = ''
}

function removeTopic(topic: string) {
  topics.value = topics.value.filter((item) => item !== topic)
}

async function submit() {
  loading.value = true
  error.value = ''
  success.value = ''

  try {
    const course = await api.createCourse(payload.value)
    success.value = 'Курс создан.'
    await router.replace({ name: 'course-detail', params: { courseId: course.id } })
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось создать курс.'
  } finally {
    loading.value = false
  }
}
</script>
