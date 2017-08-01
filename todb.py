import MySQLdb



class ToDB(object):
    def __init__(self):
        self.db = MySQLdb.connect("localhost","test","1234","fiotest" )

        self.cursor = self.db.cursor()

    def insert_tb_result(self, **kwargs):
        sql = "INSERT INTO RESULT(case_name, \
            time, blocksize, iodepth, numberjob, imagenum, \
            clientnum, iops, readwrite, lat ) \
            VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', \
            '{}', '{}', '{}' )".format(
                kwargs['case_name'],
                kwargs['time'],
                kwargs['blocksize'],
                kwargs['iodepth'],
                kwargs['numberjob'],
                kwargs['imagenum'],
                kwargs['clientnum'],
                kwargs['iops'],
                kwargs['readwrite'],
                kwargs['lat']
        )
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()

    def insert_tb_sarmemdata(self, casename, node, **kwargs):
        sql = "SELECT * FROM RESULT \
            WHERE case_name = '{}'".format(casename)
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            for row in results:
                caseid = row[0]
        except:
            self.db.rollback()
        sql = "INSERT INTO SARMEMDATA(caseid, node, time, \
            kbmemfree, kbmemused, memused, kbbuffers, kbcached, \
            kbcommit, commit, kbactive, kbinact, kbdirty ) \
            VALUES ('{}', '{}', '{}', \
            '{}', '{}', '{}', '{}', '{}', \
            '{}', '{}', '{}', '{}', '{}')".format(
                caseid,
                node,
                kwargs['time'],
                kwargs['kbmemfree'],
                kwargs['kbmemused'],
                kwargs['memused'],
                kwargs['kbbuffers'],
                kwargs['kbcached'],
                kwargs['kbcommit'],
                kwargs['commit'],
                kwargs['kbactive'],
                kwargs['kbinact'],
                kwargs['kbdirty'],
        )

        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()

    def insert_tb_sarcpudata(self, casename, node, **kwargs):
        sql = "SELECT * FROM RESULT \
            WHERE case_name = '{}'".format(casename)
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            for row in results:
                caseid = row[0]
        except:
            self.db.rollback()
        sql = "INSERT INTO SARCPUDATA(caseid, node, \
            time, usr, nice, sys, iowait, steal, \
            irq, soft, guest, gnice, idle ) \
            VALUES ('{}', '{}', '{}', '{}', '{}', '{}', \
            '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
                caseid,
                node,
                kwargs['time'],
                kwargs['usr'],
                kwargs['nice'],
                kwargs['sys'],
                kwargs['iowait'],
                kwargs['steal'],
                kwargs['irq'],
                kwargs['soft'],
                kwargs['guest'],
                kwargs['gnice'],
                kwargs['idle'],
        )

        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()

    def insert_tb_sarnicdata(self, casename, node, network, **kwargs):
        sql = "SELECT * FROM RESULT \
            WHERE case_name = '{}'".format(casename)
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            for row in results:
                caseid = row[0]
        except:
            self.db.rollback()
        sql = "INSERT INTO SARNICDATA(caseid, node, network, time, \
            rxpcks, txpcks, rxkBs, txkBs, rxcmps, txcmps, rxmcsts ) \
            VALUES ('{}', '{}', '{}', '{}', \
            '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
                caseid,
                node,
                network,
                kwargs['time'],
                kwargs['rxpcks'],
                kwargs['txpcks'],
                kwargs['rxkBs'],
                kwargs['txkBs'],
                kwargs['rxcmps'],
                kwargs['txcmps'],
                kwargs['rxmcsts'],
        )

        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()

    def insert_tb_iostatdata(self, casename, node, osdnum, disk_name, **kwargs):
        sql = "SELECT * FROM RESULT \
            WHERE case_name = '{}'".format(casename)
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            for row in results:
                caseid = row[0]
        except:
            self.db.rollback()
        sql = "INSERT INTO IOSTATDATA(caseid, node, osdnum, diskname, \
            time, wrqms, avgrqsz, r_await, await, ws, avgqusz, \
            svctm, rMBs, wMBs, rrqms, rs, util, w_await ) \
            VALUES ('{}', '{}', '{}', '{}', \
            '{}', '{}', '{}', '{}', '{}', '{}', '{}', \
            '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
                caseid,
                node,
                osdnum,
                disk_name,
                kwargs['time'],
                kwargs['wrqms'],
                kwargs['avgrqsz'],
                kwargs['r_await'],
                kwargs['await'],
                kwargs['ws'],
                kwargs['avgqusz'],
                kwargs['svctm'],
                kwargs['rMBs'],
                kwargs['wMBs'],
                kwargs['rrqms'],
                kwargs['rs'],
                kwargs['util'],
                kwargs['w_await'],
        )
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()

    def insert_tb_cephconfigdata(self, casename, node, osd, **kwargs):
        sql = "SELECT * FROM RESULT \
            WHERE case_name = '{}'".format(casename)
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            for row in results:
                caseid = row[0]
        except:
            self.db.rollback()
        sql = "INSERT INTO CEPHCONFIGDATA(caseid, node, osd, \
            debug_paxos ) \
            VALUES ('{}', '{}', '{}', \
            '{}')".format(
                caseid,
                node,
                osd,
                kwargs['debug_paxos'],
        )
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()

    def create_tb_result(self):
        sql = """CREATE TABLE RESULT (
            id  int auto_increment primary key,
            case_name  CHAR(100) NOT NULL,
            time datetime,
            blocksize  CHAR(20),
            iodepth  int,
            numberjob  int,
            imagenum  int,
            clientnum  int,
            iops  int,
            readwrite  CHAR(20),
            lat  float ) ENGINE=MyISAM"""
        self.cursor.execute(sql)

    def create_tb_sarcpudata(self):
        sql = """CREATE TABLE SARCPUDATA (
            id int auto_increment primary key,
            caseid int not null,
            node  char(20),
            time  datetime,
            usr float,
            nice float,
            sys float,
            iowait float,
            steal float,
            irq float,
            soft float,
            guest float,
            gnice float,
            idle float,
            foreign key(caseid) references RESULT(id) ) ENGINE=MyISAM"""
        self.cursor.execute(sql)

    def create_tb_sarmemdata(self):
        sql = """CREATE TABLE SARMEMDATA (
            id int auto_increment primary key,
            caseid int not null,
            node  char(20),
            time  datetime,
            kbmemfree int,
            kbmemused int,
            memused float,
            kbbuffers int,
            kbcached int,
            kbcommit int,
            commit float,
            kbactive int,
            kbinact int,
            kbdirty int,
            foreign key(caseid) references RESULT(id) ) ENGINE=MyISAM"""
        self.cursor.execute(sql)


    def create_tb_sarnicdata(self):
        sql = """CREATE TABLE SARNICDATA (
            id int auto_increment primary key,
            caseid int not null,
            node  char(20),
            network char(20),
            time datetime,
            rxpcks float,
            txpcks float,
            rxkBs float,
            txkBs float,
            rxcmps float,
            txcmps float,
            rxmcsts float,
            foreign key(caseid) references RESULT(id) ) ENGINE=MyISAM"""
        self.cursor.execute(sql)

    def create_tb_iostatdata(self):
        sql = """CREATE TABLE IOSTATDATA (
            id int auto_increment primary key,
            caseid int not null,
            node char(20),
            osdnum char(20),
            diskname char(20),
            time datetime,
            wrqms float,
            avgrqsz float,
            r_await float,
            await float,
            ws float,
            avgqusz float,
            svctm float,
            rMBs float,
            wMBs float,
            rrqms float,
            rs float,
            util float,
            w_await float,
            foreign key(caseid) references RESULT(id) ) ENGINE=MyISAM"""
        self.cursor.execute(sql)

    def create_tb_cephconfigdata(self):
        sql = """CREATE TABLE CEPHCONFIGDATA (
            id int auto_increment primary key,
            caseid int not null,
            node  char(20),
            osd  char(20),
            debug_paxos char(20),
            foreign key(caseid) references RESULT(id) ) ENGINE=MyISAM"""
        self.cursor.execute(sql)

    def close_db(self):
        self.db.close()

    def cleanup_db(self):
        self.cursor.execute("DROP TABLE IF EXISTS CEPHCONFIGDATA")
        self.cursor.execute("DROP TABLE IF EXISTS IOSTATDATA")
        self.cursor.execute("DROP TABLE IF EXISTS SARCPUDATA")
        self.cursor.execute("DROP TABLE IF EXISTS SARMEMDATA")
        self.cursor.execute("DROP TABLE IF EXISTS SARNICDATA")
        self.cursor.execute("DROP TABLE IF EXISTS RESULT")


def main():

    todb = ToDB()
    todb.cleanup_db()
    todb.create_tb_result()
    todb.create_tb_sarcpudata()
    todb.create_tb_sarmemdata()
    todb.create_tb_iostatdata()
    todb.create_tb_sarnicdata()
    todb.create_tb_cephconfigdata()
    todb.close_db()

if __name__ == '__main__':
    main()

