import asyncio
import getpass
import logging
from typing import Union, List, Dict

import psutil
from aiohttp.web_app import Application
from aiohttp.web_ws import WebSocketResponse
from psutil import Error

logger = logging.getLogger("mem_usage_ui")


class SnapshotProcessor:
    """
    Main class for handling processes
    and memory snapshots
    """

    MESSAGE_INIT = "init"
    MESSAGE_SUBSCRIBE = "subscribe"
    MESSAGE_UNSUBSCRIBE = "unsubscribe"

    USER_ROOT = "root"

    MEM_RSS_DIVIDER = 1024

    DEFAULT_PROCESS_ATTRS = ("pid", "name", "cmdline")
    EXTENDED_PROCESS_ATTRS = (
        "memory_info", "status", "cpu_percent", "memory_percent", "num_threads", "username"
    )
    PROCESS_DIFF_SNAPSHOT_INTERVAL = 1
    MEMORY_SNAPSHOT_INTERVAL = 1

    @staticmethod
    def get_processes_as_dict() -> dict:
        """
        Return processes in a dict format where key is a PID
        """
        current_user = getpass.getuser()
        processes = {}
        for process in psutil.process_iter():
            if current_user == SnapshotProcessor.USER_ROOT or process.username() == current_user:
                process_dict = process.as_dict(attrs=SnapshotProcessor.DEFAULT_PROCESS_ATTRS)
                process_dict["cmdline"] = " ".join(process_dict["cmdline"] or [])
                processes[process_dict["pid"]] = process_dict

        return processes

    def __init__(self, app: Application, loop=None):
        self._websockets = app["websockets"]
        self._pid_ws = {}
        self._ws_pid = {}
        self._loop = loop or asyncio.get_event_loop()
        self._processes = self.get_processes_as_dict()

        # process diff task
        loop.create_task(self.process_diff())

    async def process_diff(self):
        """
        Background task which take a process snapshot every `interval`,
        and sends a diff to all connected websockets
        """

        await asyncio.sleep(self.PROCESS_DIFF_SNAPSHOT_INTERVAL)

        if self._websockets:
            # proceed only if there are connected clients

            current_processes = self.get_processes_as_dict()
            terminated_processes = self._processes.keys() - current_processes.keys()
            new_processes = current_processes.keys() - self._processes.keys()

            if terminated_processes or new_processes:

                await self.send_process_diff(
                    list(terminated_processes),
                    {pid: current_processes[pid] for pid in new_processes},
                )

                # update existing processes
                self._processes = current_processes

        # re-schedule task
        self._loop.create_task(self.process_diff())

    async def process_user_message(self, ws: WebSocketResponse, message: dict):
        """
        Process user message. Creates or cancel
        snapshot tasks based on user input
        """
        logger.info("Processing user message")

        # todo: handle unknown message type
        if message["type"] == self.MESSAGE_INIT:

            # on init - send only existing processes
            await self.send_process_diff(
                terminated_processes=None,
                new_processes=self._processes
            )

        elif message["type"] == self.MESSAGE_SUBSCRIBE:
            await self.subscribe(ws, message)

        elif message["type"] == self.MESSAGE_UNSUBSCRIBE:
            await self.unsubscribe(ws)

    async def subscribe(self, ws: WebSocketResponse, message: dict):
        logger.info("New subscribe message received for PID %s" % message["pid"])

        # reference of PID to websocket and vice versa
        self._pid_ws[message["pid"]] = ws
        self._ws_pid[ws] = message["pid"]

        self._loop.create_task(
            self.snapshot(
                message["pid"],
                message.get("interval", self.MEMORY_SNAPSHOT_INTERVAL)
            )
        )

    async def send_process_diff(
            self,
            terminated_processes: Union[None, List] = None,
            new_processes: Union[None, Dict[int, Dict]] = None
    ):
        terminated_processes = terminated_processes or []
        new_processes = new_processes or []

        result = {
            "type": "process_diff",
            "payload": {
                "terminated": terminated_processes,
                "new": new_processes
            }
        }

        for ws in self._websockets:
            try:
                await ws.send_json(result)
            except Exception as e:
                logger.exception(e)

    async def unsubscribe(self, ws: WebSocketResponse):
        logger.info("Unsubscribe message received")
        pid = self._ws_pid.pop(ws, None)
        self._pid_ws.pop(pid, None)

    async def snapshot(self, pid: int, interval: float = 1):
        await asyncio.sleep(float(interval))

        payload = {"type": "pid_update"}

        try:
            ws = self._pid_ws[pid]
        except KeyError:
            # user unsubscribed
            return

        try:
            process = psutil.Process(pid)
            process = process.as_dict(attrs=self.EXTENDED_PROCESS_ATTRS)
            process["rss"] = round(
                process.pop("memory_info").rss / self.MEM_RSS_DIVIDER / self.MEM_RSS_DIVIDER
            )

            payload["success"] = True
            payload["process"] = process

        except (Error, ValueError):
            logger.warning("No such process. PID=%s" % pid)
            payload["success"] = False
            payload["message"] = "No such process or it was terminated."
            await ws.send_json(payload)
            await self.unsubscribe(ws)
            return

        if not ws.closed:
            await ws.send_json(payload)
            # still subscribed - re-schedule
            _ = self._loop.create_task(self.snapshot(pid, interval))
