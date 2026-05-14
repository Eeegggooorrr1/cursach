<template>
  <section class="card">
    <div class="card__body">
      <h1 class="hero__title">Страница не найдена</h1>
      <p class="hero__text">Похоже, такого адреса здесь нет.</p>
      <div class="actions">
        <RouterLink class="button" to="/courses">Перейти к курсам</RouterLink>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>
