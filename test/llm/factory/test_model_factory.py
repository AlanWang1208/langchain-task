import pytest
from unittest.mock import patch, MagicMock
import os

# 根据实际项目结构调整导入路径
from llm.factory.model_factory import ModelFactory


class TestModelFactory:
    """ModelFactory 单元测试"""

    def setup_method(self):
        """每个测试前重置单例状态，确保测试隔离"""
        ModelFactory._instance = None
        ModelFactory._initialized = False

    # ---------- 单例模式测试 ----------
    def test_singleton_get_instance(self):
        """测试 get_instance 返回同一个实例"""
        factory1 = ModelFactory.get_instance()
        factory2 = ModelFactory.get_instance()
        assert factory1 is factory2

    def test_singleton_direct_construction(self):
        """测试直接构造也返回同一个实例"""
        factory1 = ModelFactory()
        factory2 = ModelFactory()
        assert factory1 is factory2

    # ---------- 默认提供商测试 ----------
    def test_default_provider(self):
        """测试默认提供商为 qwen"""
        factory = ModelFactory.get_instance()
        assert factory.default_provider == "qwen"

    def test_custom_default_provider_on_first_call(self):
        """测试首次调用 get_instance 可设置默认提供商"""
        factory = ModelFactory.get_instance(default_provider="zhipu")
        assert factory.default_provider == "zhipu"

    def test_default_provider_ignored_on_subsequent_calls(self):
        """测试后续调用 get_instance 忽略 default_provider 参数"""
        factory1 = ModelFactory.get_instance(default_provider="zhipu")
        factory2 = ModelFactory.get_instance(default_provider="deepseek")
        assert factory2.default_provider == "zhipu"  # 保持首次设置

    # ---------- 正常获取模型测试 ----------
    @patch("llm.factory.model_factory.init_chat_model")
    @patch("llm.factory.model_factory.os.getenv")
    def test_get_model_default_qwen(self, mock_getenv, mock_init_chat_model):
        """测试默认获取 qwen 模型"""
        # 模拟环境变量
        mock_getenv.side_effect = lambda key: {
            "DASHSCOPE_API_KEY": "test_qwen_key",
            "DASHSCOPE_BASE_URL": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        }.get(key)

        mock_init_chat_model.return_value = MagicMock()

        factory = ModelFactory.get_instance()
        model = factory.get_model()

        mock_init_chat_model.assert_called_once_with(
            api_key="test_qwen_key",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model="qwen-plus",
            model_provider="openai",
            temperature=0.7,
            timeout=30,
            max_tokens=1000,
        )
        assert model == mock_init_chat_model.return_value

    @patch("llm.factory.model_factory.init_chat_model")
    @patch("llm.factory.model_factory.os.getenv")
    def test_get_model_with_provider_zhipu(self, mock_getenv, mock_init_chat_model):
        """测试指定提供商 zhipu"""
        mock_getenv.side_effect = lambda key: {
            "ZHIPU_API_KEY": "test_zhipu_key",
            "ZHIPU_BASE_URL": "https://open.bigmodel.cn/api/paas/v4/",
        }.get(key)

        mock_init_chat_model.return_value = MagicMock()

        factory = ModelFactory.get_instance()
        model = factory.get_model(provider="zhipu")

        mock_init_chat_model.assert_called_once_with(
            api_key="test_zhipu_key",
            base_url="https://open.bigmodel.cn/api/paas/v4/",
            model="glm-4",
            model_provider="openai",
            temperature=0.7,
            timeout=30,
            max_tokens=1000,
        )

    @patch("llm.factory.model_factory.init_chat_model")
    @patch("llm.factory.model_factory.os.getenv")
    def test_get_model_with_provider_alias(self, mock_getenv, mock_init_chat_model):
        """测试使用缩写 ds 获取 deepseek 模型"""
        mock_getenv.side_effect = lambda key: {
            "DEEPSEEK_API_KEY": "test_ds_key",
            "DEEPSEEK_BASE_URL": "https://api.deepseek.com",
        }.get(key)

        mock_init_chat_model.return_value = MagicMock()

        factory = ModelFactory.get_instance()
        model = factory.get_model(provider="ds")

        mock_init_chat_model.assert_called_once_with(
            api_key="test_ds_key",
            base_url="https://api.deepseek.com",
            model="deepseek-chat",
            model_provider="openai",
            temperature=0.7,
            timeout=30,
            max_tokens=1000,
        )

    @patch("llm.factory.model_factory.init_chat_model")
    @patch("llm.factory.model_factory.os.getenv")
    def test_get_model_with_custom_model_name(self, mock_getenv, mock_init_chat_model):
        """测试自定义模型名称"""
        mock_getenv.side_effect = lambda key: {
            "DASHSCOPE_API_KEY": "test_key",
            "DASHSCOPE_BASE_URL": "https://test.url",
        }.get(key)

        mock_init_chat_model.return_value = MagicMock()

        factory = ModelFactory.get_instance()
        model = factory.get_model(model_name="qwen-max")

        mock_init_chat_model.assert_called_once_with(
            api_key="test_key",
            base_url="https://test.url",
            model="qwen-max",
            model_provider="openai",
            temperature=0.7,
            timeout=30,
            max_tokens=1000,
        )

    @patch("llm.factory.model_factory.init_chat_model")
    @patch("llm.factory.model_factory.os.getenv")
    def test_get_model_with_extra_kwargs(self, mock_getenv, mock_init_chat_model):
        """测试传递额外参数覆盖默认值"""
        mock_getenv.side_effect = lambda key: {
            "DASHSCOPE_API_KEY": "test_key",
            "DASHSCOPE_BASE_URL": "https://test.url",
        }.get(key)

        mock_init_chat_model.return_value = MagicMock()

        factory = ModelFactory.get_instance()
        factory.get_model(temperature=0.9, max_tokens=2000, timeout=60)

        mock_init_chat_model.assert_called_once_with(
            api_key="test_key",
            base_url="https://test.url",
            model="qwen-plus",
            model_provider="openai",
            temperature=0.9,
            timeout=60,
            max_tokens=2000,
        )

    # ---------- 异常情况测试 ----------
    @patch("llm.factory.model_factory.os.getenv")
    def test_get_model_missing_api_key(self, mock_getenv):
        """测试缺少 API 密钥时抛出异常"""
        mock_getenv.return_value = None  # 所有环境变量返回 None
        factory = ModelFactory.get_instance()

        with pytest.raises(ValueError, match="环境变量 DASHSCOPE_API_KEY 或 DASHSCOPE_BASE_URL 缺失"):
            factory.get_model()

    @patch("llm.factory.model_factory.os.getenv")
    def test_get_model_missing_base_url(self, mock_getenv):
        """测试缺少 Base URL 时抛出异常"""
        mock_getenv.side_effect = lambda key: {
            "DASHSCOPE_API_KEY": "test_key",
            "DASHSCOPE_BASE_URL": None,
        }.get(key)

        factory = ModelFactory.get_instance()

        with pytest.raises(ValueError, match="环境变量 DASHSCOPE_API_KEY 或 DASHSCOPE_BASE_URL 缺失"):
            factory.get_model()

    def test_get_model_unsupported_provider(self):
        """测试不支持的厂商抛出异常"""
        factory = ModelFactory.get_instance()

        with pytest.raises(ValueError, match="不支持的厂商: 'unknown'. 可用: .*"):
            factory.get_model(provider="unknown")

    def test_get_model_missing_provider_config(self):
        """测试厂商配置缺失（模拟 _PROVIDER_CONFIGS 中缺少项）"""
        factory = ModelFactory.get_instance()
        # 临时移除一个配置
        original_configs = factory._PROVIDER_CONFIGS.copy()
        try:
            factory._PROVIDER_CONFIGS.pop("zhipu", None)
            with pytest.raises(ValueError, match="厂商 'zhipu' 配置缺失"):
                factory.get_model(provider="zhipu")
        finally:
            factory._PROVIDER_CONFIGS = original_configs