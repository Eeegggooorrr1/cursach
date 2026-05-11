from dataclasses import dataclass


@dataclass(frozen=True)
class CourseGenerationPolicy:
    @staticmethod
    def get_subtopics_count(topics_count: int) -> int:
        if topics_count == 1:
            return 8
        if topics_count == 2:
            return 4
        if 3 <= topics_count <= 5:
            return 3
        return 2
