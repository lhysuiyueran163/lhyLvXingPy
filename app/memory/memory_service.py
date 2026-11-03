from langchain_core.messages import BaseMessage

MAX_HISTORY = 20

_sessions: dict[str, list[BaseMessage]] = {}


def get_history(user_id: str) -> list[BaseMessage]:
    return _sessions.get(user_id, [])


def add_message(user_id: str, message: BaseMessage) -> None:
    history = _sessions.get(user_id, [])
    history.append(message)
    if len(history) > MAX_HISTORY:
        del history[: len(history) - MAX_HISTORY]
    _sessions[user_id] = history


def clear_history(user_id: str) -> None:
    _sessions.pop(user_id, None)


def list_sessions() -> list[dict]:
    return [{"userId": uid, "messageCount": len(msgs)} for uid, msgs in _sessions.items()]
