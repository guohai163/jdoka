# -*- coding:utf8 -*-
import getopt
import os
import sys
import time
import psutil

from archive import Archive
from doperating import DOperating
from gmail import GMail
import configparser
import log4p


LOG = log4p.GetLogger('__main__').logger

CACHE_PATH = 'cache/'


def usage():
    """
    打印帮助
    :return:
    """
    print("""usage: python3 jdoka.py [option]
-l        : 使程序循环执行，默认执行间隔5分钟
-t minute : 使用此参数可以修改循环的间隔时间，只有使用-l后此参数才会生效
-h,--help : 打印此帮助
--==================--
--mail-config=path : 收发信服务器配置项目路径，如不配置为项目同目录下的conf内
--db-config=path   : 数据库服务器配置项目路径，如不配置为项目同目录下的conf内
--profession-config:业务处理配置文件
--result-path=path : 结果文件路径


更多帮助：https://github.com/guohai163/jdoka/wiki""")


def get_parm(parm):
    """
    检查接收的参数
    :param parm:
    :return:
    """
    sleep_time = 5
    mail_config = 'conf/mail-config.ini'
    db_config = 'conf/db-config.ini'
    profession_config = 'conf/profession.conf'
    result_path = 'result'
    loop = False
    try:
        optlist, args = getopt.getopt(parm, 'hlt:', ['mail-config=', 'db-config=', 'result-path=',
                                                     'profession-config=', 'help'])
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)

    for o, a in optlist:
        if o == '--mail-config':
            mail_config = a
        elif o == '--db-config':
            db_config = a
        elif o == '--result-path':
            result_path = a
        elif o == '--profession-config':
            profession_config = a
        elif o == '-t':
            sleep_time = int(a)
        elif o in ('-h', '--help'):
            usage()
            sys.exit()
        elif o == '-l':
            loop = True
    # 检查文件是否存在
    if not os.path.exists(mail_config):
        print('Please check if mail config file exists!')
        sys.exit(1)
    if not os.path.exists(db_config):
        print('Please check if database config file exists!')
        sys.exit(1)
    if not os.path.exists(profession_config):
        print('Please check if profession config file exists!')
        sys.exit(1)
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    LOG.debug('mail:%s,db:%s,result:%s', mail_config, db_config, result_path)
    return mail_config, db_config, profession_config, result_path, sleep_time, loop


def check_pid():
    """
    检查当前程序是否有多分在同时运行，如果有为了防止重复处理邮件，需要进入安全模式
    :return:
    """
    my_pid = os.getpid()
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if 'Python' == process.info['name']:
            is_jdoka_process = False
            for cmd_parm in process.info['cmdline']:
                if 'jdoka' in cmd_parm:
                    is_jdoka_process = True
                    break
            if is_jdoka_process:
                if my_pid != process.info['pid']:
                    LOG.debug('jdoka有多份同时打开，需要使用安全模式')
                    if not os.path.exists(CACHE_PATH):
                        # 打开邮件处理中检查。建立检查目录
                        os.makedirs(CACHE_PATH)
                    return True
    # 当前程序只打开了一份
    return False


def check_cache(message_id):
    """
    检查邮件是否为处理中
    :param message_id: 邮件唯一编号
    :return: 可以处理返回True, 有其它进程在处理中False
    """
    if os.path.exists(CACHE_PATH + message_id):
        return False
    else:
        open(CACHE_PATH + message_id, 'w').close()
        return True


def delete_cache(message_id):
    """
    邮件处理完后删除cache
    :param message_id: 邮件唯一编号
    :return:
    """
    if os.path.exists(CACHE_PATH + message_id):
        os.remove(CACHE_PATH + message_id)


def main():
    mail_config_path, db_config_path, profession_config_path, result_path, sleep_time, loop = get_parm(sys.argv[1:])
    safe_mode = check_pid()
    config = configparser.ConfigParser()
    arch = Archive(result_path + '/result_data.db')
    while True:
        config.read(mail_config_path)
        try:
            server = config['mail.config']['imap_server']
            port = config['mail.config']['imap_port']
            user = config['mail.config']['user']
            password = config['mail.config']['password']
            if config.has_option('mail.config', 'box'):
                box = config['mail.config']['box']
            else:
                box = ''
            smtp_server = config['mail.config']['smtp_server']
            smtp_port = config['mail.config']['smtp_port']
        except KeyError as err:
            LOG.error('请检查邮件配置文件%s。\n%s', mail_config_path, str(err))
            sys.exit(1)
        mail = GMail(server, port, user, password, box, smtp_server, smtp_port)

        LOG.debug('开始接收邮件')
        mail.parse()
        if len(mail.query_list) > 0:
            work = DOperating(dbconfig_path=db_config_path, proconfig_path=profession_config_path,
                              result_save_path=result_path)

            while mail.query_list:
                query = mail.query_list.pop()
                if safe_mode and not check_cache(query['messageid']):
                    continue
                result = work.query(parm=query)
                if result is None:
                    LOG.info('邮件<%s>查询无结果', query['messageid'])
                else:
                    LOG.info('查询成功%s', result)
                    arch.add_data(query, result)
                    mail.send_mail(query['from'], query['subject'].replace('[q]', '') + '结果', result)
                    mail.delete(query['num'])
                if safe_mode:
                    delete_cache(query['messageid'])

        LOG.debug('本次处理结束')
        mail.over()
        if not loop:
            break
        # 休眠指定时间
        LOG.info('本次查询结束，休眠%s分钟', sleep_time)
        time.sleep(sleep_time * 60)
    arch.over()


if __name__ == '__main__':
    main()
