import asyncio
import json
import logging

import psutil
from aiohttp.web_ws import WebSocketResponse
from psutil import NoSuchProcess

logger = logging.getLogger("mem_usage_ui")

SUBSCRIBE = "subscribe"
UNSUBSCRIBE = "unsubscribe"


class SnapshotProcessor:

    def __init__(self):
        self._pid_ws = {}
        self._ws_pid = {}
        self._loop = asyncio.get_event_loop()

    async def process_user_message(self, ws: WebSocketResponse, message: dict):
        """
        Process user message. Create or cancel snapshotting tasks based on user input
        """
        logger.info("Processing user message")

        if message["type"] == SUBSCRIBE:
            await self.subscribe(ws, message)

        elif message["type"] == UNSUBSCRIBE:
            await self.unsubscribe(ws)

    async def subscribe(self, ws: WebSocketResponse, message: dict):
        logger.info("New subscribe message received for PID %s" % message["pid"])
        self._pid_ws[message["pid"]] = ws
        self._ws_pid[ws] = message["pid"]
        _ = self._loop.create_task(self.snapshot(message["pid"], message["interval"]))

    async def unsubscribe(self, ws: WebSocketResponse):
        logger.info("Unsubscribe message received")
        pid = self._ws_pid[ws]
        del self._pid_ws[pid]
        del self._ws_pid[ws]

    async def snapshot(self, pid: int, interval: float = 1):
        await asyncio.sleep(float(interval))

        try:
            ws = self._pid_ws[pid]
        except KeyError:
            # user unsubscribed
            return

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

        # still subscribed - re-schedule
        _ = self._loop.create_task(self.snapshot(pid, interval))
