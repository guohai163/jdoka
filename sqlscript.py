import re
import log4p

LOG = log4p.GetLogger('DOperating').logger


def idcard_query(profession_config, parm):
    """
    身份证查询
    :param profession_config: profession配置文件
    :param parm: 用邮件内容组成的参数
    :return:
    """
    LOG.debug('准备查询身份证')
    # 白名单检查
    whitelist = profession_config[parm['subject']]['whitelist']
    if whitelist.find(parm['from'], 0, len(whitelist)) == -1:
        LOG.error('查询人不在白名单中，请检查 %s', parm['subject'])
        return None
    # 处理查询数据
    accounts = re.search(r'account:([^\r\n]+)', parm['body'], re.M | re.I).group(1).split(',')
    LOG.debug('待查询账号:%s', accounts)
    # 查询成功，生成SQL语句
    if len(accounts) == 0:
        LOG.debug('解析错误，未进行数据查询')
        return None
    else:
        # 按多条in进行查询准备SQL
        sql = """select a.account,b.cer_number,[nickname] from [userid_account_rel] a
                        inner join [game_person_detail] b on a.user_id=b.user_id
                        where a.account in ('%s')""" % '\',\''.join(accounts)
        LOG.debug(sql)
    return sql


def batch_query(profession_config, parm):
    """
    批号查询，多参数演示
    :param profession_config: 配置
    :param parm: 参数
    :return:
    """
    min_code = re.search(r'min_code:([^\r\n]+)', parm['body']).group(1)
    max_code = re.search(r'max_code:([^\r\n]+)', parm['body']).group(1)
    sql = "SELECT * FROM vaccine_batch_tb where code>%s and code<%s" % (min_code, max_code)
    LOG.debug(sql)
    return sql