class CacheKeys:
    @staticmethod
    def public_course(course_id: int) -> str:
        return f"public-course:{course_id}"

    @staticmethod
    def public_courses_pattern() -> str:
        return "public-courses:*"

    @staticmethod
    def public_courses_page(
        *,
        query: str | None,
        sort: str,
        limit: int,
        offset: int,
    ) -> str:
        normalized_query = query or "_"
        return (
            "public-courses:"
            f"q:{normalized_query}:sort:{sort}:limit:{limit}:offset:{offset}"
        )

    @staticmethod
    def test(user_id: int, course_id: int, test_id: int) -> str:
        return f"test:user:{user_id}:course:{course_id}:test:{test_id}"

    @staticmethod
    def tests_for_course_pattern(course_id: int) -> str:
        return f"test:user:*:course:{course_id}:*"

    @staticmethod
    def tests_for_user_course_pattern(user_id: int, course_id: int) -> str:
        return f"test:user:{user_id}:course:{course_id}:*"

    @staticmethod
    def test_review(user_id: int, course_id: int, test_id: int) -> str:
        return f"test-review:user:{user_id}:course:{course_id}:test:{test_id}"

    @staticmethod
    def test_reviews_for_course_pattern(course_id: int) -> str:
        return f"test-review:user:*:course:{course_id}:*"

    @staticmethod
    def test_reviews_for_user_course_pattern(
        user_id: int,
        course_id: int,
    ) -> str:
        return f"test-review:user:{user_id}:course:{course_id}:*"
