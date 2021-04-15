from abc import ABC

import tornado as tornado
import tornado.web

from config import get_all_conf


class StopDataHandler(tornado.web.RequestHandler, ABC):
    """
    安全停止服务
    """

    def get(self):
        self.write('services stop ...')
        tornado.ioloop.IOLoop.instance().stop()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(
            'jdoka auto web<br /><a href="conf?path=cron.conf">cron.conf</a><br /><a href="conf?path=profession.conf">profession.conf</a>')


class ConfigHandler(tornado.web.RequestHandler):
    def get(self):
        path = self.get_argument('path', 'cron.conf')
        self.write(get_all_conf(path))
