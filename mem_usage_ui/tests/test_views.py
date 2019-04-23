import json

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from mem_usage_ui.__main__ import init_app
from mem_usage_ui.snapshot import SUBSCRIBE


class RoutesTestCase(AioHTTPTestCase):

    async def get_application(self):
        app = await init_app(self.loop)
        return app

    @unittest_run_loop
    async def test_index(self):
        resp = await self.client.request("GET", "/")
        body = await resp.text()

        self.assertEqual(200, resp.status)
        self.assertIn("build.js", body)  # make sure we return index.html

    @unittest_run_loop
    async def test_connect_websocket(self):
        ws = await self.client.ws_connect("/ws")
        self.assertEqual(False, ws.closed)
        self.assertEqual(1, len(self.app["websockets"]))

    @unittest_run_loop
    async def test_websocket_invalid_subscribe_message(self):
        expected_response = {
            "success": False,
            "message": "Can't load provided JSON"
        }
        async with self.client.ws_connect('/ws') as ws:
            self.assertEqual(False, ws.closed)
            await ws.send_str("Invalid JSON")
            async for msg in ws:
                response = json.loads(msg.data)
                self.assertDictEqual(expected_response, response)
                await ws.close()
                self.assertEqual(0, len(self.app["websockets"]))

    @unittest_run_loop
    async def test_websocket_subscribe_invalid_process(self):
        expected_response = {
            "type": "pid_update",
            "success": False,
            "message": "No such process or it was terminated."
        }

        async with self.client.ws_connect('/ws') as ws:
            await ws.send_json({"type": SUBSCRIBE, "pid": -1})
            async for msg in ws:
                response = json.loads(msg.data)
                self.assertDictEqual(expected_response, response)
                await ws.close()
                self.assertEqual(0, len(self.app["websockets"]))
