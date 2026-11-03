from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agent.agent_router import router as agent_router
from app.config import config
from app.trips import router as trips_router
from app.tools.tools_router import router as tools_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    print(f"\n旅途 AI 服务已启动：http://localhost:{config.server.port}")
    print(f"   前端地址：{config.server.cors_origin}\n")
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.server.cors_origin],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(trips_router, prefix="/api/trips", tags=["行程工作台"])
app.include_router(agent_router, prefix="/api/agent")
app.include_router(tools_router, prefix="/api/tools")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=config.server.port, reload=True)
