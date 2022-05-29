#!/usr/bin/python3
# -*- coding:utf-8 -*-
__author__ = 'WZ'

import enum
import sqlalchemy
from sqlalchemy.orm.session import Session

from blivedm.blivedm import GiftMessage, GuardBuyMessage, SuperChatMessage

from common import OrmBase


class GiftType(enum.Enum):
    ReservedLengthForStringTypedEnum = 0  # SQLite上，sqlalchemy似乎有BUG，让表的列宽等于最长的值，但是刚好最长的这个传进去会挂掉
    Gift = 1
    Guard = 2
    SuperChat = 3


class GiftStatsTable(OrmBase):
    __tablename__ = 'gift_stats'
    type = sqlalchemy.Column(sqlalchemy.Enum(GiftType), primary_key=True)  # 礼物类型
    rid = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)  # room id
    uid = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)  # user id
    uname = sqlalchemy.Column(sqlalchemy.Unicode(100))  # user name
    gid = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)  # gift id
    gname = sqlalchemy.Column(sqlalchemy.Unicode(50))  # gift name
    num = sqlalchemy.Column(sqlalchemy.Integer)  # 礼物数量
    price = sqlalchemy.Column(sqlalchemy.Integer)  # 礼物单价
    total = sqlalchemy.Column(sqlalchemy.Integer)  # 礼物总价
    time = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)  # 送礼时间戳

    @staticmethod
    def get_line(session: Session, primary_keys: dict):
        line = session.query(GiftStatsTable).filter_by(**primary_keys).one_or_none()
        if line is None:
            line = GiftStatsTable(**primary_keys)
            session.add(line)
        return line

    @staticmethod
    def update_gift_message(session: Session, room_id: int, message: GiftMessage):
        primary_keys = {'type': GiftType.Gift, 'rid': room_id, 'uid': message.uid, 'gid': message.gift_id,
                        'time': message.timestamp}
        line = GiftStatsTable.get_line(session, primary_keys)
        # 直接update __dict__只能用于第一次生成新行，因为正常来说成员应该是Column对象，这里重置了对象，实际上并不能用于update某个字段
        line.__dict__.update({'uname': message.uname, 'gname': message.gift_name, 'price': message.price})
        # 下面这样写才能正确地更新数据库里的字段
        line.num = message.num + (line.num if line.num else 0)
        line.total = message.total_coin + (line.total if line.total else 0)

    @staticmethod
    def update_guard_message(session: Session, room_id: int, message: GuardBuyMessage):
        primary_keys = {'type': GiftType.Guard, 'rid': room_id, 'uid': message.uid, 'gid': message.gift_id,
                        'time': message.start_time}
        line = GiftStatsTable.get_line(session, primary_keys)
        line.__dict__.update({'uname': message.username, 'gname': message.gift_name, 'price': message.price})
        line.num = message.num + (line.num if line.num else 0)
        line.total = message.price * message.num + (line.total if line.total else 0)

    @staticmethod
    def update_sc_message(session: Session, room_id: int, message: SuperChatMessage):
        primary_keys = {'type': GiftType.SuperChat, 'rid': room_id, 'uid': message.uid, 'gid': message.gift_id,
                        'time': message.start_time}
        line = GiftStatsTable.get_line(session, primary_keys)
        price = message.price * 100
        line.__dict__.update({'uname': message.uname, 'gname': message.gift_name, 'price': price})
        line.num = 1 + (line.num if line.num else 0)
        line.total = price + (line.total if line.total else 0)


def main():
    pass


if __name__ == '__main__':
    main()
