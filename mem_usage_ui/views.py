import logging

import aiohttp
from aiohttp.web_response import Response
from aiohttp.web_ws import WebSocketResponse

from mem_usage_ui.settings import TEMPLATES_DIR

logger = logging.getLogger("mem_usage_ui")


async def index(request):
    logger.info("rendering index.html")
    with (TEMPLATES_DIR / "index.html").open() as f:
        return Response(text=f.read(), content_type="text/html")


async def websocket_handler(request):
    """
    Handle websocket connections
    """
    ws = WebSocketResponse()
    await ws.prepare(request)

    logger.info("New websocket connection")
    request.app["websockets"].add(ws)
    snapshot_processor = request.app["snapshot_processor"]

    async for msg in ws:

        if msg.type == aiohttp.WSMsgType.TEXT:
            try:
                message = msg.json()
            except (TypeError, ValueError):
                await ws.send_json({"success": False, "message": "Can't load provided JSON"})
            else:
                await snapshot_processor.process_user_message(ws, message)

        elif msg.type == aiohttp.WSMsgType.ERROR:
            logger.info('ws connection closed with exception %s' % ws.exception())

    logger.info("Websocket disconnect. Cleaning")
    await snapshot_processor.unsubscribe(ws)
    request.app["websockets"].remove(ws)

    return ws
