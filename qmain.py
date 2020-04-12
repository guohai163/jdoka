# -*- coding:utf8 -*-
import getopt
import sys

from doperating import DOperating
from gmail import GMail
import configparser
import log4p

LOG = log4p.GetLogger('__main__').logger


def getparm(parm):
    """
    检查接收的参数
    :param parm:
    :return:
    """
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'mdr', ['mail-config=', 'db-config=', 'result-path='])
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)
    mail_config = None
    db_config = None
    result_path = None
    for o, a in optlist:
        if o == '--mail-config':
            mail_config = a
        elif o == '--db-config':
            db_config = a
        elif o == '--result-path':
            result_path = a
    if mail_config is None or db_config is None or result_path is None:
        print('ERROR：pleas input parm')
        sys.exit(1)
    LOG.debug('mail:%s,db:%s,result:%s', mail_config, db_config, result_path)
    return mail_config, db_config, result_path


def main():
    mail_config_path, db_config_path, result_path = getparm(sys.argv[1:])
    config = configparser.ConfigParser()
    config.read(mail_config_path)
    _mail = GMail(server=config['mail.config']['imap_server'],
                  port=config['mail.config']['imap_port'],
                  user=config['mail.config']['user'],
                  password=config['mail.config']['password'],
                  box=config['mail.config']['box'],
                  smtp_server=config['mail.config']['smtp_server'],
                  smtp_port=config['mail.config']['smtp_port'])

    LOG.debug('开始接收邮件')
    _mail.parse()
    if len(_mail.query_list) > 0:
        work = DOperating(dbconfig_path=db_config_path, proconfig_path='profession.conf', result_save_path=result_path)
        for query in _mail.query_list:
            result = work.query(parm=query)
            if result is None:
                LOG.info('查询无结果')
            else:
                LOG.info('查询成功%s', result)
                _mail.send_mail(query['from'], query['subject'].replace('[q]', '') + '结果', result)
                _mail.delete(query['num'])

    LOG.debug('本次处理结束')
    _mail.over()


if __name__ == '__main__':
    main()
