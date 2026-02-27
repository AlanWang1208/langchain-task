from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from constants.messages_constants import SYSTEM_MESSAGE_LANGUAGE_DETECTION
from llm.factory.model_factory import ModelFactory
from utils.log_helper import log

_model = ModelFactory.get_instance().get_model("deepseek")

_prompt = ChatPromptTemplate.from_messages([
    SYSTEM_MESSAGE_LANGUAGE_DETECTION,
    ("human", "{user_input}")
])

_chain = _prompt | _model | StrOutputParser()

@tool
def check_language_support(user_input: str) -> str:
    """
       检测用户输入中代码的编程语言，仅支持 Python 和 Java。

       Args:
           user_input (str): 用户的原始输入，可能包含代码片段或问题描述。

       Returns:
           str: 如果检测到的语言为支持的语言（'python' 或 'java'），返回小写语言名称。

       Raises:
           ValueError: 如果语言不支持（例如识别到其他语言）或识别服务不可用，
                       抛出异常，异常信息可直接向用户展示，并终止后续代码审查。
       """
    try:
        log.info("###语言检测->大模型检测")
        detected = _chain.invoke({"user_input": user_input}).strip().lower()
        log.info("###语言检测->大模型检测结果->"+detected)
    except Exception as e:
        log.error("###语言检测->大模型检测失败!" ,e)
        raise ValueError("语言识别服务暂时不可用，请稍后重试。") from e

    supported = ["python", "java"]
    if detected in supported:
        return detected
    else:
        raise ValueError(f"语言检测失败!当前仅支持 Python 和 Java。识别到的语言为 '{detected}'。")