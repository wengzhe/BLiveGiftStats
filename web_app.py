#!/usr/bin/python3
# -*- coding:utf-8 -*-
__author__ = 'WZ'

from flask import Flask, Response, request

from common import config, Utils, BASE_PATH
from md_gen import get_md_from_room_gift
from tables import GiftType

app = Flask(__name__, static_folder=f'{BASE_PATH}/static')


def empty_response():
    return Response(status=200)


@app.route('/')
def root():
    return empty_response()


@app.route('/l/<int:room_id>/<string:gtype>')
@app.route('/live/<int:room_id>/<string:gtype>')
def show_live_all(room_id: int, gtype: str):
    text = get_md_from_room_gift(room_id, GiftType[gtype], dict(request.args))
    if request.args.get('render', '').lower() != 'false':
        text = Utils.render_markdown(text, f"房间 {room_id} 的 {GiftType[gtype].to_name()} 情况\n")
    return text


@app.route('/l/<string:gtype>')
@app.route('/live/<string:gtype>')
def show_live_default(gtype: str):
    if config.live_default():
        return show_live_all(config.live_default(), gtype)
    return empty_response()


def main():
    app.run(host='::', debug=True)


if __name__ == "__main__":
    main()