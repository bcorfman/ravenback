from taskiq.brokers import RedisBroker
import taskiq_fastapi

# Set up RabbitMQ broker
broker = RedisBroker("redis://localhost:6379")

taskiq_fastapi.init(broker, "main:app")

@taskiq_app.task
def dummy_task(x: int, y: int) -> int:
    import time
    time.sleep(5)  # Simulating a long-running task
    return x + y
