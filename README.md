# chkcap
Script to check how many VMs could be spawned for given flavor in Openstack environment.

##Usage
```
usage: chkcap.py [-h] [-v] -f FLAVOR [-c CPU_OVERCOMMIT] [-a AGGREGATE]

chkcap is a tool to check how many VMs could be spawned for given flavor in
Openstack environment.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -f FLAVOR, --flavor FLAVOR
                        Name of flavor.
  -c CPU_OVERCOMMIT, --cpu-overcommit CPU_OVERCOMMIT
                        CPU overcommit fraction. Default value is 16.
  -a AGGREGATE, --aggregate AGGREGATE
                        Name of aggregate. Hosts from given aggregate are take
                        into account.
```

```
root@devstack0:~/chcap# ./chkcap.py -f m1.nano,m1.micro
Hostname  | Aggregate | Running VMs | m1.micro | m1.nano
==========+===========+=============+==========+========
devstack0 |      None |           2 |        6 |      12
devstack1 |      None |           2 |        3 |      22
devstack2 |      None |           3 |        2 |      15
devstack3 |      None |           1 |        4 |      10
devstack4 |      None |           1 |        6 |      13
devstack5 |      None |           3 |        5 |      18
devstack6 |      None |           5 |        6 |      12
  Summary |           |          17 |       32 |     102
```
On example above we can see that on devstack0 hypervisor is currently running 2 VMs and additionally we could spawn 6 instances using m1.micro flavor or 12 using m1.nano.
