import pytest

from tools.check_intent import check_intent
# 友好的提示消息常量（应与工具中定义的一致）
INTENT_NOT_CODE_REVIEW_MESSAGE="您好，我是一个代码审查助手，专门帮助审查代码.如果您有代码需要审查，请提供代码片段，谢谢！"

@pytest.mark.parametrize("user_input, expected", [
    # 匹配意图的用例（应返回 "INTENT_OK"）
    ("请帮我 review 这段代码", "INTENT_OK"),
    ("审查一下代码", "INTENT_OK"),
    ("代码质量检查", "INTENT_OK"),
    ("帮我做静态分析", "INTENT_OK"),
    ("can you review my code", "INTENT_OK"),
    ("code review needed", "INTENT_OK"),
    ("请进行代码审查", "INTENT_OK"),
    ("CODE QUALITY check", "INTENT_OK"),           # 测试大小写
    ("帮我检查代码风格", "INTENT_OK"),
    ("帮我审核一下代码", "INTENT_OK"),
    ("需要进行代码评估", "INTENT_OK"),
    ("请做代码分析", "INTENT_OK"),
    ("review code", "INTENT_OK"),
    ("audit the code", "INTENT_OK"),
    ("inspect this code", "INTENT_OK"),
    ("examine the code", "INTENT_OK"),
    ("code check", "INTENT_OK"),
    ("静态分析", "INTENT_OK"),                      # 纯关键词
    ("代码审查", "INTENT_OK"),
    ("review", "INTENT_OK"),                       # 单个关键词
    ("code", "INTENT_OK"),                          # 单个关键词
    # 不匹配意图的用例（应返回友好提示消息）
    ("今天天气怎么样", INTENT_NOT_CODE_REVIEW_MESSAGE),
    ("你好", INTENT_NOT_CODE_REVIEW_MESSAGE),
    ("帮我写首诗", INTENT_NOT_CODE_REVIEW_MESSAGE),
    ("", INTENT_NOT_CODE_REVIEW_MESSAGE),           # 空字符串
    (" ", INTENT_NOT_CODE_REVIEW_MESSAGE),          # 空格
    ("random text with no keywords", INTENT_NOT_CODE_REVIEW_MESSAGE),
    ("我需要帮助", INTENT_NOT_CODE_REVIEW_MESSAGE),
    ("请告诉我时间", INTENT_NOT_CODE_REVIEW_MESSAGE),
])
def test_check_intent(user_input, expected):
    """测试 check_intent 工具：应正确识别意图并返回相应字符串。"""
    assert check_intent.run(user_input) == expected