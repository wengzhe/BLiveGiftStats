#!/usr/bin/python3
# -*- coding:utf-8 -*-
__author__ = 'WZ'

import json
import markdown
import os
import time
import sqlalchemy.exc
import sqlalchemy.ext.declarative
import sqlalchemy.orm

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
OrmBase = sqlalchemy.ext.declarative.declarative_base()


class Config:
    def __init__(self):
        self.cfg = {}

    def load(self, config_file=BASE_PATH + '/data/config.json'):
        try:
            self.cfg = json.load(open(config_file))
        except FileNotFoundError:
            self.cfg = json.load(open(config_file + '.example'))
            json.dump(self.cfg, open(config_file, 'w'), indent=4)

    def room_id(self):
        return self.cfg.get('room_id', [])

    def database_url(self):
        return self.cfg.get('db_url', 'sqlite:///data/database.db')

    def web_port(self):
        return self.cfg.get('web', {}).get('port', 0)

    def web_debug(self):
        return self.cfg.get('web', {}).get('debug', False)

    def live_default(self):
        return self.cfg.get('live', {}).get('default', 0)


class DB:
    def __init__(self):
        self._engine = None
        self._DbSession = None

    def init(self, url):
        self._engine = sqlalchemy.create_engine(url, pool_pre_ping=True, pool_recycle=1800)
        self._DbSession = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(bind=self._engine))

    def create_all(self):
        OrmBase.metadata.create_all(self._engine)

    def session(self):
        return self._DbSession()

    def write(self, func, *args, **kwargs):
        with self.session() as session:
            func(*args, **kwargs, session=session)
            session.commit()


class Utils:
    @staticmethod
    def render_markdown(md, title):
        html = '<!DOCTYPE html><html>'
        html += '<head><meta charset="utf-8">' + f'<title>{title}</title>'
        html += '<link rel="stylesheet" href="/static/md_github.css" type="text/css" /></head>'
        html += '<body><article class="markdown-body">'
        html += markdown.markdown(md, extensions=['markdown.extensions.tables'])
        html += '</article></body></html>'
        return html

    @staticmethod
    def time_from_unix(value):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value))

    @staticmethod
    def time_param_to_unix(value):
        return int(time.mktime(time.strptime(value, '%Y%m%d-%H%M%S')))

    @staticmethod
    def to_time_param(value):
        return value.strftime('%Y%m%d-%H%M%S')


config = Config()
config.load()

db = DB()
db.init(config.database_url())


def main():
    print(config.cfg)
    print(config.room_id())
    print(config.database_url())
    print(config.web_port())
    print(config.web_debug())
    print(config.live_default())
    print(Utils.render_markdown('#123', ''))


if __name__ == "__main__":
    main()
