import logging
import sys

# 过滤器：为所有日志记录添加默认的 class_name 属性
class ClassInjectFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'class_name'):
            record.class_name = '?'
        return True

# 创建日志器
log = logging.getLogger('loghelper')
log.setLevel(logging.INFO)

# 控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# 日志格式：加入 filename 字段，同时保留 class_name
formatter = logging.Formatter(
    fmt='%(asctime)s - %(name)s - %(filename)s - %(class_name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(formatter)

# 将过滤器添加到处理器
console_handler.addFilter(ClassInjectFilter())

log.addHandler(console_handler)
log.propagate = False

# 适配器函数：为指定类创建带类名的日志适配器
def get_logger_for_class(cls):
    """
    返回一个 LoggerAdapter，自动在 extra 中设置 class_name 为 cls.__name__。
    使用示例：
        class MyClass:
            logger = get_logger_for_class(MyClass)
            def do_something(self):
                self.logger.info("操作成功")
    """
    class ClassLoggerAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            extra = kwargs.get('extra', {})
            extra['class_name'] = cls.__name__
            kwargs['extra'] = extra
            return msg, kwargs

    return ClassLoggerAdapter(log, {})