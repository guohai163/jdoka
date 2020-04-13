# -*- coding:utf8 -*-
import getopt
import os
import sys
import time

from doperating import DOperating
from gmail import GMail
import configparser
import log4p

LOG = log4p.GetLogger('__main__').logger


def get_parm(parm):
    """
    检查接收的参数
    :param parm:
    :return:
    """
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 't', ['mail-config=', 'db-config=', 'result-path='])
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)
    mail_config = 'conf/mail-config.ini'
    db_config = 'conf/db-config.ini'
    result_path = 'result'
    sleep_time = 0
    for o, a in optlist:
        if o == '--mail-config':
            mail_config = a
        elif o == '--db-config':
            db_config = a
        elif o == '--result-path':
            result_path = a
        elif o == '-t':
            sleep_time = a
    # 检查文件是否存在
    if not os.path.exists(mail_config):
        print('Please check if mail config file exists!')
        sys.exit(1)
    if not os.path.exists(db_config):
        print('Please check if database config file exists!')
        sys.exit(1)
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    LOG.debug('mail:%s,db:%s,result:%s', mail_config, db_config, result_path)
    return mail_config, db_config, result_path, sleep_time


def main():
    mail_config_path, db_config_path, result_path, sleep_time = get_parm(sys.argv[1:])
    config = configparser.ConfigParser()
    while 1:
        config.read(mail_config_path)
        mail = GMail(server=config['mail.config']['imap_server'],
                      port=config['mail.config']['imap_port'],
                      user=config['mail.config']['user'],
                      password=config['mail.config']['password'],
                      box=config['mail.config']['box'],
                      smtp_server=config['mail.config']['smtp_server'],
                      smtp_port=config['mail.config']['smtp_port'])

        LOG.debug('开始接收邮件')
        mail.parse()
        if len(mail.query_list) > 0:
            work = DOperating(dbconfig_path=db_config_path, proconfig_path='conf/profession.conf', result_save_path=result_path)
            for query in mail.query_list:
                result = work.query(parm=query)
                if result is None:
                    LOG.info('查询无结果')
                else:
                    LOG.info('查询成功%s', result)
                    mail.send_mail(query['from'], query['subject'].replace('[q]', '') + '结果', result)
                    mail.delete(query['num'])

        LOG.debug('本次处理结束')
        mail.over()
        if sleep_time == 0:
            break
        # 休眠指定时间
        time.sleep(sleep_time * 60)


if __name__ == '__main__':
    main()
