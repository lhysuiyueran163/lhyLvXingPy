import json
from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agent.agent_service import agent_service
from app.config import config
from app.memory import memory_service

router = APIRouter()


class ChatBody(BaseModel):
    userId: str = "default"
    message: str


@router.post("/chat/stream")
async def stream_chat(body: ChatBody):
    user_id = body.userId or "default"

    async def event_stream():
        try:
            async for event in agent_service.stream_chat(user_id, body.message):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as error:
            yield f"data: {json.dumps({'type': 'error', 'message': str(error)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/chat")
async def chat(body: ChatBody):
    user_id = body.userId or "default"
    answer = await agent_service.chat(user_id, body.message)
    return {"userId": user_id, "message": body.message, "answer": answer}


@router.get("/history/{user_id}")
def get_history(user_id: str):
    history = memory_service.get_history(user_id)
    return {
        "userId": user_id,
        "count": len(history),
        "messages": [
            {
                "index": i,
                "role": "user" if m.__class__.__name__ == "HumanMessage" else "assistant",
                "content": m.content,
            }
            for i, m in enumerate(history)
        ],
    }


@router.delete("/history/{user_id}")
def clear_history(user_id: str):
    memory_service.clear_history(user_id)
    return {"success": True, "message": f"用户 {user_id} 的对话历史已清除"}


@router.get("/sessions")
def list_sessions():
    return memory_service.list_sessions()


@router.get("/tools")
def get_tools():
    return {
        "tools": [
            {"name": "get_weather", "desc": "查询目的地天气和穿衣建议"},
            {"name": "get_attractions", "desc": "推荐景点和目的地信息"},
            {"name": "generate_itinerary", "desc": "生成逐日详细行程"},
            {"name": "calculate_budget", "desc": "估算旅行总费用"},
            {"name": "check_visa", "desc": "查询签证要求"},
            {"name": "convert_currency", "desc": "货币换算和消费参考"},
            {"name": "generate_packing_list", "desc": "生成打包清单"},
            {"name": "translate_phrases", "desc": "旅行常用短语翻译"},
        ]
    }


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "lhy旅行AI后端服务 旅行规划助手",
        "llmProvider": config.llm["provider"],
        "model": config.llm["model"],
        "time": datetime.now().isoformat(),
    }
