# -*- coding:utf8 -*-
import sqlite3
import log4p

LOG = log4p.GetLogger('Archive').logger


class Archive:
    _archive_path = None
    _sql_conn = None
    _cursor = None

    def __init__(self, archive_path):
        """
        初始化方法
        :param archive_path: 存档路径
        """
        self._archive_path = archive_path
        self._sql_conn = sqlite3.connect(archive_path)
        self._cursor = self._sql_conn.cursor()
        self._cursor.execute('CREATE TABLE IF NOT EXISTS mail_archive ('
                             'mail_subject TEXT,mail_from TEXT,'
                             'mail_body TEXT,mail_date TEXT,result_path TEXT)')
        self._sql_conn.commit()

    def add_data(self, mail, result_path):
        """
        增加数据
        :param mail: 邮件参数
        :param result_path: 结果路径
        :return:
        """
        LOG.debug('准备增加数据 %s %s' % (str(mail), result_path))
        sql_parm = [(mail['subject'], mail['from'], mail['body'], mail['date'], result_path)]
        self._cursor.executemany('INSERT INTO mail_archive VALUES(?,?,?,?,?)', sql_parm)
        self._sql_conn.commit()

    def over(self):
        """
        析构方法，关闭连接
        :return:
        """
        if self._sql_conn is None:
            self._sql_conn.close()
            self._sql_conn = None
