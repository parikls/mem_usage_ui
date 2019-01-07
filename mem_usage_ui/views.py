import getpass
import json
import logging
import os

import aiohttp
import psutil
from aiohttp.web_response import Response
from aiohttp.web_ws import WebSocketResponse

from mem_usage_ui.snapshot import SnapshotProcessor
from mem_usage_ui.settings import TEMPLATES_DIR

logger = logging.getLogger("mem_usage_ui")


ROOT = "root"
PROCESS_ATTRS = ("pid", "name", "cmdline")

snapshot_processor = SnapshotProcessor()


async def index(request):
    logger.info("rendering index.html")
    with open(os.path.join(TEMPLATES_DIR, "index.html")) as f:
        return Response(text=f.read(), content_type="text/html")


async def get_processes(request):
    """
    Return JSON with all system processes
    """
    logger.info("get all processes")
    current_user = getpass.getuser()
    processes = []
    for process in psutil.process_iter():
        if current_user == ROOT or process.username() == current_user:
            process_dict = process.as_dict(attrs=PROCESS_ATTRS)
            process_dict["cmdline"] = " ".join(process_dict["cmdline"] or [])
            processes.append(process_dict)

    return Response(text=json.dumps(processes), content_type="application/json")


async def websocket_handler(request):
    """
    Handle websocket connections
    """
    ws = WebSocketResponse()
    await ws.prepare(request)

    logger.info("New websocket connection")
    request.app["websockets"].add(ws)

    async for msg in ws:

        if msg.type == aiohttp.WSMsgType.TEXT:
            try:
                message = msg.json()
            except (TypeError, ValueError) as e:
                await ws.send_json({"success": False, "message": "Can't load provided JSON"})
                await ws.close()
            else:
                await snapshot_processor.process_user_message(ws, message)

        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' % ws.exception())

    logger.info("Websocket disconnect. Cleaning")
    await snapshot_processor.unsubscribe(ws)
    request.app["websockets"].remove(ws)

    return ws
