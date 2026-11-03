from fastapi import APIRouter
from pydantic import BaseModel

from app.tools.budget_tool import budget_tool
from app.tools.currency_tool import currency_tool
from app.tools.visa_tool import visa_tool
from app.tools.weather_tool import weather_tool

router = APIRouter()


class CityBody(BaseModel):
    city: str


class DestinationBody(BaseModel):
    destination: str


class BudgetBody(BaseModel):
    destination: str
    days: int
    people: int | None = 1
    budget_level: str | None = "中等"
    include_flight: bool | None = False


class CurrencyBody(BaseModel):
    amount: float
    from_currency: str
    to_currency: str | None = "CNY"


@router.post("/weather")
async def get_weather(body: CityBody):
    return await weather_tool.ainvoke({"city": body.city})


@router.post("/budget")
async def calculate_budget(body: BudgetBody):
    return budget_tool.invoke(body.model_dump())


@router.post("/visa")
async def check_visa(body: DestinationBody):
    return visa_tool.invoke({"destination": body.destination})


@router.post("/currency")
async def convert_currency(body: CurrencyBody):
    return currency_tool.invoke(body.model_dump())
