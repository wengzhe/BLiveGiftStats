#!/usr/bin/python3
# -*- coding:utf-8 -*-
__author__ = 'WZ'

import asyncio

from blivedm.blivedm import BLiveClient

from common import config, db
from handlers import GiftStatsHandler


async def listen():
    clients = [BLiveClient(room_id) for room_id in config.room_id()]
    handler = GiftStatsHandler(db)
    for client in clients:
        client.add_handler(handler)
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
    config.load()
    db.init(config.database_url())
    asyncio.get_event_loop().run_until_complete(listen())


if __name__ == '__main__':
    main()
