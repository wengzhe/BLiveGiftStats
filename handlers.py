#!/usr/bin/python3
# -*- coding:utf-8 -*-
__author__ = 'WZ'

from blivedm.blivedm import BaseHandler, BLiveClient
from blivedm.blivedm import GiftMessage, GuardBuyMessage, SuperChatMessage

from tables import GiftStatsTable


class GiftStatsHandler(BaseHandler):
    def __init__(self, db):
        self.db = db

    async def _on_gift(self, client: BLiveClient, message: GiftMessage):
        if message.coin_type != 'gold':
            return
        print(f'[{client.room_id}] {message.uname} 赠送{message.gift_name}x{message.num}'
              f' （{message.coin_type}瓜子x{message.total_coin}）', message.__dict__)
        self.db.write(GiftStatsTable.update_gift_message, room_id=client.room_id, message=message)

    async def _on_buy_guard(self, client: BLiveClient, message: GuardBuyMessage):
        print(f'[{client.room_id}] {message.username} 购买{message.gift_name}', message.__dict__)
        self.db.write(GiftStatsTable.update_guard_message, room_id=client.room_id, message=message)

    async def _on_super_chat(self, client: BLiveClient, message: SuperChatMessage):
        print(f'[{client.room_id}] 醒目留言 ¥{message.price} {message.uname}：{message.message}', message.__dict__)
        self.db.write(GiftStatsTable.update_sc_message, room_id=client.room_id, message=message)


def main():
    pass


if __name__ == '__main__':
    main()
