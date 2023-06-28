from argparse import ArgumentParser
from typing import Optional, Any

from aiohttp import web

from mem_usage_ui.routes import setup_routes
from mem_usage_ui.snapshot import SnapshotProcessor


def init_app(options: Optional[Any] = None):
    app = web.Application()
    app["websockets"] = set()
    app["options"] = options
    app.on_startup.extend([open_browser, SnapshotProcessor.create])
    app.on_cleanup.append(shutdown)
    setup_routes(app)
    return app


async def shutdown(app):
    for ws in app["websockets"]:
        await ws.close()

    app["websockets"].clear()


async def open_browser(app):
    options = app["options"]
    if not options:
        return
    if options.debug:
        return

    import webbrowser
    url = "http://{host}:{port}".format(host=options.host, port=options.port)
    webbrowser.open(url)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--debug", required=False, default=False, type=bool)
    parser.add_argument("--host", required=False, default="localhost")
    parser.add_argument("--port", required=False, default=8080)
    return parser.parse_args()


def main():
    options = parse_args()
    app = init_app(options)
    web.run_app(app, host=options.host, port=options.port)


if __name__ == "__main__":
    main()
