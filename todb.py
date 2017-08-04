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
            svctm, rMBs, wMBs, rrqms, rs, util, w_await, tps ) \
            VALUES ('{}', '{}', '{}', '{}', \
            '{}', '{}', '{}', '{}', '{}', '{}', '{}', \
            '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
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
                kwargs['tps'],
            )
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()


    def insert_tb_cephconfigjournaldata(self, casename, node, osd, **kwargs):
        sql = "SELECT * FROM RESULT \
            WHERE case_name = '{}'".format(casename)
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            for row in results:
                caseid = row[0]
        except:
            self.db.rollback()
        sql = "INSERT INTO CEPHCONFIGJDATA(caseid, node, osd, \
            osd_journal_size, journal_max_write_bytes, \
            journal_max_write_entries, journal_throttle_high_multiple, \
            journal_throttle_max_multiple ) \
            VALUES ('{}', '{}', '{}', \
            '{}', '{}', '{}', '{}', '{}')".format(
                caseid,
                node,
                osd,
                kwargs['osd_journal_size'],
                kwargs['journal_max_write_bytes'],
                kwargs['journal_max_write_entries'],
                kwargs['journal_throttle_high_multiple'],
                kwargs['journal_throttle_max_multiple'],
            )
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()


    def insert_tb_cephconfigosddata(self, casename, node, osd, **kwargs):
        sql = "SELECT * FROM RESULT \
            WHERE case_name = '{}'".format(casename)
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            for row in results:
                caseid = row[0]
        except:
            self.db.rollback()
        sql = "INSERT INTO CEPHCONFIGOSDDATA(caseid, node, osd, \
            osd_max_write_size, osd_num_op_tracker_shard, \
            osd_client_message_size_cap, osd_client_message_cap, \
            osd_deep_scrub_stride, osd_op_num_threads_per_shard, \
            osd_op_num_shards, osd_op_threads, osd_op_thread_timeout, \
            osd_op_thread_suicide_timeout, osd_recovery_thread_timeout, \
            osd_recovery_thread_suicide_timeout, osd_disk_threads, \
            osd_map_cache_size, osd_recovery_threads, osd_recovery_op_priority, \
            osd_recovery_max_active, osd_max_backfills, osd_scrub_begin_hour, \
            osd_scrub_end_hour, osd_scrub_sleep, osd_scrub_load_threshold, \
            osd_scrub_chunk_max, osd_scrub_chunk_min ) \
            VALUES ('{}', '{}', '{}', \
            '{}', '{}', '{}', '{}', '{}', \
            '{}', '{}', '{}', '{}', '{}', \
            '{}', '{}', '{}', '{}', '{}', \
            '{}', '{}', '{}', '{}', '{}', \
            '{}', '{}', '{}', '{}')".format(
                caseid,
                node,
                osd,
                kwargs['osd_max_write_size'],
                kwargs['osd_num_op_tracker_shard'],
                kwargs['osd_client_message_size_cap'],
                kwargs['osd_client_message_cap'],
                kwargs['osd_deep_scrub_stride'],
                kwargs['osd_op_num_threads_per_shard'],
                kwargs['osd_op_num_shards'],
                kwargs['osd_op_threads'],
                kwargs['osd_op_thread_timeout'],
                kwargs['osd_op_thread_suicide_timeout'],
                kwargs['osd_recovery_thread_timeout'],
                kwargs['osd_recovery_thread_suicide_timeout'],
                kwargs['osd_disk_threads'],
                kwargs['osd_map_cache_size'],
                kwargs['osd_recovery_threads'],
                kwargs['osd_recovery_op_priority'],
                kwargs['osd_recovery_max_active'],
                kwargs['osd_max_backfills'],
                kwargs['osd_scrub_begin_hour'],
                kwargs['osd_scrub_end_hour'],
                kwargs['osd_scrub_sleep'],
                kwargs['osd_scrub_load_threshold'],
                kwargs['osd_scrub_chunk_max'],
                kwargs['osd_scrub_chunk_min'],
            )
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()


    def insert_tb_cephconfigrbddata(self, casename, node, osd, **kwargs):
        sql = "SELECT * FROM RESULT \
            WHERE case_name = '{}'".format(casename)
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            for row in results:
                caseid = row[0]
        except:
            self.db.rollback()
        sql = "INSERT INTO CEPHCONFIGRBDDATA(caseid, node, osd, \
            rbd_cache, rbd_cache_size, rbd_cache_target_dirty, \
            rbd_cache_max_dirty, rbd_cache_max_dirty_age, rbd_cache_writethrough_until_flush ) \
            VALUES ('{}', '{}', '{}', \
            '{}', '{}', '{}', \
            '{}', '{}', '{}')".format(
                caseid,
                node,
                osd,
                kwargs['rbd_cache'],
                kwargs['rbd_cache_size'],
                kwargs['rbd_cache_target_dirty'],
                kwargs['rbd_cache_max_dirty'],
                kwargs['rbd_cache_max_dirty_age'],
                kwargs['rbd_cache_writethrough_until_flush'],
            )
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()

    def insert_tb_cephconfigclientdata(self, casename, node, osd, **kwargs):
        sql = "SELECT * FROM RESULT \
            WHERE case_name = '{}'".format(casename)
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            for row in results:
                caseid = row[0]
        except:
            self.db.rollback()
        sql = "INSERT INTO CEPHCONFIGCDATA(caseid, node, osd, \
            objecter_inflight_ops, objecter_inflight_op_bytes ) \
            VALUES ('{}', '{}', '{}', \
            '{}', '{}')".format(
                caseid,
                node,
                osd,
                kwargs['objecter_inflight_ops'],
                kwargs['objecter_inflight_op_bytes'],
            )
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()

    def insert_tb_cephconfigfilestonedata(self, casename, node, osd, **kwargs):
        sql = "SELECT * FROM RESULT \
            WHERE case_name = '{}'".format(casename)
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            for row in results:
                caseid = row[0]
        except:
            self.db.rollback()
        sql = "INSERT INTO CEPHCONFIGFSDATA(caseid, node, osd, \
            max_open_files, filestore_expected_throughput_bytes, \
            filestore_expected_throughput_ops, filestore_max_sync_interval, \
            filestore_min_sync_interval, filestore_queue_max_bytes, \
            filestore_queue_max_ops, filestore_queue_high_delay_multiple, \
            filestore_queue_max_delay_multiple, filestore_ondisk_finisher_threads, \
            filestore_apply_finisher_threads, filestore_commit_timeout, \
            filestore_fd_cache_shards, filestore_fd_cache_size, \
            filestore_wbthrottle_enable, filestore_op_threads, \
            filestore_op_thread_timeout, filestore_op_thread_suicide_timeout ) \
            VALUES ('{}', '{}', '{}', \
            '{}', '{}', '{}','{}', '{}', \
            '{}', '{}', '{}','{}', '{}', \
            '{}', '{}', '{}','{}', '{}', \
            '{}', '{}', '{}')".format(
                caseid,
                node,
                osd,
                kwargs['debug_paxos'],
                kwargs['max_open_files'],
                kwargs['filestore_expected_throughput_bytes'],
                kwargs['filestore_expected_throughput_ops'],
                kwargs['filestore_max_sync_interval'],
                kwargs['filestore_min_sync_interval'],
                kwargs['filestore_queue_max_bytes'],
                kwargs['filestore_queue_max_ops'],
                kwargs['filestore_queue_high_delay_multiple'],
                kwargs['filestore_queue_max_delay_multiple'],
                kwargs['filestore_ondisk_finisher_threads'],
                kwargs['filestore_apply_finisher_threads'],
                kwargs['filestore_commit_timeout'],
                kwargs['filestore_fd_cache_shards'],
                kwargs['filestore_fd_cache_size'],
                kwargs['filestore_wbthrottle_enable'],
                kwargs['filestore_op_threads'],
                kwargs['filestore_op_thread_timeout'],
                kwargs['filestore_op_thread_suicide_timeout'],
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
            tps float,
            util float,
            w_await float,
            foreign key(caseid) references RESULT(id) ) ENGINE=MyISAM"""
        self.cursor.execute(sql)

    def create_tb_cephconfigfilestonedata(self):
        sql = """CREATE TABLE CEPHCONFIGFSDATA (
            id int auto_increment primary key,
            caseid int not null,
            node  char(20),
            osd  char(20),
            max_open_files char(20),
            filestore_expected_throughput_bytes char(20),
            filestore_expected_throughput_ops char(20),
            filestore_max_sync_interval char(20),
            filestore_min_sync_interval char(20),
            filestore_queue_max_bytes char(20),
            filestore_queue_max_ops char(20),
            filestore_queue_high_delay_multiple char(20),
            filestore_queue_max_delay_multiple char(20),
            filestore_ondisk_finisher_threads char(20),
            filestore_apply_finisher_threads char(20),
            filestore_commit_timeout char(20),
            filestore_fd_cache_shards char(20),
            filestore_fd_cache_size char(20),
            filestore_wbthrottle_enable char(20),
            filestore_op_threads char(20),
            filestore_op_thread_timeout char(20),
            filestore_op_thread_suicide_timeout char(20),
            foreign key(caseid) references RESULT(id) ) ENGINE=MyISAM"""
        self.cursor.execute(sql)

    def create_tb_cephconfigjournaldata(self):
        sql = """CREATE TABLE CEPHCONFIGJDATA (
            id int auto_increment primary key,
            caseid int not null,
            node  char(20),
            osd  char(20),
            osd_journal_size char(20),
            journal_max_write_bytes char(20),
            journal_max_write_entries char(20),
            journal_throttle_high_multiple char(20),
            journal_throttle_max_multiple char(20),
            foreign key(caseid) references RESULT(id) ) ENGINE=MyISAM"""
        self.cursor.execute(sql)

    def create_tb_cephconfigrbddata(self):
        sql = """CREATE TABLE CEPHCONFIGRBDDATA (
            id int auto_increment primary key,
            caseid int not null,
            node  char(20),
            osd  char(20),
            rbd_cache char(20),
            rbd_cache_size char(20),
            rbd_cache_target_dirty char(20),
            rbd_cache_max_dirty char(20),
            rbd_cache_max_dirty_age char(20),
            rbd_cache_writethrough_until_flush char(20),
            foreign key(caseid) references RESULT(id) ) ENGINE=MyISAM"""
        self.cursor.execute(sql)

    def create_tb_cephconfigosddata(self):
        sql = """CREATE TABLE CEPHCONFIGOSDATA (
            id int auto_increment primary key,
            caseid int not null,
            node  char(20),
            osd  char(20),
            osd_max_write_size char(20),
            osd_num_op_tracker_shard char(20),
            osd_client_message_size_cap char(20),
            osd_client_message_cap char(20),
            osd_deep_scrub_stride char(20),
            osd_op_num_threads_per_shard char(20),
            osd_op_num_shards char(20),
            osd_op_threads char(20),
            osd_op_thread_timeout char(20),
            osd_op_thread_suicide_timeout char(20),
            osd_recovery_thread_timeout char(20),
            osd_recovery_thread_suicide_timeout char(20),
            osd_disk_threads char(20),
            osd_map_cache_size char(20),
            osd_recovery_threads char(20),
            osd_recovery_op_priority char(20),
            osd_recovery_max_active char(20),
            osd_max_backfills char(20),
            osd_scrub_begin_hour char(20),
            osd_scrub_end_hour char(20),
            osd_scrub_sleep char(20),
            osd_scrub_load_threshold char(20),
            osd_scrub_chunk_max char(20),
            osd_scrub_chunk_min char(20),
            foreign key(caseid) references RESULT(id) ) ENGINE=MyISAM"""
        self.cursor.execute(sql)

    def create_tb_cephconfigclientdata(self):
        sql = """CREATE TABLE CEPHCONFIGCDATA (
            id int auto_increment primary key,
            caseid int not null,
            node  char(20),
            osd  char(20),
            objecter_inflight_ops char(20),
            objecter_inflight_op_bytes char(20),
            foreign key(caseid) references RESULT(id) ) ENGINE=MyISAM"""
        self.cursor.execute(sql)

    def create_tb_perfdumpdata(self):
        sql = """CREATE TABLE PERFDUMPDATA (
            id int auto_increment primary key,
            caseid int not null,
            node  char(20),
            filestore__queue_transaction_latency_avg char(20),
            filestore__bytes char(20),
            foreign key(caseid) references RESULT(id) ) ENGINE=MyISAM"""
        self.cursor.execute(sql)



    def close_db(self):
        self.db.close()

    def cleanup_db(self):
        self.cursor.execute("DROP TABLE IF EXISTS PERFDUMPDATA")
        self.cursor.execute("DROP TABLE IF EXISTS CEPHCONFIGFSDATA")
        self.cursor.execute("DROP TABLE IF EXISTS CEPHCONFIGJDATA")
        self.cursor.execute("DROP TABLE IF EXISTS CEPHCONFIGRBDDATA")
        self.cursor.execute("DROP TABLE IF EXISTS CEPHCONFIGOSDATA")
        self.cursor.execute("DROP TABLE IF EXISTS CEPHCONFIGCDATA")
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
    todb.create_tb_cephconfigfilestonedata()
    todb.create_tb_cephconfigjournaldata()
    todb.create_tb_cephconfigrbddata()
    todb.create_tb_cephconfigosddata()
    todb.create_tb_cephconfigclientdata()
    todb.create_tb_perfdumpdata()
    todb.close_db()

if __name__ == '__main__':
    main()

