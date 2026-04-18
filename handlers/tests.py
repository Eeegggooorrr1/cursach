from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends

from core.di.providers.auth import RequireRoles
from models.user import RoleEnum
from schemas.auth import UserFromToken
from schemas.test import TestCreateSchema, TestReadSchema
from services.test import TestService

router = APIRouter(prefix="/tests", tags=["tests"], route_class=DishkaRoute)

