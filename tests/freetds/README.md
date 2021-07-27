# Quick and easy FreeTDS test

## Description

osirium-main contains an [odbc.py](https://github.com/Osirium/osirium-main/blob/317774737bc024827b2d0ca99a6c41d64efb507e/001-python/source/osirium/osirium/odbc.py) utility that connects to MSSQL databases using ODBC.

This directory contains a copy of the odbc.py utility, as well the odbcinst.ini that gets copied in by `osirium-freetds`.

This allows you to test the minimal package requirements to run the utility.

## The test

Firstly run a SQL Express instance:

```
docker run -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=yourStrong(!)Password' -e 'MSSQL_PID=Express' -p 1433:1433 -d mcr.microsoft.com/mssql/server:2017-latest-ubuntu
```

Then connect to it using Microsoft SQL Server Management Studio and make a database called `MYDB`. Create something - e.g. a table called `users`.

Next:

```
docker build --tag freetds . && docker run --rm -ti freetds
```

It will ask for the password set earlier:

```
yourStrong(!)Password
```

Then if all works, you can do a test command such as:

```
SELECT * FROM users;
```

Finally, `exit` to quit.
