from fastapi import APIRouter

from mental_wellbeing_api.api.routes.agent_runtime import router as agent_runtime_router
from mental_wellbeing_api.api.routes.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(agent_runtime_router)