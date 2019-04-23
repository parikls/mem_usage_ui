import asyncio
import logging
from argparse import ArgumentParser
from logging.config import dictConfig

from aiohttp import web

from mem_usage_ui.routes import setup_routes
from mem_usage_ui.snapshot import SnapshotProcessor


async def init_app(loop):
    app = web.Application()
    app["websockets"] = set()
    app["snapshot_processor"] = SnapshotProcessor(app, loop)

    app.on_cleanup.append(shutdown)
    setup_routes(app)
    return app


async def shutdown(app):
    for ws in app["websockets"]:
        await ws.close()

    app["websockets"].clear()


def open_browser(url, options):
    if options.debug:
        return

    import webbrowser
    webbrowser.open(url)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--debug", required=False, default=False, type=bool)
    parser.add_argument("--host", required=False, default="localhost")
    parser.add_argument("--port", required=False, default=8080)

    return parser.parse_args()


def main():
    options = parse_args()
    loop = asyncio.get_event_loop()
    loop.set_debug(options.debug)
    app = init_app(loop)
    loop.call_later(
        1,
        open_browser,
        "http://{host}:{port}".format(host=options.host, port=options.port),
        options
    )
    web.run_app(app, host=options.host, port=options.port)


if __name__ == "__main__":
    main()
