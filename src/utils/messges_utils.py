
from typing import List, Union
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, ToolMessage

def extract_final_ai_message(messages: List[BaseMessage]) -> str:
    """
    从消息列表中提取最后一条 AI 消息的内容。
    如果不存在 AI 消息，返回空字符串。
    """
    ai_messages = [msg for msg in messages if isinstance(msg, AIMessage)]
    if not ai_messages:
        return ""
    return ai_messages[-1].content

def extract_all_ai_messages(messages: List[BaseMessage]) -> List[str]:
    """提取所有 AI 消息的内容，按顺序返回列表。"""
    return [msg.content for msg in messages if isinstance(msg, AIMessage)]

def extract_tool_calls(messages: List[BaseMessage]) -> List[dict]:
    """提取所有工具调用信息（从 AI 消息中）。"""
    tool_calls = []
    for msg in messages:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            tool_calls.extend(msg.tool_calls)
    return tool_calls

def format_messages_for_log(messages: List[BaseMessage]) -> List[dict]:
    """将消息列表转换为字典格式，便于日志记录或序列化。"""
    return [msg.dict() for msg in messages]

def extract_user_query(messages: List[BaseMessage]) -> str:
    """提取第一条人类消息的内容（通常是用户输入）。"""
    for msg in messages:
        if isinstance(msg, HumanMessage):
            return msg.content
    return ""