<template>
  <section class="auth-screen">
    <div class="hero auth-screen__hero">
      <h1 class="hero__title">Регистрация</h1>
    </div>

    <div class="card auth-screen__card">
      <div class="card__body">
        <h2 class="section-title">Новый аккаунт</h2>

        <form class="form-grid" @submit.prevent="submit">
          <div class="field">
            <label class="field__label" for="username">Имя пользователя</label>
            <input id="username" v-model.trim="form.username" class="input" type="text" autocomplete="username" required :minlength="USERNAME_MIN_LENGTH" :maxlength="USERNAME_MAX_LENGTH" />
          </div>

          <div class="field">
            <label class="field__label" for="email">Email</label>
            <input id="email" v-model.trim="form.email" class="input" type="email" autocomplete="email" required />
          </div>

          <div class="field">
            <label class="field__label" for="password">Пароль</label>
            <input id="password" v-model="form.password" class="input" type="password" autocomplete="new-password" required :minlength="AUTH_PASSWORD_MIN_LENGTH" :maxlength="AUTH_PASSWORD_MAX_LENGTH" />
          </div>

          <div class="field">
            <label class="field__label" for="profileDescription">Описание профиля</label>
            <textarea
              id="profileDescription"
              v-model="form.profile_description"
              class="textarea"
              rows="4"
              :maxlength="PROFILE_DESCRIPTION_MAX_LENGTH"
              placeholder="Можно оставить пустым"
            ></textarea>
          </div>

          <div v-if="error" class="notice notice--error">{{ error }}</div>
          <div v-if="success" class="notice notice--success">{{ success }}</div>

          <div class="actions">
            <button class="button" type="submit" :disabled="loading">
              {{ loading ? 'Создаем...' : 'Создать аккаунт' }}
            </button>
            <RouterLink class="button button--secondary" to="/login">У меня уже есть аккаунт</RouterLink>
          </div>
        </form>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { ApiError } from '@/api/client'
import {
  AUTH_PASSWORD_MAX_LENGTH,
  AUTH_PASSWORD_MIN_LENGTH,
  PROFILE_DESCRIPTION_MAX_LENGTH,
  USERNAME_MAX_LENGTH,
  USERNAME_MIN_LENGTH,
} from '@/constants/validation'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const loading = ref(false)
const error = ref('')
const success = ref('')
const form = reactive({
  username: '',
  email: '',
  password: '',
  profile_description: '',
})

async function submit() {
  loading.value = true
  error.value = ''
  success.value = ''

  try {
    await auth.register(form)
    success.value = 'Аккаунт создан.'
    const next = typeof route.query.next === 'string' ? route.query.next : '/courses'
    await router.replace(next)
  } catch (e) {
    if (e instanceof ApiError) {
      error.value = e.message
    } else {
      error.value = 'Не удалось зарегистрироваться.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-screen {
  width: min(100%, 760px);
  min-height: calc(100vh - 84px);
  margin: 0 auto;
  display: grid;
  align-content: center;
  gap: 18px;
}

.auth-screen__hero {
  justify-items: center;
  text-align: center;
}

.auth-screen__card {
  width: 100%;
}

@media (max-width: 900px) {
  .auth-screen {
    min-height: auto;
  }
}
</style>
