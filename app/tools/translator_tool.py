from langchain_core.tools import tool
from app.llm import create_chat_model
from pydantic import BaseModel, Field

from app.config import config

PHRASES: dict[str, dict[str, str]] = {
    "日语": {
        "你好": "こんにちは（Konnichiwa）",
        "谢谢": "ありがとうございます（Arigatou gozaimasu）",
        "对不起": "すみません（Sumimasen）",
        "多少钱": "いくらですか（Ikura desu ka）",
        "在哪里": "どこですか（Doko desu ka）",
        "帮帮我": "たすけてください（Tasukete kudasai）",
        "结账": "おかいけいをおねがいします（Okaikei wo onegaishimasu）",
        "好吃": "おいしい（Oishii）",
    },
    "泰语": {
        "你好": "สวัสดี（Sawasdee krab/ka）",
        "谢谢": "ขอบคุณ（Khob khun）",
        "多少钱": "ราคาเท่าไร（Raka thao rai）",
        "不要辣": "ไม่เผ็ด（Mai phet）",
        "好的": "ตกลง（Tok long）",
    },
    "韩语": {
        "你好": "안녕하세요（Annyeonghaseyo）",
        "谢谢": "감사합니다（Gamsahamnida）",
        "多少钱": "얼마예요（Eolmayeyo）",
        "好吃": "맛있어요（Massisseoyo）",
        "在哪里": "어디예요（Eodiyeyo）",
    },
}

LANG_MAP: dict[str, str] = {
    "日本": "日语", "东京": "日语", "大阪": "日语", "京都": "日语",
    "泰国": "泰语", "曼谷": "泰语", "清迈": "泰语",
    "韩国": "韩语", "首尔": "韩语",
    "法国": "法语", "巴黎": "法语",
}


class TranslatorInput(BaseModel):
    text: str | None = Field(default=None, description="要翻译的中文")
    target_language: str | None = Field(default=None, description="目标语言：日语/泰语/韩语/法语/英语")
    destination: str | None = Field(default=None, description="目的地（可从目的地推断语言）")


@tool("translate_phrases", args_schema=TranslatorInput)
async def translator_tool(
    text: str | None = None,
    target_language: str | None = None,
    destination: str | None = None,
) -> str:
    """提供旅行常用短语翻译和发音指导。用户询问怎么说某句话、当地语言时调用。"""
    language = (
        target_language
        or (next((v for k, v in LANG_MAP.items() if k in destination), None) if destination else None)
        or "英语"
    )

    phrases = PHRASES.get(language)
    if (not text or "常用" in text or "短语" in text) and phrases:
        listing = "\n".join(f"**{zh}** → {trans}" for zh, trans in phrases.items())
        return f"🗣️ **旅行{language}常用短语**\n\n{listing}\n\n💡 在当地多说几句当地语，会让当地人更热情！"

    llm = create_chat_model(temperature=0.5)

    resp = await llm.ainvoke(
        f'请将"{text}"翻译成{language}，提供：翻译、发音（罗马字/拼音）、适用场合。格式简洁。'
    )
    return f"🗣️ **旅行翻译**\n\n原文：{text}\n目标语言：{language}\n\n{resp.content}"
