import asyncio
import sys

import uvloop
uvloop.install()

_py_version = (sys.version_info.major, sys.version_info.minor)
__version__ = '0.9'

if _py_version < (3, 5):
    raise RuntimeError("Python versions prior to 3.5 are not supported")


if _py_version < (3, 7):
    # alias for 3.5 and 3.6
    asyncio.create_task = lambda coro, loop=None: (loop if loop else asyncio.get_event_loop()).create_task(coro)
