#!/usr/bin/python3
# -*- coding:utf-8 -*-
__author__ = 'WZ'

import enum
import sqlalchemy
from sqlalchemy.inspection import inspect

from common import DB, db, Utils
from md_gen import get_md_table_line
from tables import GiftStatsTable


def get_lines(session, room_id: int, min_time: int = None, max_time: int = None):
    lines = session.query(GiftStatsTable)
    if min_time:
        lines = lines.filter(GiftStatsTable.time >= min_time)
    if max_time:
        lines = lines.filter(GiftStatsTable.time <= max_time)
    lines = lines.filter_by(rid=room_id).order_by(GiftStatsTable.time.desc())
    return lines


def get_key_from_line(line: GiftStatsTable):
    # inspect(GiftStatsTable).primary_key
    return line.time, line.type, line.rid, line.uid, line.gid


def get_other_column_from_line(line: GiftStatsTable):
    if line is None:
        return None, None, None, None, None
    return line.uname, line.gname, line.num, line.price, line.total


def get_dict_from_lines(lines):
    return {get_key_from_line(line): line for line in lines}


def should_transfer(src: GiftStatsTable, dst: GiftStatsTable):
    if get_key_from_line(src) != get_key_from_line(dst):
        return False
    return src.total > dst.total and (src.num > dst.num or src.price > dst.price)


class TransferDirection(enum.Enum):
    NO_TRANS = 0
    TO_REMOTE = 1
    TO_LOCAL = 2

    def to_string(self):
        return {self.NO_TRANS: '', self.TO_REMOTE: '=>', self.TO_LOCAL: '<='}[self]


def transfer_direction(local: GiftStatsTable, remote: GiftStatsTable):
    if local is None:
        return TransferDirection.TO_LOCAL
    if remote is None:
        return TransferDirection.TO_REMOTE
    if should_transfer(remote, local):
        return TransferDirection.TO_LOCAL
    if should_transfer(local, remote):
        return TransferDirection.TO_REMOTE
    return TransferDirection.NO_TRANS


def compare_with(remote, room_id: int, min_time: int = None, max_time: int = None):
    with db.session() as session:
        local_lines = get_dict_from_lines(get_lines(session, room_id, min_time, max_time))
    with remote.session() as session:
        remote_lines = get_dict_from_lines(get_lines(session, room_id, min_time, max_time))
    keys = sorted(set(local_lines.keys()) | set(remote_lines.keys()), reverse=True, key=lambda line: line[0])
    result = [(local_lines.get(key, None), remote_lines.get(key, None)) for key in keys]
    return [(transfer_direction(local, remote), local, remote) for local, remote in result]


def get_sync_md_line(direction: TransferDirection, local: GiftStatsTable, remote: GiftStatsTable):
    key = get_key_from_line(local) if local is not None else get_key_from_line(remote)
    return get_md_table_line(
        [*key, *get_other_column_from_line(local), direction.to_string(), *get_other_column_from_line(remote)])


def db_sync(url, room_id: int, min_time: int = None, max_time: int = None, dry_run: bool = True):
    remote = DB()
    remote.init(url)
    diff = compare_with(remote, room_id, min_time, max_time)
    if not dry_run:
        to_local = [remote for direction, local, remote in diff if direction == TransferDirection.TO_LOCAL]
        to_remote = [local for direction, local, remote in diff if direction == TransferDirection.TO_REMOTE]
        if to_local:
            db.write(lambda session: [session.merge(item) for item in to_local])
        if to_remote:
            remote.write(lambda session: [session.merge(item) for item in to_remote])
    return get_md_table_line([' '] * 16) + get_md_table_line([':--:'] * 16) + ''.join(
        get_sync_md_line(direction, local, remote) for direction, local, remote in diff if direction.to_string())


def main():
    pass


if __name__ == "__main__":
    main()
