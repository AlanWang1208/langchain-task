from typing import List

from pydantic import Field, BaseModel

class CodeReviewIssueFull(BaseModel):
    code: str = Field(description="问题代码")
    issue_type: str = Field(description="问题类型")
    suggested_fix: str = Field(description="修复后的代码")