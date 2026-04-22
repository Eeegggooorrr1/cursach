from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

router = APIRouter(prefix="/tests", tags=["tests"], route_class=DishkaRoute)
