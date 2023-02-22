from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .analysis import AnalysisAPIDep, analysis_api_dep
from .timeseries import TimeseriesAPIDep, timeseries_api_dep
from .routers import analysis_router, timeseries_router

origins = [
    "http://localhost:8000",
]

def create_app(analysis_api_dep: AnalysisAPIDep, timeseries_api_dep: TimeseriesAPIDep):

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins = ["*"],
        allow_credentials = True,
        allow_methods = ["*"],
        allow_headers = ["*"],
    )

    @app.on_event("shutdown")
    async def startdown_event():
        await analysis_api_dep.close()
        await timeseries_api_dep.close()

    @app.get("/healthz")
    def health_check():
        return JSONResponse({ "status": "healthy" })

    app.include_router(analysis_router)
    app.include_router(timeseries_router)

    return app

app = create_app(analysis_api_dep, timeseries_api_dep)