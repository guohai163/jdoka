FROM python:3.7

MAINTAINER GUOHAI.ORG

WORKDIR /tmp

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get -y update && \
    ACCEPT_EULA=Y apt-get -y install msodbcsql17 && \
    ACCEPT_EULA=Y apt-get -y install mssql-tools
ENV PATH="${PATH}:/opt/mssql-tools/bin"
RUN apt-get -y install unixodbc-dev && \
    apt-get -y install libgssapi-krb5-2 && \
    odbcinst -j
RUN wget https://dev.mysql.com/get/Downloads/Connector-ODBC/8.0/mysql-connector-odbc-8.0.19-linux-debian10-x86-64bit.tar.gz && \
    tar -zxf mysql-connector-odbc-8.0.19-linux-debian10-x86-64bit.tar.gz && \
    cp mysql-connector-odbc-8.0.19-linux-debian10-x86-64bit/bin/* /usr/local/bin && \
    cp mysql-connector-odbc-8.0.19-linux-debian10-x86-64bit/lib/* /usr/local/lib && \
    myodbc-installer -a -d -n "MySQL ODBC 8.0 Driver" -t "Driver=/usr/local/lib/libmyodbc8w.so" && \
    myodbc-installer -d -l && \
    rm -rf /tmp/*

WORKDIR /opt/jdoka

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "/opt/jdoka/qmain.py" ]