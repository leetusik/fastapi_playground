# app/tasks.py

import time
from celery_worker import app

@app.task(name="app.tasks.urgent_task")
def urgent_task(x, y):
    """긴급하게 처리되어야 할 작업"""
    print(f"--- URGENT TASK STARTED: {x} + {y} ---")
    time.sleep(2)  # 작업을 시뮬레이션하기 위한 대기
    result = x + y
    print(f"--- URGENT TASK FINISHED: Result = {result} ---")
    return result

@app.task(name="app.tasks.normal_task")
def normal_task(a, b):
    """일반적인 우선순위의 작업"""
    print(f"--- Normal Task Started: {a} * {b} ---")
    time.sleep(10)  # 더 긴 작업 시간으로 우선순위 효과를 명확히 보여줌
    result = a * b
    print(f"--- Normal Task Finished: Result = {result} ---")
    return result