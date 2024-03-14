from logging import config
from os import environ

import uvicorn
from fastapi import FastAPI, Request, status, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination

from chatbot.controller import (
    source,
    knowledge,
    configuration,
    session,
    model,
    tool,
    stats,
    auth,
)
from chatbot.knowledge import DocumentCollection
from chatbot.log import LogConfig
from chatbot.service.tool import ToolFactory

ORIGINS = [
    environ.get("API_CORS_ORIGIN", "http://localhost:3000"),
]

config.dictConfig(LogConfig().dict())

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
add_pagination(app)
app.include_router(knowledge.router)
app.include_router(source.router)
app.include_router(session.router)
app.include_router(configuration.router)
app.include_router(model.router)
app.include_router(tool.router)
app.include_router(stats.router)
app.include_router(auth.router)

for tool_api_router in ToolFactory().get_api_routers().values():
    app.include_router(tool_api_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Hello Bigger Applications!"}


@app.on_event("startup")
async def startup():
    """Startup entry point"""
    DocumentCollection().create()


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(_: Request, exc: RequestValidationError):
    """Request validation error handler"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.exception_handler(ResponseValidationError)
async def response_validation_error_handler(_: Response, exc: ResponseValidationError):
    """Response validation error handler"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


if __name__ == "__main__":
    reload: str = environ.get("API_RELOAD", "false").lower()
    reload: bool = reload == "true" or reload == "1"
    workers: int = int(environ.get("API_WORKERS", "4"))
    port: int = int(environ.get("API_PORT", "8000"))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        workers=workers,
        log_config=None,
        reload=reload,
    )
