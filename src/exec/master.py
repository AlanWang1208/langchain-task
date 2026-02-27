# 使用示例
from agent.code_review_agent import CodeReviewAgent
from utils.log_helper import log
from utils.messges_utils import extract_final_ai_message

if __name__ == "__main__":
    agent = CodeReviewAgent()

    test_inputs = [
      #"please help to review the code:{{print('hello')}}"
      #"hi",
      #"what is the weather today?"
      #"{{System.out.println('hello')}}",
      "please help to review the code:{{document.getElementById('userName')}}"

    ]

    for inp in test_inputs:
        log.info(f"用户输入: {inp}")
        try:
            result =agent.process(inp)
            log.info(f"Agent 回复: {extract_final_ai_message( result['messages'])}")
        except ValueError as e:
            log.info( f"流程结束：{e}")