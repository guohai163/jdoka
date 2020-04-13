# -*- coding:utf8 -*-
import configparser
import log4p
import uuid
import xlsxwriter
import pyodbc
import sqlscript

LOG = log4p.GetLogger('DOperating').logger

DB_TYPE = {'mssql': 'ODBC Driver 17 for SQL Server', 'mysql': 'MySQL ODBC 8.0 Driver'}


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

        if not self._check_white_list(parm):
            # 白名单检查未通过
            return None
        # 准备开始调用
        if self.__profession_config.has_option(parm['subject'], 'sql'):
            # 如果业务配置项中有sql属性，直接执行sql语句
            sql = self.__profession_config[parm['subject']]['sql']
            return self._exec_sql_use_odbc(sql, self.__profession_config[parm['subject']]['database'])
        # 反射方法
        if hasattr(sqlscript, self.__profession_config[parm['subject']]['funname']):
            LOG.debug('方法%s反射成功', self.__profession_config[parm['subject']]['funname'])
            pro_func = getattr(sqlscript, self.__profession_config[parm['subject']]['funname'])
            sql = pro_func(self.__profession_config, parm)
            if sql is None:
                LOG.error('返回的sql为空')
                return None
            else:
                result_file = self._exec_sql_use_odbc(sql, self.__profession_config[parm['subject']]['database'])
        else:
            LOG.error('未实现方法:%s', self.__profession_config[parm['subject']]['funname'])
            return None

        return result_file

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
        if whitelist.find(parm['from'], 0, len(whitelist)) == -1:
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
            LOG.error('数据库类型[%s]不被支持，请看说明文档',self.__db_config[database]['drive'])
            return None

        db_conn = pyodbc.connect(
            'DRIVER={' + DB_TYPE[self.__db_config[database]['drive']] + '};SERVER=' + self.__db_config[database][
                'server'] + ';DATABASE=' + database + ';UID=' + self.__db_config[database]['user'] + ';PWD=' +
            self.__db_config[database]['password'])
        cursor = db_conn.cursor()
        path = self.__result_save_path + '/' + str(uuid.uuid1()) + '.xlsx'
        workbook = xlsxwriter.Workbook(path)
        worksheet = workbook.add_worksheet()
        cursor.execute(sql)
        # i和j循环使用表示excel的横和列坐标用
        i = 1
        j = 0
        for desc in cursor.description:
            worksheet.write(0, j, desc[0])
            j += 1
        for row in cursor:
            j = 0
            for col in row:
                worksheet.write(i, j, col)
                j += 1
            i += 1
        workbook.close()
        db_conn.close()
        return path
