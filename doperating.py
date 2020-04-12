# -*- coding:utf8 -*-
import configparser
import log4p
import uuid
import csv
import pymssql

import sqlscript

LOG = log4p.GetLogger('DOperating').logger


class DOperating:
    __db_config = None
    __profession_config = None

    __result_save_path = ''

    def __init__(self, dbconfig_path, proconfig_path, result_save_path):
        """
        接收参数
        :param dbconfig_path: 配置文件路径
        :param result_save_path: 结果文件路径
        """
        self.__db_config = configparser.ConfigParser()
        self.__db_config.read(dbconfig_path)

        self.__profession_config = configparser.ConfigParser()
        self.__profession_config.read(proconfig_path)

        self.__result_save_path = result_save_path

    def query(self, parm):
        """
        路由
        :param parm:
        :return: 查询结果的路径
        """
        LOG.debug('拉收到参数%s', parm)
        parm['subject'] = parm['subject'].replace('[q]', '')
        if not self.__profession_config.has_section(parm['subject']):
            LOG.error('指定业务[%s]配置节点不存在，请处理！', parm['subject'])
            return None
        # 准备开始调用
        # 反射方法
        if hasattr(sqlscript, self.__profession_config[parm['subject']]['funname']):
            LOG.debug('方法%s反射成功', self.__profession_config[parm['subject']]['funname'])
            pro_func = getattr(sqlscript, self.__profession_config[parm['subject']]['funname'])
            sql = pro_func(self.__profession_config, parm)
            if sql is None:
                LOG.error('返回的sql为空')
                return None
            else:
                result_file = self.exec_sql(sql, self.__profession_config[parm['subject']]['database'])
        else:
            LOG.error('未实现方法:%s', self.__profession_config[parm['subject']]['funname'])
            return None

        return result_file

    def exec_sql(self, sql, database):
        LOG.debug('开始执行SQL[%s][%s]', sql, database)
        db_conn = pymssql.connect(self.__db_config[database]['server'],
                                  self.__db_config[database]['user'],
                                  self.__db_config[database]['password'])
        cursor = db_conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchone()
        path = self.__result_save_path + '/' + str(uuid.uuid1()) + '.csv'
        with open(path, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',')
            spamwriter.writerow(rows)
        db_conn.close()
        return path

    # def idcard_query(self, parm):
    #     """
    #     身份证查询
    #     :param parm:
    #     :return:
    #     """
    #     LOG.debug('准备查询身份证')
    #     # TODO: 白名单检查
    #     whitelist = self.__profession_config[parm['subject']]['whitelist']
    #     if whitelist.find(parm['from'], 0, len(parm['from'])) == -1:
    #         LOG.error('查询人不在白名单中，请检查 %s', parm['subject'])
    #         return None
    #     # 处理检查数据
    #     accounts = re.match(r'account:([^\r\n]+)', parm['body'], re.M | re.I).group(1).split(',')
    #     LOG.debug('待查询账号:%s', accounts)
    #     if len(accounts) == 0:
    #         LOG.debug('解析错误，未进行数据查询')
    #         return None
    #     else:
    #         # 按多条in进行查询准备SQL
    #         sql = """select a.account,b.cer_number from [AccountDB].[dbo].[userid_account_rel] a
    #                         inner join [AccountDB].[dbo].[game_person_detail] b on a.user_id=b.user_id
    #                         where a.account in ('%s')""" % '\',\''.join(accounts)
    #         LOG.debug(sql)
    #     return sql
