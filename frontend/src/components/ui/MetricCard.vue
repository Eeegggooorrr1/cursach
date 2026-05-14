<template>
  <article class="metric-card">
    <span class="metric-card__label">{{ label }}</span>
    <strong class="metric-card__value">{{ value }}</strong>
    <p v-if="hint" class="metric-card__hint">{{ hint }}</p>
    <div class="metric-card__line" :class="`metric-card__line--${tone}`"></div>
  </article>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    label: string
    value: string | number
    hint?: string
    tone?: 'green' | 'blue' | 'amber' | 'red'
  }>(),
  {
    hint: '',
    tone: 'green',
  },
)
</script>

<style scoped>
.metric-card {
  position: relative;
  overflow: hidden;
  min-height: 150px;
  border: 1px solid rgba(255, 255, 255, 0.82);
  border-radius: 26px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: var(--shadow-soft);
}

.metric-card__label {
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
}

.metric-card__value {
  display: block;
  margin-top: 8px;
  font-size: 38px;
  line-height: 1;
}

.metric-card__hint {
  margin: 10px 0 0;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.5;
}

.metric-card__line {
  position: absolute;
  left: 18px;
  right: 18px;
  bottom: 16px;
  height: 8px;
  border-radius: 999px;
}

.metric-card__line--green {
  background: linear-gradient(90deg, #116149, #1d8b68);
}

.metric-card__line--blue {
  background: linear-gradient(90deg, #174c7d, #2a77aa);
}

.metric-card__line--amber {
  background: linear-gradient(90deg, #d97706, #f59e0b);
}

.metric-card__line--red {
  background: linear-gradient(90deg, #c2412d, #e76f51);
}
</style>
