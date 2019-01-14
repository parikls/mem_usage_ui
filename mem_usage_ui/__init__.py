import asyncio
import sys

import uvloop
uvloop.install()


__version__ = '0.8'

if sys.version_info.minor < 7:
    # alias for previous python versions
    asyncio.create_task = lambda coro: asyncio.get_event_loop().create_task(coro)
