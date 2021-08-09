# -*- coding:utf8 -*-
import email
import imaplib
import smtplib
import sys
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import log4p

LOG = log4p.GetLogger('GMail').logger

VERSION = '1.0'

MAIL_HTML = """
<html>
  <head></head>
  <body>
    <p>{0}，你好：
        <p style=\"text-indent: 2em;\">查询结果见附件</p>
        <p style=\"text-indent: 10em;\"><a href=\"https://github.com/guohai163/jdoka\" target=\"view_window\">jdoka</a>.</p>
    </p>
  </body>
</html>
"""

class GMail:
    # TODO:类需要进行重构，需要使用smtp时再进行连接，否则会超时
    query_list = []
    _imap_conn = None
    _user = ''
    _pass = ''
    _smtp_server = ''
    _smtp_port = ''

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
        self._user = user
        self._pass = password
        self._smtp_server = smtp_server
        self._smtp_port = smtp_port

        try:
            self._imap_conn = imaplib.IMAP4_SSL(server, port)
            self._imap_conn.login(user, password)
        except imaplib.IMAP4.error as e:
            LOG.error("imap登录失败: %s" % e)
            sys.exit(1)
        LOG.info("邮箱登录成功")
        if box != '':
            self._imap_conn.select(box)
        else:
            self._imap_conn.select()
        result, data = self._imap_conn.search(None, 'ALL')
        if result == 'OK':
            self.all = data[0].split()
            LOG.info('所有邮件数量:%s' % len(self.all))

    def over(self):
        """
        退出时需要进行调用
        :return:
        """
        if self._imap_conn is not None:
            self._imap_conn.close()
            self._imap_conn.logout()

    def _parse_header(self, msg):
        """解析邮件头"""
        data, charset = email.header.decode_header(msg['subject'])[0]
        mail_date = email.utils.parsedate_to_datetime(msg['Date'])
        message_id = email.utils.parseaddr(msg['Message-ID'])[1]
        mail_from = email.utils.parseaddr(msg['From'])[1]
        return str(data, charset).strip(), mail_from, message_id, mail_date

    def _parse_part_to_str(self, part):
        charset = part.get_charset() or part.get_param('charset') or 'gb2312'

        payload = part.get_payload(decode=True)
        if not payload:
            return ''
        return str(part.get_payload(decode=True), charset).replace("&nbsp;", " ")

    def _parse_body(self, msg):
        mail_body = ''
        LOG.info(msg.get_body(preferencelist=('plain', 'html')))
        for part in msg.walk():
            if not part.is_multipart():
                LOG.info(part)
                name = part.get_param("name")
                if name:
                    fh = email.header.Header(name)
                    fdh = email.header.decode_header(fh)
                    fname = fdh[0][0]
                    print('附件名:', fname)
                else:
                    mail_body += self._parse_part_to_str(part) + '\n'
        return mail_body

    def parse(self):
        nums = self.all
        for num in nums:
            try:
                result, data = self._imap_conn.fetch(num, '(RFC822)')
                if result == 'OK':
                    msg = email.message_from_string(data[0][1].decode())
                    LOG.info(msg)
                    mail_subject, mail_from, message_id, mail_date = self._parse_header(msg)
                    LOG.info('标题：【%s】从：【%s】ID：【%s】日期：【%s】' % (mail_subject, mail_from, message_id, mail_date))
                    mail_body = self._parse_body(msg)
                    LOG.info(mail_body)
                    query_mail = {'messageid': message_id, 'subject': mail_subject, 'from': mail_from,
                                  'body': mail_body, 'num': num, 'date': mail_date}
                    LOG.debug('收到邮件%s', query_mail['subject'])
                    self.query_list.append(query_mail)
            except Exception as e:
                LOG.error('Message %s 解析错误:%s' % (num, e))

    def delete(self, num):
        """
        删除邮件
        :param num: 邮件在邮箱中编号
        :return:
        """
        self._imap_conn.store(num, '+FLAGS', '\\Deleted')

    def send_mail(self, to_mail, subject, attach_path):
        """
        发送邮件方法
        :param attach_path:
        :param to_mail:
        :param subject:
        :param body:
        :return:
        """
        msg = MIMEMultipart()
        msg['From'] = Header('程序自动查询结果', 'utf-8').encode() + ' <%s>' % self._user
        msg['To'] = to_mail
        msg['Subject'] = Header(subject, 'utf-8').encode()
        msg['Jdoka-Version'] = VERSION
        msg['Jdoka-Url'] = 'https://github.com/guohai163/jdoka'
        msg.attach(MIMEText(MAIL_HTML.format(to_mail.split('@')[0]), 'html', 'utf-8'))

        with open(attach_path, 'rb') as f:
            mime = MIMEBase('text/csv', 'csv', filename='query_result.csv')
            mime.add_header('Content-Disposition', 'attachment', filename='query_result.xlsx')
            mime.add_header('Content-ID', '<0>')
            mime.add_header('X-Attachment-Id', '0')
            mime.set_payload(f.read())
            encoders.encode_base64(mime)
            msg.attach(mime)
        try:
            smtp_conn = smtplib.SMTP_SSL(host=self._smtp_server, port=self._smtp_port)
            smtp_conn.login(self._user, self._pass)
        except smtplib.SMTPAuthenticationError as e:
            LOG.error("smtp登录失败: %s" % e)
            return
        smtp_conn.sendmail(from_addr=self._user, to_addrs=to_mail.split(","), msg=msg.as_string())
        smtp_conn.quit()

