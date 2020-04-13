## 配置文件说明
### db-config.ini
此文件中主要存储数据库连接所用到的服务器地址、用户名密码，以及数据库类型【目前只支持Mssql和Mysql】。
~~~ ini
# 数据库名，后续的profession.conf文件中会用到
[AccountDB]
# 服务器地址，可以是域名或IP
server = 10.0.0.1
# 连接用户名
user = db_user
# 连接密码
password = db_pass
# 数据库类型
drive = mssql | mysql

# 需要用到更数据库继续追加即可
~~~

### mail-config.ini
邮箱的配置项，本系统当前只支持imap_ssl进行收信，使用smtp_ssl协议进行发信。收发信时验证的用户名密码使用同一套。
~~~ ini
# 配置示例使用的是腾讯企业邮箱服务器
[mail.config]
imap_server = imap.exmail.qq.com
imap_port = 993
user = <email_username>
password = <email_password>
# 在收件箱内手工创建的目录，因此邮箱为个人邮箱。
# 为了方便同时的个人使用，会把需要处理的信自动过滤到此目录
box = <directory>
smtp_server = smtp.exmail.qq.com
smtp_port = 465
~~~

### profession.conf

核心的业务配置文件。
1. 初级：直接使用sql进行查询。其中白名单为非必须项，当不配置时不进行检查所有发件人过来的请求都会进行查询。当配置此项后发件人必须在此列表中。
    ~~~ ini
    [昨日注册人数]
    # 查询脚本
    sql = SELECT count(*) as yday_reg_num  FROM [community_login_log] WHERE DateDiff(dd,login_time,getdate())=1
    # 要使用的DB，会去db-config.ini进行搜索
    database = accountdb-log
    # 自定义参数，白名单。
    whitelist = guohai@gmail.com
    ~~~