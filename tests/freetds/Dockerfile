FROM ubuntu:focal-20210713

RUN apt update \
 && apt install --yes --no-install-recommends \
    build-essential \
    nano \
    python3-dev \
    python3-pip \
    tdsodbc \
    unixodbc-dev \
    ;

RUN pip3 install pyodbc setproctitle six

COPY . .

WORKDIR /odbc

CMD [ "python3", "-m", "odbc", "--database=MYDB", "--instance=Default", "--port=1433", "sa@192.168.2.1"]
