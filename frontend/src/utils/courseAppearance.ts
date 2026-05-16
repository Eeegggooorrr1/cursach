import type { CourseListItem } from '@/api/types'

function hashString(value: string) {
  let hash = 0
  for (let index = 0; index < value.length; index += 1) {
    hash = (hash * 31 + value.charCodeAt(index)) >>> 0
  }
  return hash
}

export function courseStyle(course: Pick<CourseListItem, 'id' | 'title'>) {
  const seed = hashString(`${course.id}-${course.title}`)
  const hueA = seed % 360
  const hueB = (hueA + 38 + (seed % 54)) % 360
  const hueC = (hueA + 104 + (seed % 66)) % 360
  const gradient = `linear-gradient(145deg, hsl(${hueA} 74% 56%), hsl(${hueB} 70% 46%) 52%, hsl(${hueC} 66% 40%))`
  return { backgroundImage: gradient }
}
