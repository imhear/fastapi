# app/modules/log/models.py
from sqlalchemy import Column, String, DateTime, JSON, Text, func
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID

class BusinessLog(Base):
    __tablename__ = "business_log"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    create_time = Column(DateTime, server_default=func.now(), nullable=False)
    operation_type = Column(String(50), nullable=False, comment="操作类型，如 CREATE、UPDATE、DELETE、LOGIN")
    module = Column(String(50), nullable=False, comment="模块名，如 user、role")
    operator_id = Column(String(36), nullable=True, comment="操作人ID")
    operator_name = Column(String(64), nullable=True, comment="操作人用户名")
    content = Column(JSON, nullable=True, comment="操作内容（结构化数据）")
    result = Column(String(10), nullable=False, comment="结果：SUCCESS / FAILURE")
    error_detail = Column(Text, nullable=True, comment="失败详情")
    ip_address = Column(String(45), nullable=True, comment="客户端IP")
    user_agent = Column(String(255), nullable=True, comment="User-Agent")
    level = Column(String(20), nullable=False, default="INFO", comment="日志级别：DEBUG/INFO/WARN/ERROR/AUDIT")
    request_id = Column(String(64), nullable=True, comment="请求唯一标识（链路追踪）")
    api_path = Column(String(255), nullable=True, comment="操作对应的API路径")
    http_method = Column(String(10), nullable=True, comment="HTTP方法：GET/POST/PUT/DELETE")