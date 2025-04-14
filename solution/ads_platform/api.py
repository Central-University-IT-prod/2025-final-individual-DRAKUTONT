from functools import partial

from ninja import NinjaAPI

from ads.api import router as ad_router
from ads_platform import error_handlers
from advertisers.api import router as advertisers_router
from ai_tools.api import router as ai_tools_router
from clients.api import router as clients_router
from score.api import router as score_router
from stats.api import router as stats_router
from time_emulation.api import router as time_router

api = NinjaAPI()

api.add_router("/clients", clients_router)
api.add_router("/advertisers", advertisers_router)
api.add_router("/moderation", ai_tools_router)
api.add_router("/ml-scores", score_router)
api.add_router("/ads", ad_router)
api.add_router("/stats", stats_router)
api.add_router("/time", time_router)

for exception, handler in error_handlers.exception_handlers:
    api.add_exception_handler(exception, partial(handler, router=api))
