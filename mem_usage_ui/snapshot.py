import asyncio
import json
import logging

import psutil
from aiohttp.web_ws import WebSocketResponse
from psutil import NoSuchProcess

logger = logging.getLogger("mem_usage_ui")

SUBSCRIBE = "subscribe"
UNSUBSCRIBE = "unsubscribe"


async def process_user_message(ws: WebSocketResponse, message: dict, task: asyncio.Task) -> asyncio.Task:
    """
    Process user message. Create or cancel snapshotting tasks based on user input
    """

    logger.info("Processing user message")
    logger.debug(message)

    if message["type"] == SUBSCRIBE:
        logger.info("New subscribe message received for PID %s" % message["pid"])

        # if user was already subscribed to another process we need to cancel that task
        clean_snapshotting_task(task)

        # schedule snapshotting task
        logger.info("Scheduling new snapshotting task for pid %s" % message["pid"])
        loop = asyncio.get_event_loop()
        task = loop.create_task(snapshotting(ws, message["pid"], int(message["interval"])))

    elif message["type"] == UNSUBSCRIBE:

        logger.info("Unsubscribe message received for PID %s" % message["pid"])
        clean_snapshotting_task(task)

    return task


async def snapshotting(ws: WebSocketResponse, pid: int, interval: int = 1):
    """
    Perform snapshotting with provided `interval` and send snapshot to user
    """
    logger.info("Start snapshotting process with PID %s" % pid)

    while True:
        await asyncio.sleep(interval)
        try:
            process = psutil.Process(pid)
        except NoSuchProcess:
            logger.warning("No such process with PID %s" % pid)
            await ws.send_str(json.dumps({
                "success": False,
                "message": "No such process or it was terminated."
            }))
            return

        await ws.send_str(json.dumps({
            "success": True,
            "rss": round(process.memory_info().rss / 1024 / 1024),
            "status": process.status(),
            "cpu_percent": process.cpu_percent(),
            "memory_percent": process.memory_percent(),
            "num_threads": process.num_threads(),
            "username": process.username(),
        }))


def clean_snapshotting_task(task):
    if task and not task.cancelled() and not task.done():
        logger.info("Clear snapshotting task")
        task.cancel()
