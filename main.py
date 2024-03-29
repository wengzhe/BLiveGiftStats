#!/usr/bin/python3
# -*- coding:utf-8 -*-
__author__ = 'WZ'

import asyncio
import threading

from blivedm.blivedm import BLiveClient

from common import config, db
from handlers import GiftStatsHandler
from web_app import app as application


async def listen_rooms():
    clients = [BLiveClient(room_id) for room_id in config.room_id()]
    handler = GiftStatsHandler(db)
    for client in clients:
        client.set_handler(handler)
        client.start()

    try:
        await asyncio.gather(*(
            client.join() for client in clients
        ))
    finally:
        await asyncio.gather(*(
            client.stop_and_close() for client in clients
        ))


def main():
    db.create_all()  # 如果Table不存在，则创建Table
    if config.web_port():
        # 如果使用debug模式，需要修改use_reloader为False，因为use_reloader预期自己在主线程
        threading.Thread(target=application.run, daemon=True,
                         kwargs={'host': '::', 'port': config.web_port(), 'debug': config.web_debug(),
                                 'use_reloader': False}).start()
    asyncio.get_event_loop().run_until_complete(listen_rooms())


if __name__ == '__main__':
    main()
