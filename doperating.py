# -*- coding:utf8 -*-
import configparser
import re
from importlib import import_module
from importlib.util import find_spec

import log4p
import uuid
import xlsxwriter
import pyodbc
import datetime
import os

LOG = log4p.GetLogger('DOperating').logger

# 程序目前支持的数据类型
DB_TYPE = {'mssql': 'ODBC Driver 17 for SQL Server', 'mysql': 'MySQL ODBC 8.0 Driver'}

# 客制化模块的包名
CUSTOM_PACKAGE = 'customized'


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

        self.__profession_config = configparser.RawConfigParser(strict=False)
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
        sql = {}
        if not self.__profession_config.has_section(parm['subject']):
            LOG.error('指定业务[%s]配置节点不存在，请处理！', parm['subject'])
            return None

        if not self._check_white_list(parm):
            LOG.error('[%s]<%s>白名单检查未通过', parm['subject'], parm['messageid'])
            return None
        # 当直接包含SQL时
        if self.__profession_config.has_option(parm['subject'], 'sql'):
            # 如果业务配置项中有sql属性，直接执行sql语句
            sql["data"] = self._with_sql_attribut(parm)

        # 当包含module时
        if self.__profession_config.has_option(parm['subject'], 'module'):
            sql = self._with_module_attribut(parm)

        if sql is None:
            return None
        try:
            return self._exec_sql_use_odbc(sql, self.__profession_config[parm['subject']]['database'])
        except Exception as err:
            LOG.error('执行SQL时发生错误[%s]\n%s', sql, str(err))
            return None

    def _with_module_attribut(self, mail_parm):
        """
        使用用户自定义模块内方法
        :param mail_parm:
        :return:
        """
        module_name = ".%s" % self.__profession_config[mail_parm['subject']]['module']
        if find_spec(module_name, CUSTOM_PACKAGE) is None:
            LOG.error('<%s>自定义邮件，模块名[]没有找到，请检查配置', mail_parm['messageid'], module_name)
            return None
        custom = import_module(module_name, package=CUSTOM_PACKAGE)
        try:
            return custom.make_sql(self.__profession_config, mail_parm)
        except AttributeError as err:
            LOG.error('自定义业务[%s]没有实现make_sql方法，请检查', mail_parm['subject'])
            return None

    def _check_white_list(self, parm):
        """
        白名单检查，发件人是否允许进行此次查询
        :param p_config: 配置项目
        :param parm: 邮件参数
        :return: 布尔值
        """
        # 先检查是否有白名单参数，如没有默认为可以查询
        if not self.__profession_config.has_option(parm['subject'], 'whitelist'):
            LOG.debug('此次查询不不要使用白名单')
            return True

        whitelist = self.__profession_config[parm['subject']]['whitelist']
        for from_mail in parm['from'].split(','):
            if whitelist.find(from_mail.replace(' ', ''), 0, len(whitelist)) == -1:
                LOG.debug('查询人不在白名单中，请检查 %s', parm['subject'])
                return False

        return True

    def _exec_sql_use_odbc(self, sql, database):
        """
        sql执行方法
        :param sql: sql语句
        :param database: 数据库
        :return: 结果文件路径
        """
        if self.__db_config[database]['drive'] not in DB_TYPE:
            LOG.error('数据库类型[%s]不被支持，请看说明文档', self.__db_config[database]['drive'])
            return None

        db_conn = pyodbc.connect(
            'DRIVER={' + DB_TYPE[self.__db_config[database]['drive']] + '};SERVER=' + self.__db_config[database][
                'server'] + ';DATABASE=' + database + ';UID=' + self.__db_config[database]['user'] + ';PWD=' +
            self.__db_config[database]['password'])
        db_conn.timeout = 60 * 3
        cursor = db_conn.cursor()
        result_path = None
        workbook_obj = None
        sql_len = len(sql)
        for sql_key, sql_val in sql.items():
            LOG.info('待执行SQL为:%s' % sql_val)
            cursor.execute(sql_val)
            sql_len = sql_len - 1
            if sql_len == 0:
                result_path, workbook_obj = self._write_xlsx(cursor, workbook_obj, result_path, True, sql_key)
            else:
                result_path, workbook_obj = self._write_xlsx(cursor, workbook_obj, result_path, False, sql_key)

        db_conn.close()
        return result_path

    def _write_xlsx(self, cursor, workbook_obj, path, is_close_xlsx, sql_key):
        """
        写XLMS
        :param cursor:
        :return:
        """
        if None is workbook_obj:
            result_dir = '%s/%d/%d' % (
                self.__result_save_path, datetime.datetime.now().year, datetime.datetime.now().month)
            if not os.path.exists(result_dir):
                LOG.debug('路径%s不存在，准备创建', result_dir)
                os.makedirs(result_dir)
            path = result_dir + '/' + str(uuid.uuid1()) + '.xlsx'
            workbook = xlsxwriter.Workbook(path)
        else:
            workbook = workbook_obj

        worksheet = workbook.add_worksheet(sql_key)
        # i和j循环使用表示excel的横和列坐标用
        i = 1
        for j in range(len(cursor.description)):
            worksheet.write(0, j, cursor.description[j][0])

        for row in cursor:
            for j in range(len(row)):
                if type(row[j]) in (datetime.datetime,
                                    datetime.date,
                                    datetime.time,
                                    datetime.timedelta):
                    worksheet.write_datetime(i, j, row[j], workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'}))
                else:
                    worksheet.write(i, j, row[j])
            i += 1
        if is_close_xlsx:
            workbook.close()
        return path, workbook

    def _with_sql_attribut(self, mail_parm):
        """
        为有sql属性的配置进行参数解析
        :param mail_parm: 邮件内参数
        :return: 返回SQL语句
        """
        config_sql = self.__profession_config[mail_parm['subject']]['sql']
        if self.__profession_config.has_option(mail_parm['subject'], 'sqlparm'):
            parm = self.__profession_config[mail_parm['subject']]['sqlparm'].split()
            LOG.debug('sql语句携带了参数 %s', parm)
            try:
                sql_parm = [re.search(reparm, mail_parm['body']).group(1) for reparm in parm]
            except Exception as err:
                LOG.error('邮件内参数匹配异常:\n%s', str(err))
                return None
            try:
                sql = config_sql.format(sql_parm)
            except IndexError as err:
                LOG.error('请节点[%s]检查配置项目:\n%s', mail_parm['subject'], str(err))
                return None
            return sql
        else:
            return config_sql
