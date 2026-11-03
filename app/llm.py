"""Shared model configuration for the agent and model-backed tools."""
from urllib.parse import urlparse
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from app.config import config


def create_chat_model(temperature=0.5, **kwargs):
    if config.llm["provider"] == "deepseek":
        return ChatOpenAI(model=config.llm["model"], api_key=config.llm["api_key"],
                          base_url=config.llm["base_url"], temperature=temperature, **kwargs)
    # Local requests must not go through proxies inherited from a terminal.
    local = urlparse(config.llm["base_url"]).hostname in {"localhost", "127.0.0.1", "::1"}
    return ChatOllama(model=config.llm["model"], base_url=config.llm["base_url"],
                      temperature=temperature,
                      client_kwargs={"trust_env": not local, "timeout": 180.0}, **kwargs)
