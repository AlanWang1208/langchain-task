from typing import List, Dict

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool

from constants.messages_constants import SYSTEM_MESSAGE_DO_CODE_REVIEW
from llm.factory.model_factory import ModelFactory
from model.code_review_result_full import CodeReviewResultFull
from model.code_review_result_lite import CodeReviewResultLite
from utils.filter_issues import filter_issues
from utils.generate_fixes_concurrently import generate_fixes_concurrently
from utils.log_helper import log


@tool
def code_review(user_input: str) -> CodeReviewResultFull:
    """
    对用户输入的代码片段进行代码审查，根据以下预定义关键词对代码进行审查
    1.安全规范
    2.代码命名
    3.代码风格
    4.代码设计
    5.并发和现场安全
    6.集合处理
    7.数据库开发
    8.缓存开发
    9.日志规范
    10.异常处理
    11.测试规范
    12.工程结构

    Args:
        user_input (str): 用户的原始输入，可能包含代码片段或问题描述。

    Returns:
        List[Dict]: 问题集合，每个字典包含 code, issue_type, suggested_fix 三个字段。
    """
    # 初始化大模型（可根据需要调整模型和参数）

    llm = ModelFactory.get_instance().get_model()
    log.info("###代码审查")
    # 预定义问题类型列表
    categories = [
        "安全规范",
        "代码命名",
        "代码风格",
        "代码设计",
        "并发和现场安全",
        "集合处理",
        "数据库开发",
        "缓存开发",
        "日志规范",
        "异常处理",
        "测试规范",
        "工程结构"
    ]
    categories_str = ", ".join(categories)

    # 输出解析器
    parser = PydanticOutputParser(pydantic_object=CodeReviewResultLite)

    # 构建提示模板
    prompt = PromptTemplate(
        template=SYSTEM_MESSAGE_DO_CODE_REVIEW,
        input_variables=["user_input", "categories"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    # 创建链并执行
    chain = prompt | llm | parser
    result = chain.invoke({"user_input": user_input, "categories": categories_str})


    # 使用过滤函数过滤无效的问题类型
    filtered_issues = filter_issues(result.issues, categories)

    # 并发生成修复代码，得到完整的 CodeReviewIssueFull 列表
    full_issues = generate_fixes_concurrently(filtered_issues, user_input, max_workers=5)

    log.info(f"代码审查完成，共处理 {len(full_issues)} 个问题")
    return CodeReviewResultFull(issues=full_issues)


