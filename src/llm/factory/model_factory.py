import os
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

from utils.log_helper import log

load_dotenv()

class ModelFactory:
    """
    单例的 LLM 客户端工厂，返回 LangChain 聊天模型实例。
    支持厂商：zhipu（智谱）、deepseek（深度求索）、qwen（通义千问）.
    如需接入其他模型，请扩展此方法
    使用 get_instance() 获取唯一实例。
    """

    _instance = None
    _initialized = False

    # 厂商配置：环境变量映射 + 默认模型名称
    _PROVIDER_CONFIGS = {
        "zhipu": {
            "api_key_env": "ZHIPU_API_KEY",
            "base_url_env": "ZHIPU_BASE_URL",
            "default_model": "glm-4"               # 智谱的默认模型
        },
        "deepseek": {
            "api_key_env": "DEEPSEEK_API_KEY",
            "base_url_env": "DEEPSEEK_BASE_URL",
            "default_model": "deepseek-chat"        # DeepSeek 的默认模型
        },
        "qwen": {
            "api_key_env": "DASHSCOPE_API_KEY",
            "base_url_env": "DASHSCOPE_BASE_URL",
            "default_model": "qwen-plus"            # 千问的默认模型
        }
    }

    _PROVIDER_ALIASES = {
        "zhipu": "zhipu", "zp": "zhipu",
        "deepseek": "deepseek", "ds": "deepseek",
        "qwen": "qwen", "qw": "qwen"
    }

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, default_provider="qwen"):
        if not self._initialized:
            self.default_provider = default_provider
            self._initialized = True

    @classmethod
    def get_instance(cls, default_provider="qwen"):
        if cls._instance is None:
            cls._instance = cls(default_provider)
        return cls._instance

    def get_model(self, provider=None, model_name=None, **kwargs):
        """
        返回 LangChain 聊天模型实例。
        :param provider: 厂商名称或缩写，默认使用 self.default_provider
        :param model_name: 具体模型名称，若为 None 则使用配置中的 default_model
        :param kwargs: 传递给 init_chat_model 的其他参数（如 temperature, timeout 等）
        :return: 聊天模型实例
        """
        if provider is None:
            provider = self.default_provider

        provider_key = provider.lower().strip()
        canonical_name = self._PROVIDER_ALIASES.get(provider_key)
        if canonical_name is None:
            raise ValueError(f"不支持的厂商: '{provider}'. 可用: {list(self._PROVIDER_ALIASES.keys())}")

        config = self._PROVIDER_CONFIGS.get(canonical_name)
        if config is None:
            raise ValueError(f"厂商 '{canonical_name}' 配置缺失")

        api_key = os.getenv(config["api_key_env"])
        base_url = os.getenv(config["base_url_env"])

        if not api_key or not base_url:
            raise ValueError(f"环境变量 {config['api_key_env']} 或 {config['base_url_env']} 缺失")

        # 确定模型名称：优先使用传入的 model_name，否则使用默认模型
        _model = model_name or config["default_model"]

        log.info("###模型名称->"+_model)

        # 合并默认参数与用户传入参数
        params = {
            "api_key": api_key,
            "base_url": base_url,
            "model": _model,
            "model_provider": "openai",
            "temperature": 0.7,
            "timeout": 30,
            "max_tokens": 1000,
            **kwargs
        }

        return init_chat_model(**params)



