"""
日志模型
app/modules/audit/models.py
"""
from datetime import datetime
from sqlalchemy import Column, func, String, Integer, BigInteger,Text, DateTime
from app.core.database import Base


class SysAccessLog(Base):
    """系统访问日志（技术视角）"""
    __tablename__ = "sys_access_log"

    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    request_id = Column(String(36), index=True, comment="请求唯一标识")
    request_uri = Column(String(255), comment="请求URI")
    request_method = Column(String(10), comment="请求方法(GET/POST/PUT/DELETE)")
    request_params = Column(Text, nullable=True, comment="请求参数(query)")
    http_status = Column(Integer, comment="响应状态码")
    execution_time = Column(Integer, comment="请求耗时(毫秒)")
    ip = Column(String(50), nullable=True, comment="客户端IP")
    user_agent = Column(Text, nullable=True, comment="客户端UA")
    create_by = Column(BigInteger, nullable=True, comment='操作人ID')
    handler = Column(String(100), nullable=True, comment="处理器函数名")
    create_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment='创建时间')
    request_body = Column(Text, nullable=True, comment="请求体（脱敏）")

    def __repr__(self):
        return f"<SysAccessLog(request_id={self.request_id}, uri={self.request_uri})>"


class BizAuditLog(Base):
    """业务审计日志（业务视角）"""
    __tablename__ = "biz_audit_log"

    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    request_id = Column(String(36), index=True, comment="请求唯一标识")
    operator_id = Column(BigInteger, nullable=True, comment='操作人ID')
    operator_name = Column(String(50), comment="操作人名称")
    module = Column(String(50), comment="业务模块(user/role/order)")
    operation_type = Column(String(20), comment="操作类型(CREATE/UPDATE/DELETE/QUERY)")
    business_id = Column(String(36), comment="业务ID")
    operation_content = Column(Text, comment="操作内容")
    operation_result = Column(String(10), default="SUCCESS", comment="操作结果(SUCCESS/FAILURE)")
    error_msg = Column(Text, nullable=True, comment="错误信息")
    ip_address = Column(String(50), nullable=True, comment="操作IP")
    create_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment='创建时间')

    def __repr__(self):
        return f"<BizAuditLog(module={self.module}, operator={self.operator_name})>"


class SysErrorLog(Base):
    """系统错误日志"""
    __tablename__ = "sys_error_log"

    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    request_id = Column(String(36), index=True, comment="请求唯一标识")
    error_code = Column(String(20), comment="错误码")
    error_msg = Column(Text, comment="错误信息")
    error_stack = Column(Text, comment="异常栈信息")
    request_uri = Column(String(255), nullable=True, comment="请求URI")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")

    def set_error_stack(self, stack: str):
        """异常栈脱敏（简单版）"""
        import re
        # 隐藏文件路径和敏感信息
        stack = re.sub(r"File \"(.+\/)([^\/]+)\"", r"File \"***\/\2\"", stack)
        stack = re.sub(r"(password|token|secret)=[^\s&]+", r"\1=***", stack)
        self.error_stack = stack

    def __repr__(self):
        return f"<SysErrorLog(request_id={self.request_id}, code={self.error_code})>"