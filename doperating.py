# -*- coding:utf8 -*-
import configparser
import log4p
import uuid
import xlsxwriter
import pyodbc

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
                result_file = self.exec_sql_use_odbc(sql, self.__profession_config[parm['subject']]['database'])
        else:
            LOG.error('未实现方法:%s', self.__profession_config[parm['subject']]['funname'])
            return None

        return result_file

    def exec_sql_use_odbc(self, sql, database):
        db_conn = pyodbc.connect(
            'DRIVER={' + self.__db_config[database]['drive'] + '};SERVER=' + self.__db_config[database][
                'server'] + ';DATABASE=' + database + ';UID=' + self.__db_config[database]['user'] + ';PWD=' +
            self.__db_config[database]['password'])
        cursor = db_conn.cursor()
        i = 1
        j = 0
        path = self.__result_save_path + '/' + str(uuid.uuid1()) + '.xlsx'
        workbook = xlsxwriter.Workbook(path)
        worksheet = workbook.add_worksheet()
        cursor.execute(sql)
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
