# CephSeed-RBD

![](ceph-seed.jpg)


CephSeed-RBD是基于ceph-seed的而写的ceph部署项目，本项目的目的是：
1. 适配centos 7环境
2. 适配rbd对于共享journal的需求

包含以下两点功能：

1. 快速部署Ceph集群
2. 快速扩展OSD

## 注意事项
- 安装fabric和ceph-deploy。
- 提前配置ceph.repo (ceph.repo已经写到了deployFile/ceph.repo中，如repo有变动，请修改此文件)
**ceph.repo**:

```
[ceph]
name=Letv ceph
baseurl=http://s3s.lecloud.com/ceph-jewel/el7/update
enabled=1
gpgcheck=0
type=repo-md
priority=1
```

- 之后执行：
```
yum install fabric ceph-deploy -y
git pull http://git.letv.cn/wuxingyi/cephseed-rbd.git
```

## 利用 Ceph-Seed 快速部署Ceph集群
1. 配置到所有节点ssh登陆权限(即SSH白名单),如果没有配置到节点的服务器，那么需要在部署过程中手工输入节点的密码(如果服务器密码一致，只需输入一次).
2. 参考conf/nodeProfile.conf.example的格式，创建conf/nodeProfile.conf, 并填充area，mroom, storage，这三者是形成节点hostname的依据。 `注意：等于号之间不要有空格，文件尾部不要有空行`
3. 参考conf/monhosts.example、conf/osdhosts.example的格式，创建conf/monhosts和conf/osdhosts, 填充需要部署的monitor hosts和osd hosts。 `注意：一行一个IP，文件尾部不要有空行`
4. 执行：
```
sh deploy.sh [-D|--diskprofile] [raid0|noraid] [-N|--no-purge]
```
绝大部分场景下，使用sh deploy.sh -D raid0这个命令行进行部署即可。

5. 福利: 部署完成之后，会生成一个fabfile.py，这个文件已经配置了集群的一些环境，可以方便的增加其他函数来对集群进行运维操作。

### 参数说明
- -D|--diskprofile	
	- `必填参数`。如果磁盘做了RAID0，则参数为raid0;否则参数为noraid，磁盘会去做lvm。
- -N|--no-purge 	
	- 如果是干净环境，加上此参数，可不做purge data的操作

## 利用 Ceph-Seed 快速扩展OSD
1. 配置到所有节点ssh登陆权限(即SSH白名单),如果没有配置到节点的服务器，那么需要在部署过程中手工输入节点的密码(如果服务器密码一致，只需输入一次).
2. 填写conf目录下的area，mroom和storage。 `注意：等于号之间不要有空格，文件尾部不要有空行`
3. 执行:
```
sh expend-osd.sh [-c|--confserver] CONFSERVER [-s|--osdserver] OSDSERVER [-D|--diskprofile] [raid0|noraid] [-N|--no-purge] [-H|--hostname MONHOSTNAME]
```
绝大部分场景下，使用形如sh extend-osd.sh  -c 1.1.1.1 -s 1.1.1.2 -D raid0进行扩展即可。

4. 扩充节点后，为了便于后续管理新增加的节点，可以将此节点也添加到fabfile.py中。
5. 通常情况下, 新扩展的节点上的osd是不会新增到对应的host上的,因为在新扩展节点上防不胜防的被配置了“osd crush update on start = false”，为了让osd加入到这个host上，只需在ceph.conf
中删除此项配置，然后重启osd即可。在osd起来了之后，在把“osd crush update on start = false”这项配置重新添加上。

### 参数说明
- -c|--confserver CONFSERVER
	- `必填参数`。已有集群monitor服务器的ip。
- -s|--osdserver OSDSERVER
	- `必填参数`。要安装osd服务器的ip。
- -D|--diskprofile [raid0|noraid]
	- `必填参数`。如果磁盘做了RAID0，则参数为raid0;否则参数为noraid，磁盘会去做lvm。
- -N|--no-purge         
	- 如果是干净环境，加上此参数，可不做purge data的操作
- -H|--hostname MONHOSTNAME
	- 如果已有集群monitor服务器另有hostname，需添加此参数
