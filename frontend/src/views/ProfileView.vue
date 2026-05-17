<template>
  <section class="page-stack">
    <header class="page-header">
      <div class="page-header__copy">
        <p class="page-header__eyebrow">Профиль</p>
        <h1 class="page-header__title">{{ profile?.username || 'Профиль' }}</h1>
        <p class="page-header__text">Здесь можно обновить описание профиля и выйти из аккаунта.</p>
      </div>

      <div class="page-header__actions">
        <button class="button button--secondary" type="button" @click="logout">Выйти</button>
      </div>
    </header>

    <div v-if="error" class="notice notice--error">{{ error }}</div>
    <div v-if="success" class="notice notice--success">{{ success }}</div>
    <div v-if="loading && !profile" class="notice">Загружаем профиль...</div>

    <section v-if="profile" class="profile-grid">
      <article class="card card--muted">
        <div class="card__body profile-summary">
          <span class="pill">{{ profile.role }}</span>
          <h2 class="profile-summary__name">{{ profile.username }}</h2>
          <p class="profile-summary__email">{{ profile.email }}</p>
        </div>
      </article>

      <article class="card">
        <div class="card__body">
          <form class="form-grid" @submit.prevent="submit">
            <div class="form-grid form-grid--2">
              <div class="field">
                <label class="field__label" for="username">Имя пользователя</label>
                <input id="username" class="input" type="text" :value="profile.username" disabled />
              </div>

              <div class="field">
                <label class="field__label" for="email">Email</label>
                <input id="email" class="input" type="email" :value="profile.email" disabled />
              </div>
            </div>

            <div class="field">
              <label class="field__label" for="profileDescription">Описание профиля</label>
              <textarea
                id="profileDescription"
                v-model="form.profile_description"
                class="textarea"
                rows="6"
                :maxlength="PROFILE_DESCRIPTION_MAX_LENGTH"
                placeholder="Расскажите коротко о себе или своих учебных целях"
              ></textarea>
            </div>

            <div class="actions">
              <button class="button" type="submit" :disabled="saving">
                {{ saving ? 'Сохраняем...' : 'Сохранить профиль' }}
              </button>
            </div>
          </form>
        </div>
      </article>
    </section>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, ApiError } from '@/api/client'
import type { UserProfile } from '@/api/types'
import { PROFILE_DESCRIPTION_MAX_LENGTH } from '@/constants/validation'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const profile = ref<UserProfile | null>(null)
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')
const form = reactive({
  profile_description: '',
})

async function loadProfile() {
  loading.value = true
  error.value = ''
  try {
    profile.value = await api.getProfile()
    form.profile_description = profile.value.profile_description || ''
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось загрузить профиль.'
  } finally {
    loading.value = false
  }
}

async function submit() {
  saving.value = true
  error.value = ''
  success.value = ''

  try {
    profile.value = await api.updateProfile({
      profile_description: form.profile_description || null,
    })
    form.profile_description = profile.value.profile_description || ''
    success.value = 'Профиль обновлен.'
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось обновить профиль.'
  } finally {
    saving.value = false
  }
}

async function logout() {
  await auth.logout()
  await router.push({ name: 'login' })
}

onMounted(loadProfile)
</script>

<style scoped>
.profile-grid {
  display: grid;
  grid-template-columns: 0.7fr 1.3fr;
  gap: 18px;
}

.profile-summary {
  display: grid;
  gap: 12px;
  align-content: start;
}

.profile-summary__name {
  margin: 0;
  font-size: 34px;
}

.profile-summary__email {
  margin: 0;
  color: var(--muted);
}

@media (max-width: 1100px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}
</style>
