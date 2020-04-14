## Jdoka-自动数据查询系统

做为运营开发可能经常会遇到需求方的一个新系统上线后需求方会需要查询各种运维数据，比如过去30天留存、昨天充值情况、过去1小时新游戏新活动参与情况。再复杂一些的如指定账号的用户信息，指定时间内的PV|UV等需要频繁查询的情况。但是需求方毕竟不是技术人员不会写SQL语句，但即使会写也不方便把数据库的查询权限开给这么多人。传统的运营团队解决方案基本都是开发后台，或雇佣专职查询人员。

无论哪个解决方法都是高成本的，为了简单的查询开发后台。得考虑浏览器兼容、数据分页、权限划分登问题，至少要消耗1个服务器开发1个前端1个测试一天的时间，3人天对于一个中小型团队也是个不小的成本开销。最后后台过多后维护也是个问题，经常有业务早已经停止后台权限无法收回等问题。

使用专职查询，大多人类都是反感重复查询的。干不了多久就会开始反感这种频繁重复的查询，也容易出现查询出错的情况。

本程序就是基于运营团队的这个现状下开发出来的，可以自动抓取符合规则的邮件，查询结果并自动回信。可以大大方便开发团队后台制作的成本。

1. 对于简单的无参数查询，只要配置一个业务配置项目写好sql即可，5分钟即可完成书写到测试上线
2. 对于相对复杂的需要参数的查询，可以通过反射方法，增加sqlscript.py里的方法进行各种复杂查询
3. 白名单功能，如果配置了白名单参数，只有在白名单里的发件人查询才会进行回复

### 安装
首先准备好如果文件
1. profession.conf

#### Docker安装

#### 源码安装 
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