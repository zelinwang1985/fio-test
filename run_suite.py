import os
import sys
import argparse
import datetime
import shutil
import subprocess
import re
import time
import platform
import paramiko
import json
import yaml

from result import Result
from collect_system_status import SysInfo

class RunFIO(object):

    def __init__(self, path, todb=False):
        os.chdir(path)
        with open('fioserver_list.conf', 'r') as f:
            clients = f.readlines()
            self.sysinfo = SysInfo(clients[0], havedb=todb)

        self.hwinfo_file = '{}/../../ceph_hw_info.yml'.format(os.getcwd())
        with open(self.hwinfo_file, 'r') as f:
            ceph_info = yaml.load(f)
        self.nodes = ceph_info['ceph-node']
 

    def checkandstart_fioser(self, path, suitename):
        with open('{}/fioserver_list.conf'.format(path, suitename), 'r') as f:
            for client in f:
                client = client.strip()
                output =''
                while output == '':
                    ssh = paramiko.SSHClient()
                    ssh.load_system_host_keys()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    
                    ssh.connect(hostname=client, port=22, username='root', password='passw0rd')
                    cmd = 'ps -ef | grep fio | grep server | grep -v grep'
                    stdin, stdout, stderr = ssh.exec_command(cmd)
                    output = stdout.readlines()
                    if output == []:
                        print "================={} without fio server".format(client)
                        cmd = 'nohup fio --server &'
                        ssh.exec_command(cmd)
                        output = ''
                    elif len(output) > 1:
                        print "Error: Found more than one fio server in {}: {}".format(client, output)
                        sys.exit(1)
                    else:
                        match = re.match('\S+\s+(\d+)', output[0])
                        platform_type = platform.platform()
                        if re.search('ubuntu', platform_type, re.I):
                            process_id = match.group(1)
                        elif re.search('centos', platform_type, re.I):
                            process_id = match.group(1)
                        else:
                            print "unsupport system os {}".format(platform_type)
                            sys.exit(0)
         
                        print "process_id: {}".format(process_id)
                    ssh.close()
    
    def create_log_dir(self, path, ceph_config):
        config = ''
        for key, value in ceph_config.items():
            value = re.sub('\/', '', value)
            key = re.sub('_', '', key)
            config = config + key + value + '_'
        
        log_dir = '{}/log_{}{}'.format(
            path,
            config,
            time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
        )
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except Exception, e:
                print "make log dir fail:{}".format(e)
                sys.exit(1)
        return log_dir
    
    def run(self, path, ceph_config={}):
        org_ceph_config = self.modify_ceph_config(ceph_config)
        print org_ceph_config
        log_dir = self.create_log_dir(path, ceph_config)
        configs = os.listdir('{}/config/'.format(path))
        with open('fioserver_list.conf', 'r') as f:
            clients = f.readlines()
            num_clients = len(clients)
            i = 0
            while (i < len(configs)):
                match_config = re.match(r'(.*)_0\.config', configs[i])
                if match_config:
                    cmd = ['fio']
                    n = 0
                    for client in clients:
                        config = '{}_{}.config'.format(match_config.group(1), n)
                        if configs.count(config) == 0:
                            print "can't find {} in {}/config/!".format(config, path)
                            sys.exit(1)
                        cmd = cmd + ['--client', client.strip(), '{}/config/{}'.format(path, config)]
                        n = n + 1
                    i = i + 1
                    log_file_name = '{}_{}'.format(
                        match_config.group(1),
                        time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
                    )
                    log_file = '{}/{}.log'.format(
                        log_dir,
                        log_file_name
                    )
                    print cmd
                    self.sysinfo.cleanup_ceph_perf()
                    child = subprocess.Popen(
                        cmd,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE)
                    self.sysinfo.get_sys_info()
                    with open(log_file, 'wt') as handle:
                        while True:
                            line = child.stdout.readline()
                            if not line:
                                break
                            print line
                            handle.write(line)
                    time.sleep(1)
                    self.sysinfo.get_all_host_logfile('{}/sysinfo_{}'.format(log_dir, log_file_name))
                else:
                    i = i + 1
        self.reset_ceph_config(org_ceph_config)
        return log_dir
    
    def gen_result(self, log_dir, todb=False):
        print log_dir
        log_dir_list = log_dir.split('/')
        match = re.match(r'log_(.*)', log_dir_list[-1])
        timetag = match.group(1)
        result = Result(havedb=todb)
        output_file = result.deal_with_fio_data(
            log_dir_list[-2],
            timetag,
            './result_{}'.format(timetag)
        )
        print "============================="
        print output_file
        print "============================="
    
        try:
            sysinfo_dir_list = subprocess.check_output(
                'ls {} | grep sysinfo'.format(log_dir),
                shell=True).split('\n')
        except Exception, e:
            print e
            sys.exit(0)
        else:
            del sysinfo_dir_list[-1]
            for sysinfo_dir in sysinfo_dir_list:
                self.sysinfo.deal_with_sysinfo_logfile(
                    sysinfo_dir,
                    self.hwinfo_file
                )
            self.sysinfo.close_db()
    
    def update_ceph_conffile(self, host, ceph_config):
        t = paramiko.Transport(host, "22")
        t.connect(username = "root", password = "passw0rd")
        sftp = paramiko.SFTPClient.from_transport(t)
        remotepath = '/etc/ceph/ceph.conf'
        sftp.get(remotepath, './ceph.conf.org')
        with open('./ceph.conf', 'w') as output_f:
            with open('./ceph.conf.org', 'r') as input_f:
                for ceph_key, ceph_value in ceph_config.items():
                    for line in input_f.readlines():
                        if re.match('\[osd\.\d+\]', line):
                            output_f.write(line)
                            output_f.write('    {} = {}\n'.format(ceph_key,
             ceph_value))
                        else:
                            output_f.write(line)
            
        sftp.put('./ceph.conf', remotepath)
        sftp.put('./ceph.conf.org', '/etc/ceph/ceph.conf.org')
        t.close()
    
    
    def modify_ceph_config(self, ceph_config):
        org_all_config = {}
        for host in self.sysinfo.host_list:
            org_host_config = {}
            #timetag = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
            ssh.connect(
                hostname = self.nodes[host]['public_ip'],
                port = 22,
                username = 'root',
                password = 'passw0rd'
            )
            cmd = 'find /var/run/ceph -name \'*osd*asok\''
            stdin, stdout, stderr = ssh.exec_command(cmd)
            osd_list = stdout.readlines()
            for osd in osd_list:
                org_osd_config = {}
                osd = osd.strip()
                for ceph_key, ceph_value in ceph_config.items():
                    cmd = 'ceph --admin-daemon {} config show | grep {}'.format(osd, ceph_key)
                    stdin, stdout, stderr = ssh.exec_command(cmd)
                    output = stdout.readlines()
                    if len(output) < 1:
                        print "Error: Can't find {} in ceph conf!".format(ceph_key)
                        sys.exit(1)
                    elif len(output) > 1:
                        print "Error: find {} in ceph conf fail:{}".format(ceph_key, output)
                        sys.exit(1)
                    else:
                        cephkey_match = re.search('".*": "(.*)",', output[0])
                        org_osd_config[ceph_key] = cephkey_match.group(1)
                    cmd = 'ceph --admin-daemon {} config set {} "{}"'.format(osd, ceph_key, ceph_value)
                    ssh.exec_command(cmd)
                org_host_config[osd] = org_osd_config
            org_all_config[host] = org_host_config
            ssh.close()
        #update_ceph_conffile(self.nodes[host][public_ip], ceph_config)
        return org_all_config
    
    def reset_ceph_config(self, org_all_config):
        for host, host_config in org_all_config.items():
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
            ssh.connect(
                hostname = self.nodes[host]['public_ip'],
                port = 22,
                username = 'root',
                password = 'passw0rd'
            )
            for osd, osd_config in host_config.items():
                for cephkey, value in osd_config.items():
                    value = re.sub(r'\\', '', value)
                    cmd = 'ceph --admin-daemon {} config set {} "{}"'.format(osd, cephkey, value)
                    print cmd
                    ssh.exec_command(cmd)
            ssh.close()


