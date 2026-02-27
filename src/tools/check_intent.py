from langchain_core.tools import tool

from constants.messages_constants import SYSTEM_MESSAGE_INTENT
from llm.factory.model_factory import ModelFactory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from utils.log_helper import log

# 获取模型实例（单例）
_model = ModelFactory.get_instance().get_model()

# 构建意图判断链
_intent_prompt = ChatPromptTemplate.from_messages([
    SYSTEM_MESSAGE_INTENT,
    ("human", "{user_input}")
])
_intent_chain = _intent_prompt | _model | StrOutputParser()

@tool
def check_intent(user_input: str) -> str:
    """
    检测用户的意图是否为代码审查

    Args:
        user_input (str): 用户的原始输入，可能包含代码片段或问题描述。

    Returns:
        str: 如果用户的意图是代码审查，返回INTENT_OK，否则返回提示消息：
        您好，我是一个代码审查助手，专门帮助审查代码.如果您有代码需要审查，请提供代码片段，谢谢！
    """
    # 代码审查相关的关键词（中英文）
    keywords = [
        # 中文关键词
        '代码', '审查', 'review', 'code review', '代码质量', '代码风格',
        '代码检查', '代码评估', '代码审核', '代码分析', '代码审查',
        'code check', 'quality check', '静态分析', 'lint',
        # 英文关键词
        'code', 'review', 'audit', 'inspect', 'examine', 'code quality',
        'static analysis', 'code style', 'check code', 'evaluate code',
        'review code'
    ]

    log.info("###意图审查->关键字匹配")

    user_input_lower = user_input.lower()
    if any(kw in user_input_lower for kw in keywords):
        log.info("###意图审查结果->INTENT_OK")
        return "INTENT_OK"

    # 关键词未匹配，使用大模型进一步判断
    try:
        log.info("###进入意图审查->大模型审查")
        result = _intent_chain.invoke({"user_input": user_input}).strip().upper()
        if result == "YES":
            log.info("###意图审查结果->INTENT_OK")
            return "INTENT_OK"
        else:
            log.info("###意图审查结果->INTENT_FAILED")
            return "您好，我是一个代码审查助手，专门帮助审查代码.如果您有代码需要审查，请提供代码片段，谢谢！"
    except Exception as e:
        # 如果大模型调用失败，保守地返回提示消息
        log.error("###意图审查结果->INTENT_FAILED",e)
        return "您好，我是一个代码审查助手，专门帮助审查代码.如果您有代码需要审查，请提供代码片段，谢谢！"
