import os
import sys
import argparse
import datetime
import shutil
import subprocess
import re
import time
import paramiko
from multiprocessing import Process
import json
import yaml
import socket,struct

from todb import ToDB

class SysInfo(object):

    def __init__(self, havedb=False):
        if havedb:
            self.db = ToDB()
        self.havedb = havedb
        self.host_list = []
        cmd = 'ceph osd tree | grep host'
        items_list = subprocess.check_output(cmd, shell=True).split('\n')
        del items_list[-1]
        for item in items_list:
            match = re.search('host (\S*)\s+', item)
            self.host_list.append(match.group(1))

    def run_sshcmds(self, host, cmds):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(hostname=host, port=22, username='root', password='passw0rd')
        for cmd in cmds:
            print "exec {} in {}.".format(cmd, host)
            ssh.exec_command(cmd)
        ssh.close()

    def sys_info(self, host):
        cmds = ['sar -A 1 >/tmp/sar.log &',
            'date >/tmp/iostat.log; iostat -p -dxm 1 >>/tmp/iostat.log &',
            'while true; do ceph -s --format json-pretty; sleep 1; done >/tmp/ceph.log &']
        self.run_sshcmds(host, cmds)

    def get_sys_info(self):
        for host in self.host_list:
            print 'get sysinfo {}'.format(host)
            p = Process(target=self.sys_info, args=(host,))
            p.start()
            p = Process(target=self.get_ceph_conf, args=(host,))
            p.start()

    def cleanup_sys_info(self, host):
        cmds = [
            'kill -9 `ps -ef | grep sar | grep -v grep | awk \'{print $2}\'`',
            'kill -9 `ps -ef | grep iostat | grep -v grep | awk \'{print $2}\'`',
            'kill -9 `ps -ef | grep \'ceph -s\' | grep -v grep | awk \'{print $2}\'`',
            'kill -9 `ps -ef | grep \'ceph -name\' | grep -v grep | awk \'{print $2}\'`']
        self.run_sshcmds(host, cmds)

    def cleanup_all(self):
        for host in self.host_list:
            print 'cleanup sysinfo collect process in {}'.format(host)
            p = Process(target=self.cleanup_sys_info,args=(host,))
            p.start()
            self.get_ceph_perfdump(host)

    def get_logfile(self, host, log, log_dir):
        t = paramiko.Transport(host, "22")
        t.connect(username = "root", password = "passw0rd")
        sftp = paramiko.SFTPClient.from_transport(t)
        remotepath = '/tmp/{}'.format(log)
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except Exception, e:
                print "make sysinfo log dir fail:{}".format(e)
                sys.exit(1)

        localpath = '{}/{}_{}'.format(log_dir, host, log)
        print host, remotepath, localpath
        sftp.get(remotepath, localpath)
        t.close()

    def get_all_logfile(self, host, log_dir):
        self.get_logfile(host, 'sar.log', log_dir)
        self.get_logfile(host, 'iostat.log', log_dir)
        self.get_logfile(host, 'ceph.log', log_dir)
        self.get_logfile(host, 'perfdump.log', log_dir)
        self.get_logfile(host, 'ceph_config.log', log_dir)

    def get_all_host_logfile(self, log_dir):
        self.cleanup_all()
        for host in self.host_list:
            print 'get sysinfo logs from {}'.format(host)
            p = Process(target=self.get_all_logfile,args=(host, log_dir))
            p.start()

    def get_ceph_perfdump(self, host):
        #cmds = ['while true; do find /var/run/ceph -name \'*osd*asok\' | while read path; do ceph --admin-daemon $path perf dump; done; sleep 1; done >/tmp/perfdump.log &']
        cmds = ['find /var/run/ceph -name \'*osd*asok\' | while read path; do ceph --admin-daemon $path perf dump; done >/tmp/perfdump.log']
        self.run_sshcmds(host, cmds)

    def cleanup_ceph_perf(self):
        for host in self.host_list:
            cmds = ['find /var/run/ceph -name \'*osd*asok\' | while read path; do ceph --admin-daemon $path perf reset all; done']
            self.run_sshcmds(host, cmds)

    def get_ceph_conf(self, host):
        cmds = ['find /var/run/ceph -name \'*osd*asok\' | while read path; do ceph --admin-daemon $path config show; done >/tmp/ceph_config.log']
        self.run_sshcmds(host, cmds)

    def deal_with_sysinfo_logfile(self, log_dir, ceph_info):
        self.deal_with_sarlog(log_dir, ceph_info)
        self.deal_with_iostatlog(log_dir, ceph_info)
        if self.havedb:
            self.db.close_db()

    def get_datetime_fordb_sarlog(self, time, t_type, casename):
        if t_type == 'PM':
            time_list = time.split(':')
            _time = '{}:{}:{}'.format(
                int(time_list[0]) + 12,
                time_list[1],
                time_list[2]
            )
        else:
            _time = time

        casename_list = casename.split('_')  #rbd_rw_4k_runtime30_iodepth1_numjob1_imagenum2_test2_%70_2017_07_27_17_47_33
        result_time = '{}-{}-{} {}'.format(
            casename_list[-6],
            casename_list[-5],
            casename_list[-4],
            _time
        )
        return result_time

    def deal_with_sarlog_cpu(self, host, casename):
        #%usr     %nice      %sys   %iowait    %steal      %irq     %soft    %guest    %gnice     %idle
        cpu_result = []
        cmd = 'grep "CPU      %usr" -A 1 {}_sar.log | grep all'.format(host)
        cpu_data_list = subprocess.check_output(cmd, shell=True).split('\n')
        del cpu_data_list[-1]
        for cpu_data in cpu_data_list:
            result = {}
            cpu_data = re.sub(r'\s+', ",", cpu_data)
            cpu_data = cpu_data.split(',')
            result['time'] = self.get_datetime_fordb_sarlog(cpu_data[0], cpu_data[1], casename)
            result['usr'] = cpu_data[3]
            result['nice'] = cpu_data[4]
            result['sys'] = cpu_data[5]
            result['iowait'] = cpu_data[6]
            result['steal'] = cpu_data[7]
            result['irq'] = cpu_data[8]
            result['soft'] = cpu_data[9]
            result['guest'] = cpu_data[10]
            result['gnice'] = cpu_data[11]
            result['idle'] = cpu_data[12]
            cpu_result.append(result)
            if self.havedb:
                self.db.insert_tb_sarcpudata(casename, host, **result)
        return cpu_result

    def deal_with_sarlog_memory(self, host, casename):
        #kbmemfree kbmemused  %memused kbbuffers  kbcached  kbcommit   %commit  kbactive   kbinact   kbdirty
        mem_result = []
        with open('{}_sar.log'.format(host), 'r') as f:
            lines = f.readlines()
            mem_data_list = []
            for n in range(len(lines)):
                if re.search('kbmemfree kbmemused', lines[n]):
                    mem_data_list.append(lines[n+1].strip())
        for mem_data in mem_data_list:
            result = {}
            mem_data = re.sub(r'\s+', ",", mem_data)
            data = mem_data.split(',')
            result['time'] = self.get_datetime_fordb_sarlog(data[0], data[1], casename)
            result['kbmemfree'] = data[2]
            result['kbmemused'] = data[3]
            result['memused'] = data[4]
            result['kbbuffers'] = data[5]
            result['kbcached'] = data[6]
            result['kbcommit'] = data[7]
            result['commit'] = data[8]
            result['kbactive'] = data[9]
            result['kbinact'] = data[10]
            result['kbdirty'] = data[11]
            mem_result.append(result)
            if self.havedb:
                self.db.insert_tb_sarmemdata(casename, host, **result)
        return mem_result

    def get_network_device(self, host, ceph_info):
        with open(ceph_info, "r") as f:
            ceph_info = yaml.load(f)
        network = ceph_info['ceph-network']

        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(hostname=host, port=22, username='root', password='passw0rd')
        stdin, stdout, stderr = ssh.exec_command(
            'ifconfig | grep "inet " -B 1')
        result = stdout.read()
        ssh.close()

        results = result.split('--')
        for result in results:
            result = re.sub('\n', '', result)
            match = re.match('(\S+):.*inet (\S+) ', result)
            ip = match.group(2)
            if ip_in_subnet(ip, network['public_network']):
                public_n = match.group(1)
            elif ip_in_subnet(ip, network['cluster_network']):
                cluster_n = match.group(1)

        return cluster_n, public_n

    def deal_with_sarlog_nic(self, host, casename, ceph_info):
        #rxpck/s   txpck/s    rxkB/s    txkB/s   rxcmp/s   txcmp/s  rxmcst/s
        cluster_n, public_n = self.get_network_device(host, ceph_info)
        with open('{}_sar.log'.format(host), 'r') as f:
            lines = f.readlines()
            nic_data_list = []
            for n in range(len(lines)):
                if re.search(r'rxpck\/s   txpck\/s', lines[n]):
                    i = 1
                    while lines[n+i] != '\n':
                        nic_data_list.append(lines[n+i].strip())
                        i = i+1
        both_result = {}
        cluster_result = []
        public_result = []
        for nic_data in nic_data_list:
            result = {}
            nic_data = re.sub(r'\s+', ",", nic_data)
            data = nic_data.split(',')
            if data[2] == cluster_n:
                result['time'] = self.get_datetime_fordb_sarlog(data[0], data[1], casename)
                result['rxpcks'] = data[3]
                result['txpcks'] = data[4]
                result['rxkBs'] = data[5]
                result['txkBs'] = data[6]
                result['rxcmps'] = data[7]
                result['txcmps'] = data[8]
                result['rxmcsts'] = data[9]
                cluster_result.append(result)
                if self.havedb:
                    self.db.insert_tb_sarnicdata(
                        casename,
                        host,
                        'cluster:{}'.format(cluster_n),
                        **result
                    )
            elif data[2] == public_n:
                result['time'] = self.get_datetime_fordb_sarlog(data[0], data[1], casename)
                result['rxpcks'] = data[3]
                result['txpcks'] = data[4]
                result['rxkBs'] = data[5]
                result['txkBs'] = data[6]
                result['rxcmps'] = data[7]
                result['txcmps'] = data[8]
                result['rxmcsts'] = data[9]
                public_result.append(result)
                if self.havedb:
                    self.db.insert_tb_sarnicdata(
                        casename,
                        host,
                        'public:{}'.format(public_n),
                        **result
                    )
        both_result['cluster_network:{}'.format(cluster_n)] = cluster_result
        both_result['public_network:{}'.format(public_n)] = public_result

        return both_result

    def deal_with_sarlog(self, log_dir, ceph_info):
        org_dir = os.getcwd()
        os.chdir(log_dir)
        dir_list = os.getcwd().split('/')
        casename = re.match('sysinfo_(.*)', dir_list[-1]).group(1)

        all_result = {}
        for host in self.host_list:
            all_result[host] = self.deal_with_sarlog_cpu(host, casename)
        json.dump(all_result, open('./sar_cpu.json', 'w'), indent=2)

        for host in self.host_list:
            all_result[host] = self.deal_with_sarlog_memory(host, casename)
        json.dump(all_result, open('./sar_memory.json', 'w'), indent=2)

        for host in self.host_list:
            all_result[host] = self.deal_with_sarlog_nic(host, casename, ceph_info)
        json.dump(all_result, open('./sar_nic.json', 'w'), indent=2)

        os.chdir(org_dir)

    def get_datetime_fordb_iostatlog(self, casename, time, n):
        time_match = re.match('(.*):(.*):(.*)', time)
        sec = int(time_match.group(3)) + n
        if sec > 59:
            minu = int(time_match.group(2)) + 1
            if minu == 60:
                hour = int(time_match.group(1)) + 1
                if hour == 24:
                    _time = '00:00:{:0>2}'.format(sec%60)
                else:
                    _time = '{}:00:{:0>2}'.format(hour, sec%60)
            else:
                _time = '{}:{}:{:0>2}'.format(time_match.group(1), minu, sec%60)
        else:
            _time = _time = '{}:{}:{:0>2}'.format(time_match.group(1), time_match.group(2), sec)

        casename_list = casename.split('_')

        result_time = '{}-{}-{} {}'.format(
            casename_list[-6],
            casename_list[-5],
            casename_list[-4],
            _time
        )
 
        return result_time

    def deal_with_iostatlog(self, log_dir, ceph_info):
        #rrqm/s   wrqm/s     r/s     w/s    rMB/s    wMB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util
        with open(ceph_info, "r") as f:
            ceph_info = yaml.load(f)
        nodes = ceph_info['ceph-node']

        org_dir = os.getcwd()
        os.chdir(log_dir)
        dir_list = os.getcwd().split('/')
        casename = re.match('sysinfo_(.*)', dir_list[-1]).group(1)

        all_result = {}
        for host in self.host_list:
            osd_result = {}

            with open('{}_iostat.log'.format(host)) as f:
                time = f.readline()
            osd_result['start_time'] = re.search(' (\S*:.*:\S*) ', time).group(1)

            for osd_num,osd in nodes[host].items():
                oj_result = {}
                for disk_name,disk in osd.items():
                    osd_disk = re.match('/dev/(.*)', disk).group(1)
                    disk_result = []
                    cmd = 'grep "{}" {}_iostat.log'.format(osd_disk, host)
                    disk_data_list = subprocess.check_output(cmd, shell=True).split('\n')
                    del disk_data_list[0]
                    del disk_data_list[-1]
                    n = 0
                    for disk_data in disk_data_list:
                        result = {}
                        disk_data = re.sub(r'\s+', ",", disk_data)
                        data = disk_data.split(',')
                        result['time'] = self.get_datetime_fordb_iostatlog(casename, osd_result['start_time'], n)
                        result['rrqms'] = data[1]
                        result['wrqms'] = data[2]
                        result['rs'] = data[3]
                        result['ws'] = data[4]
                        result['rMBs'] = data[5]
                        result['wMBs'] = data[6]
                        result['avgrqsz'] = data[7]
                        result['avgqusz'] = data[8]
                        result['await'] = data[9]
                        result['r_await'] = data[10]
                        result['w_await'] = data[10]
                        result['svctm'] = data[10]
                        result['util'] = data[10]
                        disk_result.append(result)
                        if self.havedb:
                            self.db.insert_tb_iostatdata(casename, host, osd_num, disk_name, **result)
                        n = n + 1
                    oj_result[disk_name] = disk_result
                osd_result[osd_num] = oj_result
            all_result[host] = osd_result
        json.dump(all_result, open('./iostat.json', 'w'), indent=2)
        os.chdir(org_dir)

    def deal_with_perfdumplog(self, log_dir):
        os.chdir(log_dir)
        for host in self.host_list:
            with open('{}_perfdump_.log'.format(host)) as f:
                load_dict = json.load(f)
                print load_dict



