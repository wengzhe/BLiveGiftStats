#!/usr/bin/python3
# -*- coding:utf-8 -*-
__author__ = 'WZ'

from flask import Flask, Response

from common import config, db
from tables import GiftType, GiftStatsTable

app = Flask(__name__)


def empty_response():
    return Response(status=200)


@app.route('/')
def root():
    return empty_response()


@app.route('/<room_id>/<gtype>')
def show_all(room_id: int, gtype: GiftType):
    result = f"房间{room_id} 礼物类型{gtype}\n"
    with db.session() as session:
        lines = session.query(GiftStatsTable).filter_by(type=gtype, rid=room_id)
    return result + '\n'.join(f"{line.__dict__}" for line in lines)


def main():
    app.run(host='::', debug=True)


if __name__ == "__main__":
    main()
