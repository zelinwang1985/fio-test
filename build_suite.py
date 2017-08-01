import os
import sys
import argparse
import datetime
import shutil
import subprocess
import re
import json
import copy


class FIOTest(object):
  def __init__(self):
    self.rw = [
        'rw',
        'randrw'
    ]
    self.bs = [
        '4k',
        '8k',
        '16k',
        '32k',
        '64k',
        '128k',
        '256k',
        '512k',
        '1024k',
        '2048k',
        '4MB',
        '8MB',
        '16MB',
        '32MB',
        '64MB',
        '128MB'
    ]
    self.iodepth = [
        1,
        4,
        8,
        16,
        32,
        64,
        128,
        256,
        512,
        1024,
    ]
    self.numjob = [
        1,
        4,
        8,
        16,
        32
    ]


def create_suite_dir(suitename):
    path = "{}/test-suites/{}/config".format(os.getcwd(), suitename)
    print "=================================="
    print "test suite dir is: {}/test-suites/{}".format(os.getcwd(), suitename)
    print "=================================="
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
        except Exception, e:
            print "remove the previous test suite dir fail:{}".format(e)
            sys.exit(1)
    try:
        os.makedirs(path)
    except Exception, e:
        print "make test suite dir fail:{}".format(e)
        sys.exit(1)
    return "{}/test-suites/{}".format(os.getcwd(), suitename)

def getlist(data):
    result = data.split(',')
    if result[-1] == '':
        del result[-1]
    return result

def CheckIPAddr(IP):
    if not re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', IP):
      return 1
    nums = IP.split('.')
    for num in nums:
        if ( int(num) > 255 or int(num) < 0 ):
            return 1
    return 0

def generate_run_config(path):
    with open('{}/run_config'.format(path), 'aw') as f:
        configs = os.listdir('{}/config/'.format(path))
        for config in configs:
            f.write(config)
            f.write('\n')

def case(pool, rw, bs, runtime, iodepth, numjobs, image_num, case_num, rwmixread, imagename, clientslists):
    for i in range(len(clientslists)):
        config_para = pool+'_'+rw+'_'+bs+'_runtime'+runtime+'_iodepth'+iodepth+'_numjob'+numjobs+'_imagenum'+image_num+'_'+case_num+'_%'+rwmixread+'_'+str(i)
        config_filename = config_para+'.config'
        with open('./config/{}'.format(config_filename), 'aw') as f:
            f.write("[global]\n")
            f.write("ioengine=rbd\n")
            f.write("clientname=admin\n")
            f.write("pool={}\n".format(pool))
            f.write("rw={}\n".format(rw))
            f.write("bs={}\n".format(bs))
            f.write("runtime={}\n".format(runtime))
            f.write("iodepth={}\n".format(iodepth))
            f.write("numjobs={}\n".format(numjobs))
            f.write("direct=1\n")
            f.write("rwmixread={}\n".format(rwmixread))
            f.write("new_group\n")
            f.write("group_reporting\n")
            # $image_start $image_end: Different fio server run in different image
            image_start = i*int(image_num)
            image_end = image_start + int(image_num)
            for n in range(image_start, image_end):
                f.write("[rbd_image{}]\n".format(n))
                f.write("rbdname={}_{}\n".format(imagename, n))

def gen_setup_ceph_config(cephconfig):
    if cephconfig != 'default':
        result_ceph_configs = []
        cephconfig_list = cephconfig.split(',')
        for raw_ceph_config in cephconfig_list:
            match = re.search('\[(\d+)-(\d+)\]', raw_ceph_config)

            result_ceph_config = {}
            ceph_config_list = raw_ceph_config.split(':')
            n = 0

            if match:
                range_ceph_configs = []
                range_dic = {}
                normal_dic = {}
                while n < len(ceph_config_list) - 1:
                    n = n + 1
                    match_range = re.match('\[(\d+)-(\d+)\]', ceph_config_list[n])
                    if match_range:
                        range_dic[ceph_config_list[n-1]] = ceph_config_list[n]
                    else:
                        normal_dic[ceph_config_list[n-1]] = ceph_config_list[n]
                    n = n + 1
                range_ceph_configs.append(normal_dic)
                while len(range_dic) > 0:
                    key, value = range_dic.popitem()
                    range_match = re.match('\[(\d+)-(\d+)\]', value)
                    _range_ceph_configs = []
                    for org_ceph_config in range_ceph_configs:
                        for range_num in range(int(range_match.group(1)), int(range_match.group(2))+1):
                            org_dic = copy.deepcopy(org_ceph_config)
                            org_dic[key] = range_num
                            _range_ceph_configs.append(org_dic)
                    range_ceph_configs = _range_ceph_configs
                result_ceph_configs = result_ceph_configs + range_ceph_configs
            else:
                while n < len(ceph_config_list):
                    result_ceph_config[ceph_config_list[n]] = ceph_config_list[n+1]
                    n = n + 2
                result_ceph_configs.append(result_ceph_config)
        json.dump(result_ceph_configs, open('./setup_ceph_config.json', 'w'), indent=2)

        return result_ceph_configs

