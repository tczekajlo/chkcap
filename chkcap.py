#!/usr/bin/python

from keystoneclient.auth.identity import v2 as identity
from keystoneclient import session
from novaclient import client

from texttable import Texttable

import argparse
import os


CREDS = {
        'auth_url': os.getenv('OS_AUTH_URL', 'http://localhost:5000/v2.0'),
        'username': os.getenv('OS_USERNAME', 'admin'),
        'password': os.getenv('OS_PASSWORD','pass'),
        'tenant_name': os.getenv('OS_TENANT_NAME', 'admin')
        }

args=None
__version__ = "0.0.1"

class chkcap():
    def __init__(self):
        sauth = identity.Password(**CREDS)
        ssession = session.Session(auth=sauth)

        #Nova
        self.nova = client.Client(2, session=ssession)

    def hosts(self,aggregate=None):
        if aggregate != None:
            return self.nova.aggregates.find(name=aggregate).hosts
        else:
            return [hv.hypervisor_hostname for hv in self.nova.hypervisors.list()]

    def hypervisors_list(self):
        hv_list = {}
        for hv in self.hosts(args.aggregate):
            host = self.nova.hypervisors.find(hypervisor_hostname=hv)
            hv_list[host.hypervisor_hostname]={
                    'id': host.id,
                    'memory_mb': host.memory_mb,
                    'memory_mb_used': host.memory_mb_used,
                    'vcpus': host.vcpus,
                    'vcpus_used': host.vcpus_used,
                    'free_disk_gb': host.free_disk_gb,
                    'running_vms': host.running_vms
                    }
        return hv_list

    def cap_count(self,flavor_name):
        result = {}
        hv_list = self.hypervisors_list()

        for flavor_name in flavor_name.split(','):
            flavor = self.nova.flavors.find(name=flavor_name)

            memory= int(flavor.ram)
            disk = int(flavor.disk) + int(flavor.swap or 0)
            vcpus = int(flavor.vcpus)

            for host, v in hv_list.items():
                vm_count=0
                free_memory = int(v['memory_mb']) - int(v['memory_mb_used'])
                free_vcpus = (int(v['vcpus']) * args.cpu_overcommit) - int(v['vcpus_used'])
                free_disk = int(v['free_disk_gb'])

                while True:
                    if (free_disk < disk or free_vcpus < vcpus or free_memory < memory):
                        break
                    vm_count += 1
                    free_memory -= memory
                    free_vcpus -= vcpus
                    free_disk -= disk
                
                if result.has_key(host):
                    result[host][flavor.name]=vm_count
                else:
                    result={host:{flavor.name:vm_count}}

        return [result, hv_list]

def parse_args():
    global args 

    parser = argparse.ArgumentParser(description="chkcap is a tool to check how \
            many VMs could be spawned for given flavor in Openstack environment.", 
            version="%(prog)s " + __version__)
    parser.add_argument('-f', '--flavor', help='Name of flavor.', required=True)
    parser.add_argument('-c', '--cpu-overcommit', help='CPU overcommit fraction. \
            Default value is 16.', default=16, type=int)
    parser.add_argument('-a', '--aggregate', help='Name of aggregate. Hosts from \
            given aggregate are taking into account.')

    args = parser.parse_args()
    
if __name__ == "__main__":
    parse_args()
    c = chkcap()
    table = Texttable()
    perdict_vms = c.cap_count(args.flavor)

    table.set_deco(Texttable.HEADER | Texttable.VLINES)
    table.set_cols_align(['r' for x in range(len(args.flavor.split(','))+3)])

    header=['Hostname','Aggregate','Running VMs']
    for flavor in sorted(args.flavor.split(',')):
        header.append(flavor)

    print_table = [header]
    sum_vm = {}

    for host, v in perdict_vms[1].items():
        row = [host,args.aggregate,v['running_vms']]
        for vm, vms_amount in sorted(perdict_vms[0][host].items()):
            row.append(vms_amount)
        print_table.append(row)

    #summary
    vms_sum = [array[2:] for array in print_table[1:]]
    vms_sum = map(sum,zip(*vms_sum))
    vms_sum[0:0] = ['Summary','']
    print_table.append(vms_sum)

    #print table
    table.add_rows(print_table)
    print table.draw()