def main():
    parser = argparse.ArgumentParser(
        prog="build_suite",
        version='v0.1',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Run fio")
    parser.add_argument('-N', '--suitename', dest="suitename",
                metavar="test suite name", action="store",
                    help='''test suite name''')
    parser.add_argument('-l', '--listsuite', dest="listsuite", default=False,
                action="store_true", help='''list all test suite''')
    parser.add_argument('-b', '--inserttodb', dest="todb", default=False,
                action="store_true", help='''insert data to db''')
    args = parser.parse_args()

    if args.listsuite:
        tests = os.listdir('{}/test-suites/'.format(os.getcwd()))
        if args.suitename == None:
            for test in tests:
                print test
        else:
            for test in tests:
                if test == args.suitename:
                    try:
                        os.system(
                            'cd {}/test-suites/{}/config/; ls *config'.format(os.getcwd(), test))
                    except Exception, e:
                        print e
                        sys.exit(1)
        sys.exit(0)

    path = "{}/test-suites/{}".format(os.getcwd(), args.suitename)
    runfio = RunFIO(path, todb=args.todb)
    runfio.checkandstart_fioser(path, args.suitename)

    ceph_config_file = './setup_ceph_config.json'
    if os.path.exists(ceph_config_file): 
        ceph_configs = json.load(open(ceph_config_file))
        for ceph_config in ceph_configs:
            log_dir = runfio.run(path, ceph_config=ceph_config)
            time.sleep(2)
            runfio.gen_result(log_dir, todb=args.todb)
    else:
        log_dir = runfio.run(path)
        time.sleep(2)
        runfio.gen_result(log_dir, todb=args.todb)



if __name__ == '__main__':
    main()
