#!/usr/bin/env python3

import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve

from escaperoom.asgi import application

asyncio.run(serve(application, Config()))
