#!/usr/bin/python3
# -*- coding:utf-8 -*-
__author__ = 'WZ'

import sqlalchemy
from flask import Flask, Response, request

from common import db, Utils, BASE_PATH
from tables import GiftType, GiftStatsTable

app = Flask(__name__, static_folder=f'{BASE_PATH}/static')


def empty_response():
    return Response(status=200)


class GiftStatsLine:
    def __init__(self, key, name, obj, func):
        self.key = key
        self.name = name
        self.obj = obj
        self.func = func


gift_stats_line_list = [
    GiftStatsLine('uid', 'uid', GiftStatsTable.uid, lambda i: i),
    GiftStatsLine('uname', '用户名', GiftStatsTable.uname, lambda i: i),
    GiftStatsLine('gid', '礼物id', GiftStatsTable.gid, lambda i: i),
    GiftStatsLine('gname', '礼物名', GiftStatsTable.gname, lambda i: i),
    GiftStatsLine('num', '数量', sqlalchemy.func.sum(GiftStatsTable.num), lambda i: i),
    GiftStatsLine('price', '单价（元）', sqlalchemy.func.avg(GiftStatsTable.price), lambda i: i / 1000),
    GiftStatsLine('total', '总价（元）', sqlalchemy.func.sum(GiftStatsTable.total), lambda i: float(i) / 1000),
    GiftStatsLine('time', '时间', sqlalchemy.func.max(GiftStatsTable.time), lambda i: Utils.time_from_unix(i)),
]


def get_md_table_line(items):
    return '|' + '|'.join(str(i) for i in items) + '|\n'


def get_md_from_line(line):
    return get_md_table_line(v.func(line[i]) for i, v in enumerate(gift_stats_line_list))


def get_order_obj(order_by: int):
    key = getattr(GiftStatsTable, gift_stats_line_list[abs(order_by) - 1].key)
    return key.asc() if order_by > 0 else key.desc()


def get_query(url_args: dict, **kwargs):
    return "&".join(f"{k}={v}" for k, v in {**url_args, **kwargs}.items())


def get_md_from_room_gift(room_id: int, gtype: GiftType, url_args: dict):
    order_by = int(url_args.get('order', -len(gift_stats_line_list)))
    aggregate = url_args.get('aggregate', 'false').lower() == 'true'
    md = f"# 房间 {room_id} 的 {gtype.to_string()} 情况\n"
    md += f"[聚合](?{get_query(url_args, aggregate=not aggregate)})\n"
    md += get_md_table_line(
        f'[{v.name}](?{get_query(url_args, order=-i if i == order_by else i)})'
        for i, v in enumerate(gift_stats_line_list, start=1))
    md += get_md_table_line([':--:'] * len(gift_stats_line_list))
    with db.session() as session:
        lines = session.query(*(v.obj for v in gift_stats_line_list)) \
            .filter_by(type=gtype, rid=room_id).order_by(get_order_obj(order_by))
        if aggregate:
            lines = lines.group_by(GiftStatsTable.uid, GiftStatsTable.gid)
        else:
            lines = lines.group_by(GiftStatsTable.uid, GiftStatsTable.gid, GiftStatsTable.time)
    md += ''.join(get_md_from_line(line) for line in lines)
    return md


@app.route('/')
def root():
    return empty_response()


@app.route('/<room_id>/<gtype>')
def show_all(room_id: int, gtype: str):
    text = get_md_from_room_gift(room_id, GiftType[gtype], dict(request.args))
    if request.args.get('render', '').lower() != 'false':
        text = Utils.render_markdown(text)
    return text


def main():
    app.run(host='::', debug=True)


if __name__ == "__main__":
    main()
