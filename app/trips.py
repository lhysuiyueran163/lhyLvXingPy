"""Local single-user itinerary workspace with validated plans and SQLite persistence."""
from contextlib import contextmanager
import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, model_validator
from app.llm import create_chat_model

router = APIRouter()
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "trips.sqlite3"

class Activity(BaseModel):
    time: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(min_length=1, max_length=2000)
    transport: str = Field(min_length=1, max_length=300)
    estimated_cost: float = Field(ge=0)

class Day(BaseModel):
    day: int = Field(ge=1, le=14)
    activities: list[Activity] = Field(min_length=1, max_length=12)

class Plan(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    destination: str = Field(min_length=1, max_length=120)
    travelers: int = Field(ge=1, le=20)
    budget: float = Field(gt=0)
    days: list[Day] = Field(min_length=1, max_length=14)

    @model_validator(mode="after")
    def ordered_days(self):
        if [d.day for d in self.days] != list(range(1, len(self.days) + 1)):
            raise ValueError("行程日期必须从第1天起连续排列")
        return self

class GenerateBody(BaseModel):
    destination: str = Field(min_length=1, max_length=120)
    days: int = Field(ge=1, le=14)
    travelers: int = Field(default=1, ge=1, le=20)
    budget: float = Field(gt=0)
    preferences: str = Field(default="文化、美食", max_length=1000)

@contextmanager
def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.execute("CREATE TABLE IF NOT EXISTS trips (id TEXT PRIMARY KEY, created_at TEXT NOT NULL, plan TEXT NOT NULL)")
    try:
        with db:
            yield db
    finally:
        db.close()

@router.post("/generate")
async def generate(body: GenerateBody):
    try:
        llm = create_chat_model(temperature=0.3)
        result = await llm.with_structured_output(Plan, method="json_schema").ainvoke(
            "生成中文旅行计划，严格遵守结构。费用为全部同行人合计的人民币估算，每项费用只计算一次，包含餐饮、住宿、交通和活动，尽量不超总预算。"
            "每天提供早中晚活动，交通字段说明如何前往；不得声称已核实实时价格。需求：" + body.model_dump_json())
        plan = Plan.model_validate(result)
        if len(plan.days) != body.days:
            raise ValueError("模型生成天数与需求不符，请重试")
        plan.destination = body.destination
        plan.travelers = body.travelers
        plan.budget = body.budget
        return plan
    except Exception:
        logging.getLogger(__name__).exception("Structured itinerary generation failed")
        raise HTTPException(502, "行程生成失败或格式不完整，请重试或减少天数")

@router.post("")
def save(plan: Plan):
    trip_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    with connect() as db:
        db.execute("INSERT INTO trips VALUES (?, ?, ?)", (trip_id, created_at, plan.model_dump_json()))
    return {"id": trip_id, "created_at": created_at, "plan": plan}

@router.get("")
def list_trips():
    with connect() as db:
        rows = db.execute("SELECT id, created_at, plan FROM trips ORDER BY created_at DESC").fetchall()
    return [{"id": row[0], "created_at": row[1], "plan": json.loads(row[2])} for row in rows]

@router.get("/{trip_id}")
def get_trip(trip_id: str):
    with connect() as db:
        row = db.execute("SELECT id, created_at, plan FROM trips WHERE id=?", (trip_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "行程不存在")
    return {"id": row[0], "created_at": row[1], "plan": json.loads(row[2])}

@router.delete("/{trip_id}")
def delete_trip(trip_id: str):
    with connect() as db:
        cursor = db.execute("DELETE FROM trips WHERE id=?", (trip_id,))
        if cursor.rowcount == 0:
            raise HTTPException(404, "行程不存在")
    return {"success": True}
