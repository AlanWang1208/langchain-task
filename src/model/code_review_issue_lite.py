from pydantic import BaseModel, Field

class CodeReviewIssueLite(BaseModel):
    code: str = Field(description="问题代码")
    issue_type: str = Field(description="问题类型")
