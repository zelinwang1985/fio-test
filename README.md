# fio-test


5.5.52-MariaDB
```bash
yum install -y gcc python-devel python-pip mysql mysql-devel mariadb-server mariadb

systemctl start mariadb
systemctl enable mariadb
```

# create database
mysql
MariaDB [(none)]> insert into mysql.user(Host,User,Password) values('localhost','test',password('1234'));
MariaDB [(none)]> flush privileges;
MariaDB [(none)]> create database fiotest;
MariaDB [(none)]> grant all privileges on fiotest.\* to test@localhost identified by '1234';
MariaDB [(none)]> exit;


# install dependenies
```bash
pip install --upgrade pip
pip install -r requirement.txt
```


./run-fio [init-image|build-suite|list-suites|run ${suite_name}]

For the new ceph env, please run "init-image" to create new rbds for testing.
Or use "build-suite" to create new test config file for FIO.
Or use "list-suites" to show the previous created test.
Or use "run $test_suite_name" to run test.

