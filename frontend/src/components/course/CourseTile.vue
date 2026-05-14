<template>
  <RouterLink class="course-tile" :style="courseStyle(course)" :to="to">
    <div class="course-tile__overlay"></div>
    <div class="course-tile__content">
      <div class="course-tile__head">
        <span class="course-tile__status">{{ statusLabel }}</span>
        <span class="course-tile__date">{{ formatDate(course.created_at) }}</span>
      </div>

      <div class="course-tile__body">
        <h3 class="course-tile__title">{{ course.title }}</h3>
        <p class="course-tile__text">{{ course.comment || fallbackText }}</p>
      </div>

      <div class="course-tile__foot">
        <span class="course-tile__hint">{{ hint }}</span>
        <span class="course-tile__arrow">></span>
      </div>
    </div>
  </RouterLink>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import type { CourseListItem } from '@/api/types'
import { courseStyle } from '@/utils/courseAppearance'
import { formatDate } from '@/utils/format'

const props = withDefaults(
  defineProps<{
    course: CourseListItem
    to: string | { name: string; params?: Record<string, string | number> }
    hint: string
    fallbackText?: string
    statusLabel?: string
  }>(),
  {
    fallbackText: 'Описание пока не добавлено.',
    statusLabel: '',
  },
)

const statusLabel = computed(() => {
  if (props.statusLabel) {
    return props.statusLabel
  }
  return props.course.is_public ? 'публичный' : 'приватный'
})
</script>

<style scoped>
.course-tile {
  position: relative;
  overflow: hidden;
  min-height: 230px;
  border-radius: 28px;
  color: white;
  box-shadow: var(--shadow-strong);
  transition:
    transform 180ms ease,
    box-shadow 180ms ease;
}

.course-tile:hover {
  transform: translateY(-3px);
}

.course-tile__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.06), rgba(17, 24, 39, 0.68));
}

.course-tile__content {
  position: relative;
  z-index: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 18px;
  padding: 20px;
}

.course-tile__head,
.course-tile__foot {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.course-tile__status {
  border-radius: 999px;
  padding: 7px 11px;
  background: rgba(255, 255, 255, 0.16);
  font-size: 12px;
  font-weight: 800;
}

.course-tile__date,
.course-tile__hint {
  color: rgba(255, 255, 255, 0.76);
  font-size: 13px;
}

.course-tile__body {
  display: grid;
  gap: 12px;
}

.course-tile__title {
  margin: 0;
  font-size: 26px;
  line-height: 1.05;
}

.course-tile__text {
  margin: 0;
  line-height: 1.55;
  color: rgba(255, 255, 255, 0.82);
}

.course-tile__arrow {
  font-weight: 900;
}
</style>