def format_subnet(subnet_input):  
    if subnet_input.find("/") == -1:  
        return subnet_input + "/255.255.255.255"  
  
    else:  
        subnet = subnet_input.split("/")  
        if len(subnet[1]) < 3:  
            mask_num = int(subnet[1])  
            last_mask_num = mask_num % 8  
            last_mask_str = ""  
            for i in range(last_mask_num):  
                last_mask_str += "1"  
            if len(last_mask_str) < 8:  
                for i in range(8-len(last_mask_str)):  
                    last_mask_str += "0"  
            last_mask_str = str(int(last_mask_str,2))  
            if mask_num / 8 == 0:  
                subnet = subnet[0] + "/" + last_mask_str +"0.0.0"  
            elif mask_num / 8 == 1:  
                subnet = subnet[0] + "/255." + last_mask_str +".0.0"  
            elif mask_num / 8 == 2 :  
                subnet = subnet[0] + "/255.255." + last_mask_str +".0"  
            elif mask_num / 8 == 3:  
                subnet = subnet[0] + "/255.255.255." + last_mask_str  
            elif mask_num / 8 == 4:  
                subnet = subnet[0] + "/255.255.255.255"  
            subnet_input = subnet  
  
        subnet_array = subnet_input.split("/")  
        subnet_true = socket.inet_ntoa( 
            struct.pack(
                "!I",
                struct.unpack(
                    "!I", 
                    socket.inet_aton(subnet_array[0])
                )[0] & struct.unpack(
                    "!I",
                    socket.inet_aton(subnet_array[1])
                )[0]
            )
        ) + "/" + subnet_array[1]  
        return subnet_true 

def ip_in_subnet(ip,subnet):  
    subnet = format_subnet(str(subnet))  
    subnet_array = subnet.split("/")  
    ip = format_subnet(ip + "/" + subnet_array[1])  
    return ip == subnet 



def main():
    parser = argparse.ArgumentParser(
        prog="sysinfo",
        version='v0.1',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="collect systen info")
    parser.add_argument('-D', '--logdir', dest="logdir",
                metavar="sysinfo log dir", action="store",
                    help='''sysinfo log dir''')
    args = parser.parse_args()

    sysinfo = SysInfo()
    '''
    #sysinfo.get_sys_info()
    #sysinfo.cleanup_all()
    sysinfo.deal_with_sysinfo_logfile(
        sysinfo_dir,
        '{}/../../../ceph_hw_info.yml'.format(os.getcwd())
    )
    '''
    sysinfo.deal_with_perfdumplog('/root/fio-zelin/test-suites/test2/log_2017_07_28_15_00_39/sysinfo_rbd_rw_4k_runtime30_iodepth1_numjob1_imagenum2_test2_%70_2017_07_28_15_00_39')

if __name__ == '__main__':
    main()
