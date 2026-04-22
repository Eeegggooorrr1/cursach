from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, Path, Query

from core.di.providers.auth import RequireRoles
from models.user import RoleEnum
from schemas.auth import UserFromToken
from schemas.course import (
    CourseCreateSchema,
    CourseReadSchema,
    PaginatedCourseListSchema,
    PaginatedCourseDetailSchema,
    CourseProgressResponseSchema,
    TestReviewResponseSchema,
)
from schemas.test import (
    TestReadSchema,
    TestSubmitSchema,
    TestSubmitResponseSchema,
)
from services.course import CourseService
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
        topics=course.topics,
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
