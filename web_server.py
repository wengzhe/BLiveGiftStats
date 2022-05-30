#!/usr/bin/python3
# -*- coding:utf-8 -*-
__author__ = 'WZ'

from flask import Flask, Response, request

from common import Utils, BASE_PATH
from md_gen import get_md_from_room_gift
from tables import GiftType

app = Flask(__name__, static_folder=f'{BASE_PATH}/static')


def empty_response():
    return Response(status=200)


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
