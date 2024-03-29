#!/usr/bin/python3
# -*- coding:utf-8 -*-
__author__ = 'WZ'

import datetime
import sqlalchemy
from dateutil.relativedelta import relativedelta

from common import db, Utils
from tables import GiftType, GiftStatsTable


class GiftStatsLine:
    def __init__(self, key, name, obj, func):
        self.key = key
        self.name = name
        self.obj = obj
        self.func = func


gift_stats_line_list = [
    GiftStatsLine('uid', 'uid', GiftStatsTable.uid, lambda i: i),
    # TODO: 可以考虑用 markdown.Markdown.ESCAPED_CHARS 来做用户名转义，不过目前用户名仅允许'-'和'_'所以应该还好
    GiftStatsLine('uname', '用户名', sqlalchemy.func.max(GiftStatsTable.uname), lambda i: f'`{i}`'),
    GiftStatsLine('gid', '礼物id', GiftStatsTable.gid, lambda i: i),
    GiftStatsLine('gname', '礼物名', sqlalchemy.func.max(GiftStatsTable.gname), lambda i: i),
    GiftStatsLine('num', '数量', sqlalchemy.func.sum(GiftStatsTable.num), lambda i: i),
    GiftStatsLine('price', '单价（元）', sqlalchemy.func.avg(GiftStatsTable.price), lambda i: i / 1000),
    GiftStatsLine('total', '总价（元）', sqlalchemy.func.sum(GiftStatsTable.total), lambda i: float(i) / 1000),
    GiftStatsLine('time', '时间', sqlalchemy.func.max(GiftStatsTable.time), lambda i: Utils.time_from_unix(i)),
]


def get_md_table_line(items):
    return '|' + '|'.join(str(i) for i in items) + '|\n'


def get_md_from_line(line, i):
    return get_md_table_line([f'{i}'] + [v.func(line[i]) for i, v in enumerate(gift_stats_line_list)])


def get_order_obj(order_by: int):
    key = gift_stats_line_list[abs(order_by) - 1].obj
    return key.asc() if order_by > 0 else key.desc()


def get_useful_functions(gtype: GiftType, aggregate: bool, url_args: dict):
    funcs = [f"[{'取消' if aggregate else ''}聚合]({Utils.get_query(url_args, aggregate=not aggregate)})"]
    query = Utils.get_query(url_args, min=Utils.to_time_param(datetime.datetime.now() - datetime.timedelta(days=1)),
                            max=Utils.to_time_param(datetime.datetime.now()))
    funcs.append("")
    funcs.append(f"[过去24小时]({query})")
    month_split = Utils.get_nearest_past_day()
    query = Utils.get_query(url_args, min=Utils.to_time_param(month_split),
                            max=Utils.to_time_param(
                                month_split + relativedelta(months=1) - datetime.timedelta(seconds=1)))
    funcs.append(f"[本月]({query})")
    query = Utils.get_query(url_args, min=Utils.to_time_param(month_split - relativedelta(months=1)),
                            max=Utils.to_time_param(month_split - datetime.timedelta(seconds=1)))
    funcs.append(f"[上月]({query})")
    funcs.append(
        f"[全部记录]({Utils.get_query({k: v for k, v in url_args.items() if k not in ('max',)}, min='20000101-000000')})")
    funcs.append(
        f"[默认时间]({gtype.to_string()}{Utils.get_query({k: v for k, v in url_args.items() if k not in ('min', 'max')})})")
    funcs.append("")
    for gift_type in (GiftType.Gift, GiftType.Guard, GiftType.SuperChat):
        if gift_type != gtype:
            funcs.append(f"[{gift_type.to_name()}]({gift_type.to_string()}{Utils.get_query(url_args)})")
    return funcs


def get_md_from_room_gift(room_id: int, gtype: GiftType, url_args: dict):
    order_by = int(url_args.get('order', -len(gift_stats_line_list)))
    aggregate = url_args.get('aggregate', 'false').lower() == 'true'
    min_time, max_time = Utils.get_min_max_time(url_args)

    md = f"# 房间 {room_id} 的 {gtype.to_name()} 情况\n"

    md += "常用功能： "
    md += " | ".join(get_useful_functions(gtype, aggregate, url_args))
    md += "\n\n"

    md += get_md_table_line([' '] +
                            [f'[{v.name}]({Utils.get_query(url_args, order=-i if i == order_by else i)})'
                             for i, v in enumerate(gift_stats_line_list, start=1)])
    md += get_md_table_line([':--:'] * (len(gift_stats_line_list) + 1))
    with db.session() as session:
        lines = session.query(*(v.obj for v in gift_stats_line_list))
        if min_time:
            lines = lines.filter(GiftStatsTable.time >= min_time)
        if max_time:
            lines = lines.filter(GiftStatsTable.time <= max_time)
        lines = lines.filter_by(type=gtype, rid=room_id).order_by(get_order_obj(order_by))
        if aggregate:
            lines = lines.group_by(GiftStatsTable.uid, GiftStatsTable.gid)
        else:
            lines = lines.group_by(GiftStatsTable.uid, GiftStatsTable.gid, GiftStatsTable.time)
    md += ''.join(get_md_from_line(line, i + 1) for i, line in enumerate(lines))
    return md


def main():
    pass


if __name__ == "__main__":
    main()
