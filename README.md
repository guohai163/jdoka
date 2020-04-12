## 自动数据查询系统

本程序可以自动抓取符合规则的邮件，查询结果并自动回信。可以大大方便开发团队后台制作的成本。

### 安装
#### Docker安装

#### 源码安装 
本项目使用Python开发，目前基于3.7版本。
1. 克隆项目到本地，并安装依赖包
    ~~~ shell script
    git clone https://github.com/guohai163/auto-database-query.git
    cd auto-database-query
    pip install -r requirements.txt
    ~~~
 2. 配置本地的cofnig文件
    ~~~ shell script
    // 邮箱配置
    mv mail-config-example.ini mail-config.ini
    vim mail-config.ini
    // 数据库配置，目前只支持mssql
    mv db-config-example.ini db-config.ini
    vim db-config.ini
    ~~~
 3. 编辑业务处理文件
    ~~~ shell script
    // 业务配置文件
    vim profession.conf
    // SQL生成方法
    vim sqlscript.py
    ~~~
 4. 测试运行
    ~~~ shell script
    python3 qmain.py
    ~~~