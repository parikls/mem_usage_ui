import asyncio
import logging

import psutil
from aiohttp.web_ws import WebSocketResponse
from psutil import Error

logger = logging.getLogger("mem_usage_ui")

SUBSCRIBE = "subscribe"
UNSUBSCRIBE = "unsubscribe"
RSS_DIVIDER = 1024


class SnapshotProcessor:

    def __init__(self, loop=None):
        self._pid_ws = {}
        self._ws_pid = {}
        self._loop = loop or asyncio.get_event_loop()

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
        _ = self._loop.create_task(self.snapshot(message["pid"], message.get("interval", 1)))

    async def unsubscribe(self, ws: WebSocketResponse):
        logger.info("Unsubscribe message received")
        pid = self._ws_pid.pop(ws, None)
        self._pid_ws.pop(pid, None)

    async def snapshot(self, pid: int, interval: float = 1):
        await asyncio.sleep(float(interval))

        try:
            ws = self._pid_ws[pid]
        except KeyError:
            # user unsubscribed
            return

        try:
            process = psutil.Process(pid)
            process = process.as_dict(
                attrs=("memory_info", "status", "cpu_percent", "memory_percent", "num_threads", "username")
            )
            process["rss"] = round(process.pop("memory_info").rss / RSS_DIVIDER / RSS_DIVIDER)
            process["success"] = True

        except (Error, ValueError):
            logger.warning("No such process. PID=%s" % pid)
            await self.unsubscribe(ws)
            await ws.send_json({
                "success": False,
                "message": "No such process or it was terminated."
            })
            return

        if not ws.closed:
            await ws.send_json(process)
            # still subscribed - re-schedule
            _ = self._loop.create_task(self.snapshot(pid, interval))
