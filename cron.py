# -*- coding:utf8 -*-
import configparser
import getopt
import os
import sys
import time

import log4p
from crontab import CronTab

from doperating import DOperating
from gmail import GMail


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CRON_CONFIG_PATH = '%s/conf/cron.conf' % BASE_DIR
LOG = log4p.GetLogger('CRON').logger


def init_cron_task():
    """
    初始化所有cron事件
    :return:
    """
    config = configparser.ConfigParser()
    config.read(CRON_CONFIG_PATH)
    print(config.sections())
    cron_manager = CronTab(user=True)
    for cron_sect in config.sections():
        print(config[cron_sect]['time'])
        job = cron_manager.new(
            command='/usr/local/bin/python3 %s/cron.py --task=%s >> /var/log/%s.log 2>&1' % (
            BASE_DIR, cron_sect, cron_sect))

        # 设置任务执行周期，每两分钟执行一次(更多方式请稍后参见参考链接)
        job.setall(config[cron_sect]['time'])
        LOG.info('创建事件%s' % cron_sect)
        # 将crontab写入linux系统配置文件
        cron_manager.write()


def send_data(task):
    print(task)
    mail_config_path = '%s/conf/mail-config.ini' % BASE_DIR
    db_config = '%s/conf/db-config.ini' % BASE_DIR
    profession_config = '%s/conf/profession.conf' % BASE_DIR
    result_path = '%s/result' % BASE_DIR
    work = DOperating(dbconfig_path=db_config, proconfig_path=profession_config,
                      result_save_path=result_path)
    config = configparser.ConfigParser()
    config.read(CRON_CONFIG_PATH)
    query = {'subject': config[task]['task'], 'from': config[task]['mail']}
    result = work.query(parm=query)
    print(result)
    if result is None:
        LOG.info('邮件<%s>查询无结果', query['messageid'])
        # mail.delete(query['num'])
    else:
        mail_config = configparser.ConfigParser()
        mail_config.read(mail_config_path)
        server = mail_config['mail.config']['imap_server']
        port = mail_config['mail.config']['imap_port']
        user = mail_config['mail.config']['user']
        password = mail_config['mail.config']['password']
        if mail_config.has_option('mail.config', 'box'):
            box = mail_config['mail.config']['box']
        else:
            box = ''
        smtp_server = mail_config['mail.config']['smtp_server']
        smtp_port = mail_config['mail.config']['smtp_port']
        mail = GMail(server, port, user, password, box, smtp_server, smtp_port)
        mail.send_mail(query['from'], query['subject'].replace('[q]', '') + '结果', result)
def main():
    LOG.info('进入方法main: %s' % sys.argv[1:])
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'hlt:', ['task=', 'init'])
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)
    for o, a in optlist:
        if o in ('-h', '--init'):
            init_cron_task()
            # 驻留后台
            while True:
                time.sleep(5)
        elif o == '--task':

            send_data(a)


if __name__ == '__main__':
    main()
