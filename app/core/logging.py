"""
结构化日志配置文件
app/core/logging.py
"""
import sys
import logging
import structlog
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler
from pathlib import Path
from contextvars import ContextVar

from app.config.config import settings

# ========== 全局上下文变量 ==========
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")
user_context_ctx: ContextVar[dict] = ContextVar("user_context", default={})


# ========== 日志目录初始化 ==========
def init_log_dir():
    """初始化日志目录（生产环境）"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    return log_dir

# 在 logging.py 顶部添加自定义异常处理器
def format_exception_with_utf8(_, __, event_dict):
    """修复异常栈中的中文显示"""
    if 'exception' in event_dict:
        # 将异常栈转为UTF-8编码的字符串
        if isinstance(event_dict['exception'], (list, tuple)):
            event_dict['exception'] = '\n'.join(
                line.encode('utf-8').decode('utf-8') if isinstance(line, str) else str(line)
                for line in event_dict['exception']
            )
    return event_dict

# ========== 脱敏处理器（复用原有脱敏逻辑） ==========
def desensitize_processor(_, __, event_dict):
    """structlog 脱敏处理器：自动脱敏敏感字段"""
    from app.core.desensitize import desensitize_text

    # 遍历所有字段进行脱敏
    for key, value in event_dict.items():
        if isinstance(value, str):
            event_dict[key] = desensitize_text(value)
    return event_dict


# ========== 上下文绑定处理器 ==========
def bind_contextvars_processor(_, __, event_dict):
    """自动绑定request_id和user_context到日志"""
    event_dict["request_id"] = request_id_ctx.get()
    event_dict["user_context"] = user_context_ctx.get()
    event_dict["env"] = settings.ENVIRONMENT
    return event_dict


# ========== 核心配置函数 ==========
def configure_structlog():
    """配置structlog（企业级完整配置）"""
    # 1. 基础处理器（所有环境共享）
    base_processors = [
        structlog.contextvars.merge_contextvars,  # 合并上下文变量
        bind_contextvars_processor,  # 绑定request_id/user_context
        desensitize_processor,  # 敏感数据脱敏
        structlog.processors.add_log_level,  # 添加日志级别
        structlog.processors.TimeStamper(fmt="iso"),  # ISO格式时间戳
        structlog.processors.StackInfoRenderer(),  # 堆栈信息
        structlog.processors.format_exc_info,  # 异常栈信息
        format_exception_with_utf8,  # 新增：修复异常栈中文
    ]

    # 2. 配置标准logging（用于uvicorn/第三方库日志）
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG)
    root_logger.handlers.clear()  # 清空默认处理器

    # 3. 按环境配置处理器
    if settings.ENVIRONMENT == "production":
        # 生产环境：JSON输出 + 文件轮转 + 控制台输出
        # 3.1 文件处理器（轮转）
        log_dir = init_log_dir()
        file_handler = RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,  # 保留10个备份
            encoding="utf-8"
        )
        file_handler.setFormatter(logging.Formatter("%(message)s"))

        # 3.2 控制台处理器（JSON）
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter("%(message)s"))

        # 3.3 添加处理器
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        # 3.4 structlog最终处理器（JSON）
        final_processors = base_processors + [
            # 关键修改：ensure_ascii=False 保留中文
            structlog.processors.JSONRenderer(ensure_ascii=False)
        ]
    else:
        # 开发环境：彩色控制台输出
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter("%(message)s"))
        root_logger.addHandler(console_handler)

        # structlog最终处理器（彩色）
        final_processors = base_processors + [
            structlog.dev.ConsoleRenderer(colors=True)  # 彩色输出
        ]

    # 4. 初始化structlog
    structlog.configure(
        processors=final_processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # 5. 禁用uvicorn默认的access log（避免重复）
    logging.getLogger("uvicorn.access").disabled = True


# ========== 日志器获取函数 ==========
def get_logger(name: str = "app") -> structlog.BoundLogger:
    """获取结构化日志器（统一入口）"""
    return structlog.get_logger(name)


# ========== 异步日志上下文管理器 ==========
@asynccontextmanager
async def log_context(request_id: str = None, user_context: dict = None):
    """
    日志上下文管理器（协程安全）
    使用示例：
    async with log_context(request_id="xxx", user_context={"id": 1}):
        logger.info("操作日志")
    """
    token1 = token2 = None
    try:
        if request_id:
            token1 = request_id_ctx.set(request_id)
        if user_context:
            token2 = user_context_ctx.set(user_context)
        yield
    finally:
        if token1:
            request_id_ctx.reset(token1)
        if token2:
            user_context_ctx.reset(token2)