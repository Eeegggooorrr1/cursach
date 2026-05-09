from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, Path, Query, Response, status

from core.auth import RequireRoles
from models.user import RoleEnum
from schemas.auth import UserFromToken
from schemas.course import (
    CourseCreateSchema,
    CourseDashboardSummarySchema,
    CourseReadSchema,
    PaginatedCourseListSchema,
    PaginatedCourseDetailSchema,
    CourseProgressResponseSchema,
    TestReviewResponseSchema,
    CourseEnrollSchema,
    CourseEnrollmentResponseSchema,
    CourseMembershipSchema,
    CourseVisibilityUpdateSchema,
    CourseDetailSchema,
    CoursePublicSearchSchema,
    PublicCourseDetailSchema,
)
from schemas.test import (
    TestReadSchema,
    TestSubmitSchema,
    TestSubmitResponseSchema,
)
from services.course import CourseService
from services.course_search import CourseSearchService
from services.submission import TestSubmissionService
from services.test import TestService

router = APIRouter(
    prefix="/courses", tags=["courses"], route_class=DishkaRoute
)


@router.post("/")
async def create_course(
    course: CourseCreateSchema,
    user: Annotated[
        UserFromToken, Depends(RequireRoles(RoleEnum.USER, RoleEnum.ADMIN))
    ],
    course_service: FromDishka[CourseService],
) -> CourseReadSchema:
    created_course = await course_service.create_course(
        user_id=user.id,
        title=course.title,
        comment=course.comment,
        prompt=course.prompt,
        topics=course.topics,
        initial_difficulty=course.initial_difficulty,
        is_public=course.is_public,
    )

    return created_course


@router.post("/{course_id}/create-test")
async def create_test(
    course_id: Annotated[int, Path(gt=0)],
    test_service: FromDishka[TestService],
    user: Annotated[
        UserFromToken, Depends(RequireRoles(RoleEnum.USER, RoleEnum.ADMIN))
    ],
) -> TestReadSchema:
    return await test_service.create_test(course_id=course_id, user_id=user.id)


@router.get("/summary")
async def get_dashboard_summary(
    user: Annotated[
        UserFromToken, Depends(RequireRoles(RoleEnum.USER, RoleEnum.ADMIN))
    ],
    course_service: FromDishka[CourseService],
) -> CourseDashboardSummarySchema:
    return await course_service.get_dashboard_summary(user_id=user.id)


@router.get("/{course_id}/tests/{test_id}")
async def get_test(
    course_id: Annotated[int, Path(gt=0)],
    test_id: Annotated[int, Path(gt=0)],
    test_service: FromDishka[TestService],
    user: Annotated[
        UserFromToken, Depends(RequireRoles(RoleEnum.USER, RoleEnum.ADMIN))
    ],
) -> TestReadSchema:
    return await test_service.get_test(
        course_id=course_id,
        test_id=test_id,
        user_id=user.id,
    )


@router.post(
    "/{course_id}/{test_id}/submit",
)
async def submit_test(
    course_id: int,
    test_id: int,
    payload: TestSubmitSchema,
    user: Annotated[
        UserFromToken, Depends(RequireRoles(RoleEnum.USER, RoleEnum.ADMIN))
    ],
    service: FromDishka[TestSubmissionService],
) -> TestSubmitResponseSchema:
    return await service.submit_test(
        course_id=course_id,
        test_id=test_id,
        user_id=user.id,
        payload=payload,
    )


@router.get("/")
async def get_my_courses(
    user: Annotated[
        UserFromToken, Depends(RequireRoles(RoleEnum.USER, RoleEnum.ADMIN))
    ],
    course_service: FromDishka[CourseService],
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PaginatedCourseListSchema:
    return await course_service.get_user_courses(
        user_id=user.id,
        limit=limit,
        offset=offset,
    )


@router.get("/public")
async def get_public_courses(
    course_search_service: FromDishka[CourseSearchService],
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    q: str | None = Query(default=None, min_length=1, max_length=120),
    sort: str = Query(
        default="created_desc",
        pattern="^(created_desc|created_asc)$",
    ),
) -> PaginatedCourseListSchema:
    return await course_search_service.search_public_courses(
        limit=limit,
        offset=offset,
        filters=CoursePublicSearchSchema(q=q, sort=sort),
    )


@router.get("/public/{course_id}")
async def get_public_course_detail(
    course_id: int,
    course_service: FromDishka[CourseService],
) -> PublicCourseDetailSchema:
    return await course_service.get_public_course_detail(course_id=course_id)


@router.post("/{course_id}/enroll")
async def enroll_public_course(
    course_id: int,
    payload: CourseEnrollSchema,
    user: Annotated[
        UserFromToken, Depends(RequireRoles(RoleEnum.USER, RoleEnum.ADMIN))
    ],
    course_service: FromDishka[CourseService],
) -> CourseEnrollmentResponseSchema:
    return await course_service.enroll_public_course(
        user_id=user.id,
        course_id=course_id,
        initial_difficulty=payload.initial_difficulty,
    )


@router.get("/{course_id}/membership")
async def get_course_membership(
    course_id: int,
    user: Annotated[
        UserFromToken, Depends(RequireRoles(RoleEnum.USER, RoleEnum.ADMIN))
    ],
    course_service: FromDishka[CourseService],
) -> CourseMembershipSchema:
    return await course_service.get_course_membership(
        user_id=user.id,
        course_id=course_id,
    )


@router.patch("/{course_id}/visibility")
async def update_course_visibility(
    course_id: int,
    payload: CourseVisibilityUpdateSchema,
    user: Annotated[
        UserFromToken, Depends(RequireRoles(RoleEnum.USER, RoleEnum.ADMIN))
    ],
    course_service: FromDishka[CourseService],
) -> CourseDetailSchema:
    return await course_service.set_course_visibility(
        user_id=user.id,
        course_id=course_id,
        is_public=payload.is_public,
    )


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    user: Annotated[
        UserFromToken, Depends(RequireRoles(RoleEnum.USER, RoleEnum.ADMIN))
    ],
    course_service: FromDishka[CourseService],
) -> Response:
    await course_service.delete_course_for_user(
        user_id=user.id,
        course_id=course_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{course_id}")
async def get_course_detail(
    course_id: int,
    user: Annotated[
        UserFromToken, Depends(RequireRoles(RoleEnum.USER, RoleEnum.ADMIN))
    ],
    course_service: FromDishka[CourseService],
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PaginatedCourseDetailSchema:
    return await course_service.get_course_detail(
        user_id=user.id,
        user_role=user.role,
        course_id=course_id,
        limit=limit,
        offset=offset,
    )


@router.get("/{course_id}/progress")
async def get_course_progress(
    course_id: int,
    user: Annotated[
        UserFromToken, Depends(RequireRoles(RoleEnum.USER, RoleEnum.ADMIN))
    ],
    course_service: FromDishka[CourseService],
) -> CourseProgressResponseSchema:
    return await course_service.get_course_progress(
        user_id=user.id,
        course_id=course_id,
    )


@router.get("/{course_id}/{test_id}/review")
async def get_test_review(
    course_id: int,
    test_id: int,
    user: Annotated[
        UserFromToken, Depends(RequireRoles(RoleEnum.USER, RoleEnum.ADMIN))
    ],
    test_service: FromDishka[TestService],
) -> TestReviewResponseSchema:
    return await test_service.get_review(
        user_id=user.id,
        course_id=course_id,
        test_id=test_id,
    )
