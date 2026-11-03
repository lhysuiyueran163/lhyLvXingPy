from langchain_core.tools import tool
from pydantic import BaseModel, Field

DAILY_COSTS: dict[str, dict[str, dict]] = {
    "东京": {
        "economy": {"accommodation": 250, "food": 120, "transport": 60, "activities": 80},
        "mid": {"accommodation": 550, "food": 250, "transport": 100, "activities": 200},
        "luxury": {"accommodation": 1500, "food": 600, "transport": 200, "activities": 500},
    },
    "巴黎": {
        "economy": {"accommodation": 400, "food": 150, "transport": 80, "activities": 120},
        "mid": {"accommodation": 900, "food": 350, "transport": 150, "activities": 300},
        "luxury": {"accommodation": 2500, "food": 800, "transport": 300, "activities": 600},
    },
    "曼谷": {
        "economy": {"accommodation": 150, "food": 60, "transport": 30, "activities": 50},
        "mid": {"accommodation": 400, "food": 150, "transport": 80, "activities": 150},
        "luxury": {"accommodation": 1200, "food": 400, "transport": 200, "activities": 400},
    },
    "巴厘岛": {
        "economy": {"accommodation": 200, "food": 80, "transport": 60, "activities": 100},
        "mid": {"accommodation": 500, "food": 200, "transport": 150, "activities": 250},
        "luxury": {"accommodation": 1500, "food": 500, "transport": 300, "activities": 600},
    },
    "默认": {
        "economy": {"accommodation": 300, "food": 100, "transport": 50, "activities": 80},
        "mid": {"accommodation": 600, "food": 250, "transport": 120, "activities": 200},
        "luxury": {"accommodation": 1800, "food": 600, "transport": 250, "activities": 500},
    },
}

LEVEL_MAP: dict[str, str] = {
    "经济": "economy", "节省": "economy", "便宜": "economy",
    "中等": "mid", "适中": "mid", "普通": "mid",
    "豪华": "luxury", "高端": "luxury", "奢华": "luxury",
}

FLIGHT_EST: dict[str, int] = {
    "东京": 3000, "大阪": 3000, "首尔": 2500,
    "巴黎": 8000, "伦敦": 8000, "罗马": 8000,
    "曼谷": 2000, "巴厘岛": 2500, "新加坡": 2500,
    "纽约": 10000, "悉尼": 6000,
}


class BudgetInput(BaseModel):
    destination: str = Field(description="目的地")
    days: int = Field(description="旅行天数")
    people: int | None = Field(default=1, description="出行人数，默认1人")
    budget_level: str | None = Field(default="中等", description="预算档次：经济/中等/豪华")
    include_flight: bool | None = Field(default=False, description="是否包含机票估算")


@tool("calculate_budget", args_schema=BudgetInput)
def budget_tool(
    destination: str,
    days: int,
    people: int | None = 1,
    budget_level: str | None = "中等",
    include_flight: bool | None = False,
) -> str:
    """估算旅行总费用，按住宿/餐饮/交通/景点/购物分项计算。用户询问旅行花费时调用。"""
    people = people or 1
    budget_level = budget_level or "中等"
    level_key = LEVEL_MAP.get(budget_level, "mid")
    city_key = next((k for k in DAILY_COSTS if k in destination or destination in k), "默认")
    costs = DAILY_COSTS[city_key][level_key]
    daily_total = sum(costs.values())
    total_base = daily_total * days * people
    shopping = round(total_base * 0.15)
    misc = round(total_base * 0.10)
    subtotal = total_base + shopping + misc
    emergency = round(subtotal * 0.10)
    grand_total = subtotal + emergency

    flight_text = ""
    if include_flight:
        flight_key = next((k for k in FLIGHT_EST if k in destination), None)
        flight_cost = FLIGHT_EST.get(flight_key, 5000)
        flight_text = f"✈️ 机票（往返估算）：¥{flight_cost * people:,}（{people}人）\n"

    return f"""💰 **{destination} {days}天预算（{budget_level}档·{people}人）**

**每日明细：**
🏨 住宿：¥{costs['accommodation'] * people:,}/晚
🍜 餐饮：¥{costs['food'] * people:,}/天
🚌 交通：¥{costs['transport'] * people:,}/天
🎫 景点：¥{costs['activities'] * people:,}/天

**{days}天总费用：**
{flight_text}📋 基础花费：¥{total_base:,}
🛍️ 购物纪念品：¥{shopping:,}
📌 杂费：¥{misc:,}
🆘 应急备用（10%）：¥{emergency:,}

**💵 预计总花费：¥{grand_total:,}（人均 ¥{round(grand_total / people):,}）**

> 实际费用因个人消费习惯和汇率波动有所不同，建议多备10-15%应急资金"""
