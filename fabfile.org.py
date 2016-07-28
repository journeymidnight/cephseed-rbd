from fabric.api import *
from fabric.contrib.files import append
import time
import os

#diskprofile#

#monhostnames#

#osdhostnames#

def push_key(key_file='/root/.ssh/id_rsa.pub'):
    key_text = read_key_file(key_file)
    run('chattr -i /root/.ssh/authorized_keys')
    append('/root/.ssh/authorized_keys', key_text);

def read_key_file(key_file):
    key_file = os.path.expanduser(key_file)
    if not key_file.endswith('pub'):
        raise RuntimeWarning('Trying to push non-public part of key pair')
    with open(key_file) as f:
        return f.read()

def updateRepoAddress():
    put('./deployFile/resolv.conf','/etc/resolv.conf')
    run('rm /etc/yum.repos.d/letv-pkgs.repo /etc/yum.repos.d/CentOS.repo -f')
    put('./deployFile/CentOS-Base.repo','/etc/yum.repos.d/CentOS-Base.repo')
    put("./deployFile/ceph.repo","/etc/yum.repos.d/ceph.repo")
    put("./deployFile/watchtv.repo","/etc/yum.repos.d/watchtv.repo")

def testecho():
    run('rpm -qa|grep redhat-lsb-core || yum install redhat-lsb-core -y')
    run('echo hello')

def PurgeCeph():
    local('ceph-deploy purge %s' % env.host)
    local('ceph-deploy purgedata %s' % env.host)
    run('yum remove ceph ceph-common ceph-devel librados2 libcephfs1 python-ceph librbd1 ceph-test  libcephfs_jni1 libcephfs_jni1 libradosstriper1  librbd1 ceph-radosgw  ceph-libs-compat cephfs-java  libcephfs1 rbd-fuse rbd-fuse rest-bench -y')

def InstallCeph():
    run('yum install -y ceph ceph-osd')

def DeployOSDs():
    # in rbd case, sdb/sdc/sdd share /dev/sdg as journal disk, sde/sdf share /dev/sdh as journal disk
    run('/usr/sbin/ceph-disk zap /dev/sdg /dev/sdh') 
    local('ceph-deploy osd create --zap-disk %s:/dev/sdb:/dev/sdg %s:/dev/sdc:/dev/sdg %s:/dev/sdd:/dev/sdg %s:/dev/sde:/dev/sdh %s:/dev/sdf:/dev/sdh' % (env.host,env.host,env.host,env.host,env.host))
def prepareDisks():
    if diskprofile == "raid0":
        run('umount /dev/sd{b,b1,c,c1,d,d1,e,e1,f,f1,g,g1,h,h1}')
    elif diskprofile == "noraid":
        run('yum install -y lvm2')
        run('umount /dev/sd{b,c,d,e,f,g,h,i,j,k,l,m}')
        run('pvcreate /dev/sd{b,c,d,e,f,g,h,i,j,k,l,m}')
        run('vgcreate vg /dev/sd{b,c,d,e,f,g,h,i,j,k,l,m}')
        run('lvcreate -l200%PVS -n lv1 vg /dev/sdb /dev/sdc')
        run('lvcreate -l200%PVS -n lv2 vg /dev/sdd /dev/sde')
        run('lvcreate -l200%PVS -n lv3 vg /dev/sdf /dev/sdg')
        run('lvcreate -l200%PVS -n lv4 vg /dev/sdh /dev/sdi')
        run('lvcreate -l200%PVS -n lv5 vg /dev/sdj /dev/sdk')
        run('lvcreate -l200%PVS -n lv6 vg /dev/sdl /dev/sdm')
        run('/sbin/mkfs.xfs -i size=2048 -f /dev/vg/lv1')
        run('/sbin/mkfs.xfs -i size=2048 -f /dev/vg/lv2')
        run('/sbin/mkfs.xfs -i size=2048 -f /dev/vg/lv3')
        run('/sbin/mkfs.xfs -i size=2048 -f /dev/vg/lv4')
        run('/sbin/mkfs.xfs -i size=2048 -f /dev/vg/lv5')
        run('/sbin/mkfs.xfs -i size=2048 -f /dev/vg/lv6')

def CopyCephConf():
    put('./ceph.client.admin.keyring','/etc/ceph/ceph.client.admin.keyring')

def updatecephconf():
    run('echo "osd crush update on start = false" >> /etc/ceph/ceph.conf')

def updatentpconfig():
    put('./deployFile/ntpd', '/etc/sysconfig/ntpd')
    put('./deployFile/ntpd.service', '/etc/systemd/system/multi-user.target.wants/ntpd.service')

def updatefstab():
    run('sed -i "\/data\/slot/d" /etc/fstab')

def startdiamond():
    run('yum install diamond -y')
    put('./deployFile/diamond.conf', '/etc/diamond/diamond.conf')
    run('/etc/init.d/diamond start')
