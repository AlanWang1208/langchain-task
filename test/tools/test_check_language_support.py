import pytest
from unittest.mock import patch, MagicMock
from langchain.tools import tool

from tools.check_language_support import check_language_support  # 根据实际路径调整


class TestCheckLanguageSupport:
    """测试 check_language_support 工具"""

    @patch("tools.check_language_support._chain")
    def test_supported_language_python(self, mock_chain):
        """测试支持的语言（python）应返回 'python'"""
        mock_chain.invoke.return_value = "python"

        # 注意：直接传递字符串，不要使用关键字参数
        result = check_language_support.run("some python code")
        assert result == "python"
        mock_chain.invoke.assert_called_once_with({"user_input": "some python code"})

    @patch("tools.check_language_support._chain")
    def test_supported_language_java(self, mock_chain):
        """测试支持的语言（java）应返回 'java'"""
        mock_chain.invoke.return_value = "java"

        result = check_language_support.run("public class Test {}")
        assert result == "java"

    @patch("tools.check_language_support._chain")
    def test_unsupported_language(self, mock_chain):
        """测试不支持的语言应抛出 ValueError 并提示仅支持 Python/Java"""
        mock_chain.invoke.return_value = "ruby"

        with pytest.raises(ValueError) as exc_info:
            check_language_support.run("puts 'hello'")

        assert "当前仅支持 Python 和 Java" in str(exc_info.value)
        assert "ruby" in str(exc_info.value)

    @patch("tools.check_language_support._chain")
    def test_model_call_exception(self, mock_chain):
        """测试模型调用异常时应抛出服务不可用错误"""
        mock_chain.invoke.side_effect = Exception("Model timeout")

        with pytest.raises(ValueError) as exc_info:
            check_language_support.run("any input")

        assert "语言识别服务暂时不可用" in str(exc_info.value)

    @patch("tools.check_language_support._chain")
    def test_model_return_with_whitespace(self, mock_chain):
        """测试模型返回带空格/换行的语言名称应被正确清理"""
        mock_chain.invoke.return_value = " python\n"

        result = check_language_support.run("print('hello')")
        assert result == "python"

    @patch("tools.check_language_support._chain")
    def test_model_return_mixed_case(self, mock_chain):
        """测试模型返回大小写混合的语言名称应被转为小写"""
        mock_chain.invoke.return_value = "Java"

        result = check_language_support.run("System.out.println")
        assert result == "java"

    @patch("tools.check_language_support._chain")
    def test_empty_user_input(self, mock_chain):
        """测试空用户输入，模拟模型可能返回 'unknown' 的情况"""
        mock_chain.invoke.return_value = "unknown"

        with pytest.raises(ValueError) as exc_info:
            check_language_support.run("")

        assert "unknown" in str(exc_info.value)