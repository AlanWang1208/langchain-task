import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from constants.messages_constants import FIX_PROMPT_TEMPLATE
from model.code_review_issue_full import CodeReviewIssueFull
from model.code_review_issue_lite import CodeReviewIssueLite
from utils.log_helper import log
from llm.factory.model_factory import ModelFactory


def generate_fixes_concurrently(
    issues: List[CodeReviewIssueLite],
    full_context: str,
    max_workers: int = 5
) -> List[CodeReviewIssueFull]:
    """
    并发地为每个问题生成修复代码，使用 PydanticOutputParser 直接解析为 CodeReviewIssueFull。

    Args:
        issues: 问题列表（不包含修复代码）
        full_context: 用户输入的完整代码上下文
        max_workers: 最大并发数

    Returns:
        List[CodeReviewIssueFull] 每个元素包含 code, issue_type, suggested_fix
    """
    if not issues:
        return []

    parser = PydanticOutputParser(pydantic_object=CodeReviewIssueFull)

    def _generate_fix_with_index(issue: CodeReviewIssueLite, idx: int) -> CodeReviewIssueFull:
        thread_id = threading.current_thread().ident
        log.info(f"开始修复问题 index={idx}, thread={thread_id}, issue_type={issue.issue_type}")
        try:
            fix_prompt = PromptTemplate(
                template=FIX_PROMPT_TEMPLATE,
                input_variables=["full_context", "issue_type", "code"],
                partial_variables={"format_instructions": parser.get_format_instructions()}
            )
            model = ModelFactory.get_instance().get_model()
            chain = fix_prompt | model | parser
            result: CodeReviewIssueFull = chain.invoke({
                "full_context": full_context,
                "issue_type": issue.issue_type,
                "code": issue.code
            })
            log.info(f"完成修复问题 index={idx}, thread={thread_id}, issue_type={issue.issue_type}")
            return result
        except Exception as e:
            log.error(f"生成修复代码失败 index={idx}, thread={thread_id}, issue_type={issue.issue_type}, error={e}")
            return CodeReviewIssueFull(
                code=issue.code,
                issue_type=issue.issue_type,
                suggested_fix=""
            )

    results = [None] * len(issues)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(_generate_fix_with_index, issue, idx): idx
            for idx, issue in enumerate(issues)
        }
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                full_issue = future.result()
            except Exception as e:
                log.error(f"处理修复任务时发生未预期异常 index={idx}, error={e}")
                full_issue = CodeReviewIssueFull(
                    code=issues[idx].code,
                    issue_type=issues[idx].issue_type,
                    suggested_fix=""
                )
            results[idx] = full_issue
    return results