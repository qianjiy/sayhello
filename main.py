#!/usr/bin/env python3
from aiohttp import web
from log.log import get_logger
from app import make_app

logger = get_logger()

if __name__ == '__main__':
    app = make_app()
    logger.info("sayhello started")
    web.run_app(app=app, port=80)
