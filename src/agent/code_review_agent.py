from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from constants.messages_constants import SYSTEM_MESSAGE_CODE_REVIEW
from llm.factory.model_factory import ModelFactory
from tools.check_intent import check_intent
from tools.check_language_support import check_language_support
from tools.code_review import code_review
from utils.log_helper import log


class CodeReviewAgent:
    """
    代码审查 Agent
    集成意图检测、语言支持检查和代码审查工具。
    """
    def __init__(self, model=None, tools=None):
        """
        初始化 Agent。
        :param model: 语言模型实例，默认使用 ModelFactory 获取的默认模型
        :param tools: 工具列表，默认使用三个预定义工具

        """
        self.model = model or ModelFactory.get_instance().get_model()
        self.tools = tools or [check_intent,check_language_support,code_review]

        # 使用 create_agent 创建 ReAct Agent
        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=SYSTEM_MESSAGE_CODE_REVIEW
        )


    # def process(self, user_input: str) -> Any:
    #     """
    #     处理用户输入，返回最终回复。
    #     若流程中抛出 ValueError（如语言不支持），则返回友好的错误消息。
    #     """
    #     try:
    #
    #        human_messages=HumanMessage(content=user_input)
    #        return self.agent.invoke({"messages": [human_messages]})
    #     except ValueError as e:
    #         return f"流程中断：{e}"

    def process(self, user_input: str) -> Any:
        """
        处理用户输入，返回最终回复。
        若流程中抛出 ValueError，则将其重新抛出，由调用者处理。
        """
        try:
            human_messages = HumanMessage(content=user_input)
            return self.agent.invoke({"messages": [human_messages]})
        except ValueError as e:
            log.error(f"处理用户输入时发生ValueError: {e}")
            raise  # 重新抛出异常，让上层调用者处理

