from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict

from .connections import Connections, connections_dep
from .manager import IEXAPI
from .routers import analyser, forex, tickers

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


origins = [
    "http://localhost:8000",
]

def create_app(connections: Connections):
    app = FastAPI()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins = origins,
        allow_credentials = True,
        allow_methods = ["*"],
        allow_headers = ["*"],
    )

    @app.on_event("shutdown")
    async def shutdown():
        await connections.close()

    # app.include_router(analyser.router)
    app.include_router(forex.router)
    app.include_router(tickers.router)

    return app

app = create_app(connections_dep)