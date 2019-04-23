from mem_usage_ui.settings import STATIC_DIR
from mem_usage_ui.views import index, websocket_handler


def setup_routes(app):
    app.router.add_static('/static/', path=STATIC_DIR, name='static')
    app.router.add_get("/ws", websocket_handler)
    app.router.add_get('/', index)
