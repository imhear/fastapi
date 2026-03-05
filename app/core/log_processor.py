# app/core/log_processor.py（最终最终版）
import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from logging.handlers import TimedRotatingFileHandler
from collections import defaultdict
from app.core.database import AsyncSessionFactory
from app.modules.log.models import BusinessLog

# ===================== 1. 日志轮转配置（解决文件无限增长） =====================
logger = logging.getLogger("business_log")
logger.setLevel(logging.INFO)
# 按日期切分，保留7天备份，避免磁盘写满
handler = TimedRotatingFileHandler(
    "app/business_log_fallback.log",
    when="midnight",  # 每天凌晨切分
    backupCount=7,  # 保留7天日志
    encoding="utf-8"
)
handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
))
logger.addHandler(handler)

# ===================== 2. 轻量监控计数器（替代Prometheus，MVP够用） =====================
log_metrics = defaultdict(int)  # 统计：成功/失败/重试次数
metrics_lock = asyncio.Lock()  # 异步安全锁


# ===================== 3. 核心处理器（新增重试/背压） =====================
class AsyncLogProcessor:
    def __init__(
            self,
            batch_size: int = 50,
            flush_interval: int = 5,
            max_retry: int = 3,  # 新增：最大重试次数
            max_queue_size: int = 10000  # 新增：队列最大长度（背压）
    ):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.max_retry = max_retry
        self.max_queue_size = max_queue_size
        # 带长度限制的队列（背压处理）
        self.queue: asyncio.Queue[Dict] = asyncio.Queue(maxsize=self.max_queue_size)
        self._task: Optional[asyncio.Task] = None
        self._running = False
        # 扩展预留
        self.queue_type = "memory"
        self.redis_client = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._processor_loop())
        logger.info(f"异步日志处理器启动成功（内存队列模式，最大队列长度：{self.max_queue_size}）")

    async def stop(self):
        self._running = False
        if self._task:
            await self._task
        await self._flush_remaining()
        # 打印最终监控统计
        async with metrics_lock:
            logger.info(f"日志处理器停止，统计：{dict(log_metrics)}")

    async def log(self, log_data: Dict):
        """新增：背压处理（队列满时丢弃并告警）"""
        log_data.setdefault("create_time", datetime.now())
        log_data.setdefault("level", "INFO")
        log_data.setdefault("result", "SUCCESS")

        try:
            # 非阻塞入队，队列满时立即返回并告警
            await asyncio.wait_for(self.queue.put(log_data), timeout=0.1)
        except asyncio.TimeoutError:
            # 背压策略：丢弃日志并记录告警
            logger.error(
                f"日志队列已满（{self.max_queue_size}），丢弃日志：{json.dumps(log_data, ensure_ascii=False)[:100]}...")
            async with metrics_lock:
                log_metrics["queue_full_discard"] += 1

    async def _processor_loop(self):
        while self._running:
            try:
                batch = await self._collect_batch()
                if not batch:
                    await asyncio.sleep(self.flush_interval)
                    continue
                # 新增：带重试的批量写入
                await self._flush_batch_with_retry(batch)
            except Exception as e:
                logger.error(f"日志处理循环异常：{str(e)}", exc_info=True)
                await asyncio.sleep(5)

    async def _collect_batch(self) -> List[Dict]:
        batch = []
        for _ in range(self.batch_size):
            try:
                log = await asyncio.wait_for(self.queue.get(), timeout=self.flush_interval)
                batch.append(log)
            except asyncio.TimeoutError:
                break
        return batch

    async def _flush_batch_with_retry(self, batch: List[Dict]):
        """新增：批量写入失败时重试（最多max_retry次）"""
        retry_count = 0
        while retry_count < self.max_retry:
            try:
                async with AsyncSessionFactory() as session:
                    log_objects = [BusinessLog(**log) for log in batch]
                    session.add_all(log_objects)
                    await session.commit()
                # 成功则更新监控
                async with metrics_lock:
                    log_metrics["write_success"] += len(batch)
                    log_metrics[f"retry_{retry_count}"] += 1  # 记录重试次数分布
                logger.info(f"批量写入{len(batch)}条日志成功（重试{retry_count}次）")
                return
            except Exception as e:
                retry_count += 1
                logger.warning(f"批量写入日志失败（第{retry_count}次重试）：{str(e)}")
                await asyncio.sleep(1 * retry_count)  # 指数退避重试

        # 所有重试失败，降级到文件
        logger.error(f"批量写入{len(batch)}条日志重试{self.max_retry}次失败，降级到文件")
        self._fallback_to_file(batch)
        async with metrics_lock:
            log_metrics["write_failure"] += len(batch)

    async def _flush_remaining(self):
        batch = []
        while not self.queue.empty():
            batch.append(self.queue.get_nowait())
        if batch:
            await self._flush_batch_with_retry(batch)

    def _fallback_to_file(self, batch: List[Dict]):
        """降级写入（带结构化格式）"""
        with open("app/business_log_fallback.log", "a", encoding="utf-8") as f:
            for log in batch:
                # 兼容datetime序列化
                log_str = json.dumps(log, ensure_ascii=False, default=str)
                f.write(f"{log_str}\n")