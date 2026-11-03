import json
import re

from langchain_core.tools import tool
from app.llm import create_chat_model
from pydantic import BaseModel, Field

from app.config import config

ATTRACTIONS_DB: dict[str, list[dict]] = {
    "东京": [
        {"name": "浅草寺", "type": "文化", "duration": "1-2小时", "ticket": "免费", "tips": "早上8点前人少，可体验抽签占卜"},
        {"name": "新宿御苑", "type": "自然", "duration": "2-3小时", "ticket": "￥500", "tips": "春季赏樱最佳，秋季红叶也很美"},
        {"name": "筑地场外市场", "type": "美食", "duration": "2小时", "ticket": "免费", "tips": "早上6点开始，海鲜最新鲜"},
        {"name": "秋叶原", "type": "购物", "duration": "2-4小时", "ticket": "免费", "tips": "电子产品和动漫周边的天堂"},
        {"name": "明治神宫", "type": "文化", "duration": "1小时", "ticket": "免费", "tips": "森林环境清幽，适合晨练"},
        {"name": "涉谷十字路口", "type": "体验", "duration": "30分钟", "ticket": "免费", "tips": "全球最忙碌路口，适合拍照"},
    ],
    "巴黎": [
        {"name": "埃菲尔铁塔", "type": "地标", "duration": "2-3小时", "ticket": "€26-29", "tips": "提前网上预订，避免排队1-2小时"},
        {"name": "卢浮宫", "type": "文化", "duration": "3-4小时", "ticket": "€17", "tips": "蒙娜丽莎在713室，建议租语音导览"},
        {"name": "凡尔赛宫", "type": "历史", "duration": "半天", "ticket": "€20", "tips": "需要提前半天，花园免费"},
        {"name": "蒙马特高地", "type": "文化", "duration": "2-3小时", "ticket": "免费", "tips": "艺术家聚集地，可定制肖像画"},
        {"name": "奥赛博物馆", "type": "文化", "duration": "2-3小时", "ticket": "€16", "tips": "印象派画作最全，莫奈梵高作品众多"},
    ],
    "曼谷": [
        {"name": "大皇宫&玉佛寺", "type": "文化", "duration": "2-3小时", "ticket": "500铢", "tips": "需着装保守，禁止穿短裤背心"},
        {"name": "考山路", "type": "娱乐", "duration": "晚上", "ticket": "免费", "tips": "背包客天堂，酒吧美食按摩集中"},
        {"name": "恰图恰市场", "type": "购物", "duration": "半天", "ticket": "免费", "tips": "仅周六日开放，上午最凉快"},
        {"name": "卧佛寺", "type": "文化", "duration": "1小时", "ticket": "200铢", "tips": "46米长卧佛震撼，泰式按摩发源地"},
    ],
    "巴厘岛": [
        {"name": "乌布皇宫", "type": "文化", "duration": "1小时", "ticket": "免费", "tips": "每天晚上有克差舞表演"},
        {"name": "德格拉朗梯田", "type": "自然", "duration": "2小时", "ticket": "小费制", "tips": "日出时分最美，带防晒霜"},
        {"name": "库塔海滩", "type": "自然", "duration": "半天", "ticket": "免费", "tips": "冲浪胜地，日落景色绝美"},
        {"name": "乌鲁瓦图寺", "type": "文化", "duration": "2小时", "ticket": "约10万卢比", "tips": "悬崖神庙，注意猴子抢东西"},
    ],
}


class AttractionsInput(BaseModel):
    city: str = Field(description="目的地城市")
    interests: list[str] | None = Field(default=None, description='兴趣偏好，如：["文化","美食","购物"]')
    limit: int | None = Field(default=5, description="返回数量，默认5个")


@tool("get_attractions", args_schema=AttractionsInput)
async def attractions_tool(city: str, interests: list[str] | None = None, limit: int | None = 5) -> str:
    """查询目的地热门景点，返回景点名称、类型、游览时长、门票、实用贴士。用户询问景点时调用。"""
    limit = limit or 5
    city_key = next((k for k in ATTRACTIONS_DB if k in city or city in k), None)
    attractions = ATTRACTIONS_DB.get(city_key) if city_key else None

    if not attractions:
        llm = create_chat_model(temperature=0.5)
        resp = await llm.ainvoke(
            f'请列出{city}最值得去的{limit}个景点，每个包含名称、类型、建议游览时长、门票、实用小贴士。'
            f'只输出JSON数组：[{{"name":"","type":"","duration":"","ticket":"","tips":""}}]'
        )
        try:
            text = re.sub(r"```json\n?|\n?```", "", str(resp.content)).strip()
            attractions = json.loads(text)
        except Exception:
            return f'{city}景点信息生成失败，建议搜索"{city}必去景点"获取最新信息'

    if interests:
        filtered = [a for a in attractions if any(i in a["type"] or i in a["name"] for i in interests)]
        if filtered:
            attractions = filtered

    attractions = attractions[:limit]

    listing = "\n\n".join(
        f"**{i + 1}. {a['name']}** [{a['type']}]\n   ⏱ {a['duration']} | 🎫 {a['ticket']}\n   💡 {a['tips']}"
        for i, a in enumerate(attractions)
    )

    return f"🏛️ **{city}精选景点**（{len(attractions)}个）\n\n{listing}\n\n> 门票价格可能变化，出行前请确认"
