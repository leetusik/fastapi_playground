# celery_worker.py

from celery import Celery
from kombu import Queue

# Redis 브로커와 백엔드 설정
import os
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Celery 앱 인스턴스 생성
app = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks"]  # Celery가 작업을 찾을 경로
)

# --- 큐 정의 ---
# 우선순위 기반 큐 설정: x-max-priority로 우선순위 지원
app.conf.task_queues = (
    Queue("urgent-queue", routing_key="urgent.#", queue_arguments={'x-max-priority': 10}),
    Queue("normal-queue", routing_key="normal.#", queue_arguments={'x-max-priority': 10}),
)

# --- 기본 큐 및 라우팅 설정 ---
# 특정 큐가 지정되지 않은 작업은 'normal-queue'로 보냅니다.
app.conf.task_default_queue = "normal-queue"
app.conf.task_default_exchange = "default"
app.conf.task_default_routing_key = "normal.default"

# --- 작업별 라우팅 규칙 정의 ---
# 우선순위 기반 라우팅: urgent_task는 높은 우선순위(9), normal_task는 낮은 우선순위(1)
app.conf.task_routes = {
    "app.tasks.urgent_task": {
        "queue": "urgent-queue", 
        "routing_key": "urgent.task",
        "priority": 0,  # 최고 우선순위 (0이 가장 높음)
    },
    "app.tasks.normal_task": {
        "queue": "normal-queue",
        "routing_key": "normal.task", 
        "priority": 5,  # 낮은 우선순위
    },
}

app.conf.update(
    task_track_started=True,
    # CRITICAL: Redis broker priority configuration
    broker_transport_options={
        'priority_steps': list(range(10)),  # 0-9 priority levels (0=highest)
        'sep': ':',
        'queue_order_strategy': 'priority',
    },
    # Disable prefetching to ensure immediate priority handling
    worker_prefetch_multiplier=1,
)

# 💡 REDIS + CELERY 우선순위 시스템 (실제 동작 방식)
# 
# ❌ 이전 오해: Redis가 RabbitMQ처럼 네이티브 우선순위 지원한다고 생각
# 
# ✅ 실제 동작: Redis는 우선순위별 **별도 큐**를 생성하여 에뮬레이션
# 
# 핵심 설정:
# 1. broker_transport_options['priority_steps'] = [0,1,2...9]
# 2. broker_transport_options['queue_order_strategy'] = 'priority'  
# 3. worker_prefetch_multiplier = 1 (즉시 우선순위 확인)
#
# 우선순위 값: 0 = 최고 우선순위, 9 = 최저 우선순위
# - urgent_task: priority=0 (즉시 처리)
# - normal_task: priority=5 (나중 처리)
#
# 동작 원리:
# - Celery가 Redis에 'queue_name:0', 'queue_name:1' 등 별도 큐 생성
# - 워커는 낮은 번호(높은 우선순위) 큐부터 확인
# - prefetch_multiplier=1로 즉시 새 작업 확인
#
# 이제 urgent task가 진짜로 먼저 처리됨! 🎯