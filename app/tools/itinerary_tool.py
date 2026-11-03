from langchain_core.tools import tool
from app.llm import create_chat_model
from pydantic import BaseModel, Field

from app.config import config


class ItineraryInput(BaseModel):
    destination: str = Field(description="目的地，如：东京、巴黎、巴厘岛")
    days: int = Field(description="旅行天数")
    style: str | None = Field(default="平衡", description="旅行风格：慢节奏/深度/美食/文化/购物，默认平衡")
    budget_level: str | None = Field(default="中等", description="预算档次：经济/中等/豪华，默认中等")
    interests: list[str] | None = Field(default=None, description="兴趣偏好列表")


@tool("generate_itinerary", args_schema=ItineraryInput)
async def itinerary_tool(
    destination: str,
    days: int,
    style: str | None = "平衡",
    budget_level: str | None = "中等",
    interests: list[str] | None = None,
) -> str:
    """根据目的地、天数、旅行风格生成详细逐日行程，含景点、餐厅、交通和预算。用户要求规划行程时调用。"""
    style = style or "平衡"
    budget_level = budget_level or "中等"
    interests = interests or []

    llm = create_chat_model(temperature=0.5)

    interest_str = f"，偏好：{'、'.join(interests)}" if interests else ""
    resp = await llm.ainvoke(
        f"你是专业旅行规划师，请为以下旅行生成详细行程：\n"
        f"目的地：{destination}，天数：{days}天，风格：{style}，预算：{budget_level}{interest_str}\n\n"
        f"每天包含：上午安排（9-12点）、午餐推荐、下午安排（13-17点）、晚餐、晚上活动、交通方式、当日预算。\n"
        f"格式清晰易读，用emoji增加可读性。"
    )
    return f"📅 **{destination} {days}天{style}行程规划**\n\n{resp.content}"
