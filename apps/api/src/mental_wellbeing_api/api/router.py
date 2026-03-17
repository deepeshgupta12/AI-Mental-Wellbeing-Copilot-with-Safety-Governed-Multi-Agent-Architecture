from fastapi import APIRouter

from mental_wellbeing_api.api.routes.action_plans import router as action_plans_router
from mental_wellbeing_api.api.routes.agent_runtime import router as agent_runtime_router
from mental_wellbeing_api.api.routes.check_ins import router as check_ins_router
from mental_wellbeing_api.api.routes.conversations import router as conversations_router
from mental_wellbeing_api.api.routes.health import router as health_router
from mental_wellbeing_api.api.routes.journal_entries import router as journal_entries_router
from mental_wellbeing_api.api.routes.safety_flags import router as safety_flags_router
from mental_wellbeing_api.api.routes.users import router as users_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(agent_runtime_router)
api_router.include_router(users_router)
api_router.include_router(check_ins_router)
api_router.include_router(journal_entries_router)
api_router.include_router(conversations_router)
api_router.include_router(action_plans_router)
api_router.include_router(safety_flags_router)