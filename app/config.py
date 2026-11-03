import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

provider = os.getenv("LLM_PROVIDER", "ollama")

OLLAMA_CONFIG = {
    "provider": "ollama",
    "api_key": "ollama",
    "base_url": os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").removesuffix("/v1").rstrip("/"),
    "model": os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
    "temperature": 0.7,
    "label": "Ollama 本地",
}

DEEPSEEK_CONFIG = {
    "provider": "deepseek",
    "temperature": 0.7,
    "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
    "base_url": "https://api.deepseek.com/v1",
    "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    "label": "DeepSeek 云端",
}

llm_config = DEEPSEEK_CONFIG if provider == "deepseek" else OLLAMA_CONFIG

print(f"\n大模型：{llm_config['label']} → {llm_config['model']}")
if provider == "deepseek" and not llm_config["api_key"]:
    print(" DEEPSEEK_API_KEY 未配置！请在 .env 中填入 API Key")
elif provider == "ollama":
    print(f"   Ollama 地址：{llm_config['base_url']}")
    print(f"   请确认已执行：ollama pull {llm_config['model']}")


class ServerConfig:
    port = int(os.getenv("PORT", "3000"))
    cors_origin = os.getenv("CORS_ORIGIN", "http://localhost:5173")


class AgentConfig:
    temperature = float(os.getenv("CHAT_TEMPERATURE", "0.7"))
    max_iterations = int(os.getenv("MAX_ITERATIONS", "6"))


class WeatherConfig:
    api_key = os.getenv("WEATHER_API_KEY", "")


class Config:
    llm = llm_config
    server = ServerConfig()
    agent = AgentConfig()
    weather = WeatherConfig()


config = Config()
