# fio-test
python-devel
yum install mysql
#yum install mysql-server
yum install mysql-devel
yum install mariadb-server mariadb



./run-fio [init-image|build-suite|list-suites|run ${suite_name}]

For the new ceph env, please run "init-image" to create new rbds for testing.
Or use "build-suite" to create new test config file for FIO.
Or use "list-suites" to show the previous created test.
Or use "run $test_suite_name" to run test.

