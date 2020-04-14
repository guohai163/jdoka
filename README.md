## Jdoka-自动数据查询系统

做为运营开发可能经常会遇到需求方的一个新系统上线后需求方会需要查询各种运维数据，比如过去30天留存、昨天充值情况、过去1小时新游戏/新活动参与情况。再复杂一些的如指定账号的用户信息，指定时间内的PV|UV等需要频繁查询的情况。简单的一两句sql就能实现，但需求方毕竟不是技术人员不会写SQL语句，也不知道如何操作这些查询终端，但即使会写也不方便把数据库的查询权限开给这么多人。传统的运营团队解决方案基本都是开发后台，或雇佣专职查询人员。

无论哪个解决方法都是高成本的，为了简单的查询开发一个后台。得考虑浏览器兼容、数据分页、权限划分等问题，至少要消耗1个服务器开发1个前端1个测试一天的时间，3人天对于一个中小型团队也是个不小的成本开销。日后这些开发的后台程序的管理与维护也是个问题，经常有业务早已经停止后台权限无法收回等问题。

使用专职查询，对于小团队这个增加这么个岗位成本是更大的，而且大多人类都是反感重复工作的。干不了多久就会开始反感这种频繁重复的查询，也容易出现查询出错的情况。

本程序就是基于运营团队的这个现状下开发出来的，可以自动抓取符合规则的邮件，查询结果并自动回信。减少了运营开发团队后成本支出。

![work](https://raw.githubusercontent.com/wiki/guohai163/jdoka/img/workvs-1.png)

## 目前实现的功能

1. 对于简单的无参数查询，只要配置一个业务配置项目写好sql即可，5分钟即可完成书写到测试上线
2. 对于相对复杂的需要参数的查询，可以通过反射方法，增加sqlscript.py里的方法进行各种复杂查询
3. 白名单功能，如果配置了白名单参数，只有在白名单里的发件人查询才会进行回复

## 安装
测试使用推荐使用docker环境，可以省去odbc安装的繁琐过程。
首先准备好conf目录下的三个配置文件，可以参考该目录下的三个示例文件进行配置。我们看一下每次新增加业务时要配置的业务处理文件，主要就是把写好的SQL放进去即可
~~~ ini
[昨日注册人数]
# 查询脚本
sql = SELECT count(*) as yday_reg_num  FROM [community_login_log] WHERE DateDiff(dd,login_time,getdate())=1
# 要使用的DB，会去db-config.ini进行搜索
database = accountdb_log
# 非必须参数，白名单。
whitelist = guohai@gmail.com
~~~

如果想实现自定义参数等高级功能，更详细的配置说明可以看 [这里](https://github.com/guohai163/jdoka/wiki/ConfigurationFile) 。将mail-config.ini、db-config.ini、profession.conf存放在同一个目录下。比如我们放在了本地/home/jdoka/conf/

启动docker容器
~~~ bash
shell> docker run --rm -v /home/jdoka/conf/:/opt/jdoka/conf/ gcontainer/jdoka:1.0

2020-04-14 06:46:02,579 - gmail.py line+30 - INFO - init GMail class
2020-04-14 06:46:03,505 - gmail.py line+41 - INFO - 邮箱登录成功
2020-04-14 06:46:03,758 - gmail.py line+46 - INFO - 所有邮件数量:0
2020-04-14 06:46:04,138 - jdoka.py line+106 - INFO - 本次查询结束，休眠5分钟
~~~
看到如上提示，代表服务启动成功。我们按配置好的示例发封邮件试试。为了方便搜索，我们需要在查询的的邮件标题前加上[q]来和普通邮件进行区分。

![mail2result.png](https://raw.githubusercontent.com/wiki/guohai163/jdoka/img/mail2result.png)

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