def main():
    parser = argparse.ArgumentParser(
        prog="build_suite",
        version='v0.1',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Run fio")
    parser.add_argument('-C', '--clientslist', dest="clientslist",
                metavar="ceph client list ip address", action="store",
                    help='''ceph client list ip address''')
    parser.add_argument('--readwritetype', dest="readwritetype",
                metavar="fio read and write type", action="store",
                    help='''fio read and write type''')
    parser.add_argument('--blocksize', dest="blocksize",
                metavar="fio block size", action="store",
                    help='''fio block size''')
    parser.add_argument('--runtime', dest="runtime",
                metavar="fio run time", action="store",
                    help='''fio run time''')
    parser.add_argument('--iodepth', dest="iodepth",
                metavar="fio io depth", action="store",
                    help='''fio io depth''')
    parser.add_argument('--numjob', dest="numjob",
                metavar="fio num job", action="store",
                    help='''fio numjob''')
    parser.add_argument('--imagecount', dest="imagecount",
                metavar="ceph image count", action="store",
                    help='''ceph image count''')
    parser.add_argument('--imagename', dest="imagename",
                metavar="ceph image name", action="store",
                    help='''ceph image count''')
    parser.add_argument('--rwmixread', dest="rwmixread",
                metavar="fio rwmixread", action="store",
                    help='''fio rwmixread''')
    parser.add_argument('--pool', dest="pool",
                metavar="ceph pool name", action="store",
                    help='''ceph pool name''')
    parser.add_argument('--cephconfig', dest="cephconfig",
                metavar="setup ceph config", action="store",
                    help='''ceph pool name''')
    parser.add_argument('-N', '--suitename', dest="suitename",
                metavar="test suite name", action="store",
                    help='''test suite name''')
    args = parser.parse_args()
        

    blocksizes = getlist(args.blocksize)
    iodepths = getlist(args.iodepth)
    numjobs = getlist(args.numjob)
    readwritetypes = getlist(args.readwritetype)
    rwmixreads = getlist(args.rwmixread)
    imagecounts = getlist(args.imagecount)

    path = create_suite_dir(args.suitename)

    fio_test = FIOTest()
    current_date = str(datetime.datetime.now())
    os.chdir(path)

    if args.clientslist:
        clientslists = getlist(args.clientslist)
        with open('fioserver_list.conf', 'w') as f:
            for client in clientslists:
                f.write(client)
                f.write('\n')

    ceph_config = gen_setup_ceph_config(args.cephconfig)
    
    print "readwritetypes are {}".format(readwritetypes)
    print "blocksizes are {}".format(blocksizes)
    print "iodepths are ".format(iodepths)
    print "numjobs are {}".format(numjobs)
    print "imagecounts are {}".format(imagecounts)
    print "rwmixreads are {}".format(rwmixreads)
    print "clients are {}".format(clientslists)
    print "pool is {}".format(args.pool)
    print "runtime is {}".format(args.runtime)
    print "imagename is {}".format(args.imagename)
    print "ceph config will be modified as: {}".format(ceph_config)

    for readwritetype in readwritetypes:
        for blocksize in blocksizes:
            for iodepth in iodepths:
                for numjob in numjobs:
                    for imagecount in imagecounts:
                        for rwmixread in rwmixreads:
                            case(
                                args.pool,
                                fio_test.rw[int(readwritetype)-1],
                                fio_test.bs[int(blocksize)-1],
                                args.runtime,
                                str(fio_test.iodepth[int(iodepth)-1]),
                                str(fio_test.numjob[int(numjob)-1]),
                                imagecount,
                                args.suitename,
                                rwmixread,
                                args.imagename,
                                clientslists
                            )
    #generate_run_config(path)


if __name__ == '__main__':
    main()
