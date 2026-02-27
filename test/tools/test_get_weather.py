import pytest
from tools.get_weather import get_weather

@pytest.mark.parametrize("city, expected", [
    ("sf", "It's always sunny in sf!"),
    ("北京", "It's always sunny in 北京!"),
    ("", "It's always sunny in !"),
    ("New York", "It's always sunny in New York!"),
])
def test_get_weather(city, expected):
    """测试 get_weather 工具：应返回包含城市名称的固定格式字符串。"""
    assert get_weather.run(city) == expected