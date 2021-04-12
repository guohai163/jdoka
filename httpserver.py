from abc import ABC

import tornado as tornado
import tornado.web


class StopDataHandler(tornado.web.RequestHandler, ABC):
    """
    安全停止服务
    """

    def get(self):
        self.write('services stop ...')
        tornado.ioloop.IOLoop.instance().stop()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('jdoka auto web<br /><a href="conf/cron.conf">cron.conf</a><br /><a href="conf/profession.conf">profession.conf</a>')
