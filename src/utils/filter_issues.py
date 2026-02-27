from typing import List

from model.code_review_issue_lite import CodeReviewIssueLite
from utils.log_helper import log

def filter_issues(issues: List[CodeReviewIssueLite], categories: List[str]) -> List[CodeReviewIssueLite]:
    """
    过滤掉 issue_type 不在 categories 列表中的问题，并将被过滤的 issue 打印到日志。

    Args:
        issues: 原始 issue 列表
        categories: 有效问题类型列表

    Returns:
        过滤后的 issue 列表
    """
    log.info("###进入过滤器")
    filtered = []
    for issue in issues:
        if issue.issue_type in categories:
            filtered.append(issue)
        else:
            # 将被过滤的 issue 信息打印到日志
            log.info(f"过滤掉 issue: type='{issue.issue_type}', code='{issue.code}'")
    return filtered