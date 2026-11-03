import httpx
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.config import config

MOCK_WEATHER: dict[str, dict] = {
    "东京": {"temp": 22, "feels": 20, "weather": "晴", "humidity": 55, "wind": "东北风3级"},
    "巴黎": {"temp": 18, "feels": 16, "weather": "多云", "humidity": 68, "wind": "西风2级"},
    "曼谷": {"temp": 33, "feels": 38, "weather": "晴", "humidity": 75, "wind": "南风1级"},
    "巴厘岛": {"temp": 30, "feels": 34, "weather": "阵雨", "humidity": 82, "wind": "东南风2级"},
    "北京": {"temp": 25, "feels": 23, "weather": "晴", "humidity": 40, "wind": "北风3级"},
    "上海": {"temp": 28, "feels": 30, "weather": "多云", "humidity": 70, "wind": "东风2级"},
    "武汉": {"temp": 30, "feels": 33, "weather": "晴", "humidity": 65, "wind": "东南风2级"},
    "广州": {"temp": 32, "feels": 36, "weather": "雷阵雨", "humidity": 85, "wind": "南风1级"},
    "纽约": {"temp": 20, "feels": 18, "weather": "晴", "humidity": 50, "wind": "西风4级"},
    "悉尼": {"temp": 16, "feels": 14, "weather": "晴", "humidity": 62, "wind": "南风3级"},
    "首尔": {"temp": 19, "feels": 17, "weather": "多云", "humidity": 60, "wind": "西北风2级"},
    "新加坡": {"temp": 31, "feels": 36, "weather": "雷阵雨", "humidity": 85, "wind": "南风1级"},
}


def get_clothing_advice(temp: float) -> str:
    if temp >= 30:
        return "🌡️ 炎热，建议穿轻薄透气短袖短裤，做好防晒"
    if temp >= 25:
        return "☀️ 温暖舒适，短袖加薄外套即可"
    if temp >= 18:
        return "🍃 气温适宜，长袖加薄外套，早晚偏凉"
    if temp >= 10:
        return "🧥 较凉爽，建议穿外套或毛衣"
    return "❄️ 寒冷，需要穿厚外套或羽绒服"


class WeatherInput(BaseModel):
    city: str = Field(description="城市名称，如：东京、巴黎、曼谷、北京")


@tool("get_weather", args_schema=WeatherInput)
async def weather_tool(city: str) -> str:
    """查询指定城市的实时天气，包括温度、天气状况、湿度、风力和穿衣建议。用户询问目的地天气时调用。"""
    try:
        if config.weather.api_key:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.openweathermap.org/data/2.5/weather",
                    params={
                        "q": city,
                        "appid": config.weather.api_key,
                        "units": "metric",
                        "lang": "zh_cn",
                    },
                )
                raw = resp.json()
            data = {
                "temp": round(raw["main"]["temp"]),
                "feels": round(raw["main"]["feels_like"]),
                "weather": raw["weather"][0]["description"],
                "humidity": raw["main"]["humidity"],
                "wind": f"{raw['wind']['speed']}m/s",
            }
        else:
            key = next((k for k in MOCK_WEATHER if k in city or city in k), None)
            data = MOCK_WEATHER.get(
                key, {"temp": 22, "feels": 20, "weather": "晴", "humidity": 60, "wind": "微风"}
            )

        return f"""🌤️ **{city}实时天气**

温度：{data['temp']}°C（体感 {data['feels']}°C）
天气：{data['weather']}
湿度：{data['humidity']}%
风力：{data['wind']}

**穿衣建议：** {get_clothing_advice(data['temp'])}
**出行提示：** {'☔ 建议携带雨伞' if '雨' in data['weather'] else '✅ 天气适合出行'}

> 数据仅供参考，出发前请查看最新天气预报"""
    except Exception as e:
        return f"获取 {city} 天气失败：{e}"
