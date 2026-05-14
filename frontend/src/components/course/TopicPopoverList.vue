<template>
  <div class="topic-list">
    <article v-for="topic in topics" :key="topic.id" class="topic-item">
      <div class="topic-item__pill">
        {{ topic.name }}
        <div class="topic-item__popover">
          <div v-for="subtopic in topic.subtopics" :key="subtopic.id" class="topic-item__subrow">
            <span>{{ subtopic.name }}</span>
            <div v-if="typeof subtopic.mastery_score === 'number'" class="topic-item__bar">
              <i :style="{ width: `${Math.round(Math.max(0, Math.min(1, subtopic.mastery_score)) * 100)}%` }"></i>
            </div>
          </div>
        </div>
      </div>
    </article>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  topics: Array<{
    id: number
    name: string
    subtopics: Array<{
      id: number
      name: string
      mastery_score?: number | null
    }>
  }>
}>()
</script>

<style scoped>
.topic-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.topic-item {
  position: relative;
}

.topic-item__pill {
  position: relative;
  border-radius: 999px;
  padding: 11px 14px;
  color: #546071;
  background: #eef2ef;
  font-weight: 700;
  transition:
    transform 180ms ease,
    color 180ms ease,
    background 180ms ease;
}

.topic-item__pill:hover {
  color: white;
  background: #111827;
  transform: translateY(-2px);
}

.topic-item__popover {
  position: absolute;
  left: 50%;
  bottom: calc(100% + 12px);
  z-index: 5;
  width: 260px;
  display: grid;
  gap: 10px;
  padding: 14px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 18px;
  background: rgba(17, 24, 39, 0.97);
  box-shadow: 0 20px 54px rgba(17, 24, 39, 0.26);
  opacity: 0;
  pointer-events: none;
  transform: translate(-50%, 8px) scale(0.96);
  transition:
    opacity 160ms ease,
    transform 160ms ease;
}

.topic-item__popover::after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: -6px;
  width: 12px;
  height: 12px;
  background: rgba(17, 24, 39, 0.97);
  transform: translateX(-50%) rotate(45deg);
}

.topic-item__pill:hover .topic-item__popover {
  opacity: 1;
  transform: translate(-50%, 0) scale(1);
}

.topic-item__subrow {
  display: grid;
  gap: 6px;
  color: rgba(255, 255, 255, 0.86);
  font-size: 13px;
  line-height: 1.4;
}

.topic-item__bar {
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
}

.topic-item__bar i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #1d8b68, #2a77aa);
}
</style>
