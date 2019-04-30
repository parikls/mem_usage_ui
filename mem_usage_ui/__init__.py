import asyncio
import sys
from logging.config import dictConfig

import uvloop

uvloop.install()

_py_version = (sys.version_info.major, sys.version_info.minor)
__version__ = '0.9.2'

if _py_version < (3, 5):
    raise RuntimeError("Python versions prior to 3.5 are not supported")

if _py_version < (3, 7):
    # alias for 3.5 and 3.6
    asyncio.create_task = lambda coro, loop=None: (loop if loop else asyncio.get_event_loop()).create_task(coro)


# configure logging
dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'mem_usage_ui': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        },
    }
})
