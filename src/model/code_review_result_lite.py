# 包装多个问题的输出模型（便于解析）
from typing import List

from pydantic import Field, BaseModel

from model.code_review_issue_lite import CodeReviewIssueLite


class CodeReviewResultLite(BaseModel):
    issues: List[CodeReviewIssueLite] = Field(description="审查发现的问题列表")