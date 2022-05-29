#!/usr/bin/python3
# -*- coding:utf-8 -*-
__author__ = 'WZ'

import time

from blivedm.blivedm import BLiveClient

from common import config, db
from handlers import GiftStatsHandler


class LiveClientManager:
    def __init__(self):
        self.clients = [BLiveClient(room_id) for room_id in config.room_id()]
        self.handler = GiftStatsHandler(db)
        for client in self.clients:
            client.add_handler(self.handler)
            client.start()


def main():
    config.load()
    db.init(config.database_url())
    manager = LiveClientManager()
    time.sleep(10000)


if __name__ == '__main__':
    main()
