# -*- coding:utf8 -*-
import sys
import imaplib, email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
import log4p

LOG = log4p.GetLogger('GMail').logger

class GMail:
    query_list = []
    __imap_conn = None
    __smtp_conn = None
    __from_mail = ''

    def __init__(self, server, port, user, password, box, smtp_server, smtp_port):
        """
        构造方法
        :param server: 服务器IP
        :param port: 服务器端口
        :param user: 用户名
        :param password: 密码
        :param box: 收件箱
        """
        LOG.info('init GMail class')
        self.__from_mail = user
        if smtp_server != '':
            self.__smtp_conn = SMTP_SSL(host=smtp_server, port=smtp_port)
            self.__smtp_conn.login(user, password)
        try:
            self.__imap_conn = imaplib.IMAP4_SSL(server, port)
            self.__imap_conn.login(user, password)
        except imaplib.IMAP4.error as e:
            LOG.error("登录失败: %s" % e)
            sys.exit(1)
        LOG.info("邮箱登录成功")
        self.__imap_conn.select(box)
        result, data = self.__imap_conn.search(None, 'ALL')
        if result == 'OK':
            self.all = data[0].split()
            LOG.info('所有邮件数量:%s' % len(self.all))

    def over(self):
        """
        退出时需要进行调用
        :return:
        """
        if self.__imap_conn is not None:
            self.__imap_conn.close()
            self.__imap_conn.logout()
        if self.__smtp_conn is not None:
            self.__smtp_conn.quit()

    def __parse_header(self, msg):
        """解析邮件头"""
        data, charset = email.header.decode_header(msg['subject'])[0]
        return str(data, charset), email.utils.parseaddr(msg['From'])[1]

    def __parse_part_to_str(self, part):
        charset = part.get_charset() or 'gb2312'
        payload = part.get_payload(decode=True)
        if not payload:
            return
        return str(part.get_payload(decode=True), charset)

    def __parse_body(self, msg):
        __mail_body = ''
        for part in msg.walk():
            if not part.is_multipart():
                # charset = part.get_charset()
                # contenttype = part.get_content_type()
                name = part.get_param("name")
                if name:
                    fh = email.header.Header(name)
                    fdh = email.header.decode_header(fh)
                    fname = fdh[0][0]
                    print('附件名:', fname)
                else:
                    __mail_body += self.__parse_part_to_str(part) + '\n'
        return __mail_body

    def parse(self):
        nums = self.all
        for num in nums:
            try:
                result, data = self.__imap_conn.fetch(num, '(RFC822)')
                if result == 'OK':
                    msg = email.message_from_string(data[0][1].decode())
                    mail_subject, mail_from = self.__parse_header(msg)
                    mail_body = self.__parse_body(msg)
                    __query_mail = {'subject': mail_subject, 'from': mail_from, 'body': mail_body, 'num': num}
                    LOG.debug('收到邮件%s', __query_mail['subject'])
                    self.query_list.append(__query_mail)
            except Exception as e:
                LOG.error('Message %s 解析错误:%s' % (num, e))

    def delete(self, num):
        """
        删除邮件
        :param num: 邮件在邮箱中编号
        :return:
        """
        self.__imap_conn.store(num, '+FLAGS', '\\Deleted')

    def send_mail(self, to_mail, subject, attach_path):
        """
        发送邮件方法
        :param attach_path:
        :param to_mail:
        :param subject:
        :param body:
        :return:
        """
        __msg = MIMEMultipart()
        __msg['From'] = '程序自动查询结果 <%s>' % self.__from_mail
        __msg['To'] = to_mail
        __msg['Subject'] = Header(subject, 'utf-8').encode()
        __msg.attach(MIMEText('查询结果见附件', 'plain', 'utf-8'))

        with open(attach_path, 'rb') as f:
            __mime = MIMEBase('text/csv', 'csv', filename='query_result.csv')
            __mime.add_header('Content-Disposition', 'attachment', filename='query_result.csv')
            __mime.add_header('Content-ID', '<0>')
            __mime.add_header('X-Attachment-Id', '0')
            __mime.set_payload(f.read())
            encoders.encode_base64(__mime)
            __msg.attach(__mime)

        self.__smtp_conn.sendmail(from_addr=self.__from_mail, to_addrs=to_mail, msg=__msg.as_string())
