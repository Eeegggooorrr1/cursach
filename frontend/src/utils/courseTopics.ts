import type { CourseProgressItem, TopicRead } from '@/api/types'

export interface TopicWithProgress {
  id: number
  name: string
  subtopics: Array<{
    id: number
    name: string
    mastery_score?: number | null
  }>
}

export function groupProgressTopics(items: CourseProgressItem[]): TopicWithProgress[] {
  const grouped = new Map<number, TopicWithProgress>()

  for (const item of items) {
    if (!grouped.has(item.topic_id)) {
      grouped.set(item.topic_id, {
        id: item.topic_id,
        name: item.topic_name,
        subtopics: [],
      })
    }

    grouped.get(item.topic_id)?.subtopics.push({
      id: item.subtopic_id,
      name: item.subtopic_name,
      mastery_score: item.mastery_score,
    })
  }

  return Array.from(grouped.values())
}

export function mapTopics(items: TopicRead[]): TopicWithProgress[] {
  return items.map((topic) => ({
    id: topic.id,
    name: topic.name,
    subtopics: topic.subtopics.map((subtopic) => ({
      id: subtopic.id,
      name: subtopic.name,
      mastery_score: null,
    })),
  }))
}
