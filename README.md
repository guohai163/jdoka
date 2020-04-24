## Jdoka-自动数据查询系统

做为运营开发可能经常会遇到需求方的一个新系统上线后需求方会需要查询各种运维数据，比如过去30天留存、昨天充值情况、过去1小时新游戏/新活动参与情况。再复杂一些的如指定账号的用户信息，指定时间内的PV|UV等需要频繁查询的情况。简单的一两句sql就能实现，但需求方毕竟不是技术人员不会写SQL语句，也不知道如何操作这些查询终端，但即使会写也不方便把数据库的查询权限开给这么多人。传统的运营团队解决方案基本都是开发后台，或雇佣专职查询人员。

无论哪个解决方法都是高成本的，为了简单的查询开发一个后台。得考虑浏览器兼容、数据分页、权限划分等问题，至少要消耗1个服务器开发1个前端1个测试一天的时间，3人天对于一个中小型团队也是个不小的成本开销。日后这些开发的后台程序的管理与维护也是个问题，经常有业务早已经停止后台权限无法收回等问题。

使用专职查询，对于小团队这个增加这么个岗位成本是更大的，而且大多人类都是反感重复工作的。干不了多久就会开始反感这种频繁重复的查询，也容易出现查询出错的情况。

本程序就是基于运营团队的这个现状下开发出来的，可以自动抓取符合规则的邮件，查询结果并自动回信。减少了运营开发团队后成本支出。

![work](https://raw.githubusercontent.com/wiki/guohai163/jdoka/img/workvs-1.png)

## 目前实现的功能

1. 对于简单的无参数或少量参数的查询，只要更新配置文件写好sql即可，5分钟即可完成配置到上线
2. 对于相对复杂的需要个性定制的查询，可以通过反射方法，增加sqlscript.py里的方法进行各种复杂查询
3. 白名单功能，如果配置了白名单参数，只有在白名单里的发件人查询才会进行回复
4. 查询结果使用xlsx格式作为附件发给查询发起者邮箱
5. 查询结果存档，使用sqlite格式，存档目录在 result/result_data.db 中
6. 目前接收查询需求的邮箱需要支持IMAP协议，可以配置目录。只处理指定目录用的邮件，不与正常使用者冲突。
7. 所有查询邮件的标题必须以[q]开头

## 安装
初次使用推荐使用docker环境，可以省去odbc安装的繁琐过程。如果需要支持mssql、mysql以外的数据库，目前推荐使用源码方式。
我们先来讲解基于docker的使用方法。首先准备好conf目录下的三个配置文件，可以参考[github仓库中](https://github.com/guohai163/jdoka/tree/master/conf)该目录下的三个示例文件进行配置。我们看一下具体的配置方法：

### 不带参数的sql查询配置指导
1. 打开 conf/mail-config.ini 文件
    ~~~ ini
    # 邮箱配置，目前国内的邮件服务商大多都使用基于SSL协议的SMTP或IMAP。目前本程序也是基于SSL协议的
    [mail.config]
    imap_server = imap.exmail.qq.com
    imap_port = 993
    user = <email_username>
    password = <email_password>
    # 邮箱盒，如果不设置使用默认收件箱
    box = <directory>
    smtp_server = smtp.exmail.qq.com
    smtp_port = 465
    ~~~
2. 打开 conf/profession.conf 文件
    ~~~ ini
    # 方括号内为你要用的业务名，也是需求方要发的邮件标题
    [昨日注册人数]
    # 查询脚本
    sql = SELECT count(*) as yday_reg_num  FROM account_login_log WHERE DateDiff(dd,login_time,getdate())=1
    # 要使用的DB，会去db-config.ini进行搜索
    database = accountdb-log
    # 自定义参数，白名单。只有白名单内用户发信才进行查询。如无该字段不限制发件人
    whitelist = guohai@gmail.com
    ~~~
3. 打开 conf/db-config.ini 看一下上步操作时使用的DB在本文件是否有，如果不存在需要新建一个节点
    ~~~ ini
    # 方括号内要与上一步一致
    [AccountDB-Log]
    # 服务器IP
    server = 10.0.0.1
    user = <user>
    password = xxxxxxxxxx
    # 数据库类型，目前支持 mssql或mysql
    drive = mssql
    ~~~

将mail-config.ini、db-config.ini、profession.conf存放在同一个目录下。比如我们放在了本地/home/jdoka/conf/

启动docker容器
~~~ bash
# 推荐把结果目录也保存到本地，方便后续的跟踪
# 我们把本地的配置文件目录和结果目录映射到Docker容器内
shell> docker run --rm -v /home/user/conf/:/opt/jdoka/conf/ -v /home/user/result/:/opt/jdoka/result/ gcontainer/jdoka:1.2

2020-04-14 06:46:02,579 - gmail.py line+30 - INFO - init GMail class
2020-04-14 06:46:03,505 - gmail.py line+41 - INFO - 邮箱登录成功
2020-04-14 06:46:03,758 - gmail.py line+46 - INFO - 所有邮件数量:0
2020-04-14 06:46:04,138 - jdoka.py line+106 - INFO - 本次查询结束，休眠5分钟
~~~
看到如上提示，代表服务启动成功。我们按配置好的示例发封邮件试试。邮件标题"[q]昨日注册人数"，收件人为第一步中配置的邮箱账号。点击发送一会结果就会回来，全程不再需要人工干预。

![mail2result.png](https://raw.githubusercontent.com/wiki/guohai163/jdoka/img/mail2result.png)

### 带简单参数的查询配置方法


## 源码安装

本项目使用Python开发，目前基于3.7版本。
1. 克隆项目到本地，并安装依赖包
    ~~~ shell script
    git clone https://github.com/guohai163/jdoka.git
    cd jdoka
    pip install -r requirements.txt
    ~~~
 2. 配置本地的cofnig文件
    ~~~ shell script
    // 邮箱配置
    mv conf/mail-config-example.ini conf/mail-config.ini
    vim mail-config.ini
    // 数据库配置，目前只支持mssql
    mv conf/db-config-example.ini conf/db-config.ini
    vim db-config.ini
    ~~~
 3. 编辑业务处理文件
    ~~~ shell script
    // 业务配置文件
    vim conf/profession.conf
    ~~~
 4. 测试运行
    ~~~ shell script
    python3 jdoka.py
    ~~~
    
===
    
    
![haige](http://guohai.org/assets/wechat.jpg)