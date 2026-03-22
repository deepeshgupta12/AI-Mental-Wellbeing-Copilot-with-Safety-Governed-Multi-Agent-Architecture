from fastapi import APIRouter

from mental_wellbeing_api.api.routes.action_plans import router as action_plans_router
from mental_wellbeing_api.api.routes.admin import router as admin_router
from mental_wellbeing_api.api.routes.admin_enterprise import router as admin_enterprise_router
from mental_wellbeing_api.api.routes.admin_integrations import router as admin_integrations_router
from mental_wellbeing_api.api.routes.admin_settings import router as admin_settings_router
from mental_wellbeing_api.api.routes.agent_runtime import router as agent_runtime_router
from mental_wellbeing_api.api.routes.auth import router as auth_router
from mental_wellbeing_api.api.routes.check_ins import router as check_ins_router
from mental_wellbeing_api.api.routes.conversations import router as conversations_router
from mental_wellbeing_api.api.routes.enterprise import router as enterprise_router
from mental_wellbeing_api.api.routes.follow_ups import router as follow_ups_router
from mental_wellbeing_api.api.routes.health import router as health_router
from mental_wellbeing_api.api.routes.journal_entries import router as journal_entries_router
from mental_wellbeing_api.api.routes.memory_trends import router as memory_trends_router
from mental_wellbeing_api.api.routes.safety_flags import router as safety_flags_router
from mental_wellbeing_api.api.routes.support_tracks import router as support_tracks_router
from mental_wellbeing_api.api.routes.users import router as users_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(enterprise_router)
api_router.include_router(admin_settings_router)
api_router.include_router(admin_enterprise_router)
api_router.include_router(admin_integrations_router)
api_router.include_router(agent_runtime_router)
api_router.include_router(users_router)
api_router.include_router(check_ins_router)
api_router.include_router(journal_entries_router)
api_router.include_router(conversations_router)
api_router.include_router(action_plans_router)
api_router.include_router(follow_ups_router)
api_router.include_router(safety_flags_router)
api_router.include_router(memory_trends_router)
api_router.include_router(support_tracks_router)
api_router.include_router(admin_router)