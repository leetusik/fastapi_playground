# app/main.py

from fastapi import FastAPI
from app.tasks import urgent_task, normal_task

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Celery with FastAPI"}

@app.post("/urgent-task")
async def run_urgent_task(x: int, y: int):
    """긴급 작업을 큐에 추가합니다."""
    # apply_async()로 명시적 우선순위 설정
    task = urgent_task.apply_async(args=[x, y], priority=0, queue='urgent-queue')
    return {"task_id": task.id, "message": "Urgent task has been submitted."}

@app.post("/normal-task")
async def run_normal_task(a: int, b: int):
    """일반 작업을 큐에 추가합니다."""
    # apply_async()로 명시적 우선순위 설정
    task = normal_task.apply_async(args=[a, b], priority=5, queue='normal-queue')
    return {"task_id": task.id, "message": "Normal task has been submitted."}