#!/bin/bash
function loginfo()
{       
        msg=$1
        now=`date +%Y/%m/%d" "%X" "`
        echo -e ${now}${msg} >> extend-osd.log
}

loginfo "######################### Begin to ExtendOsd Now! #########################"
osdserver=""
confserver=""
diskprofile=""
nopurge="false"


confserver=""
TEMP=`getopt -o NWD:c:s:H: --long hostname:,no-purge,confserver:,osdserver:,diskprofile: -- "$@"`
eval set -- "$TEMP"
while true
do
        case "$1" in
		-N|--no-purge)
                        nopurge="true"
                        shift ;;
                -c|--confserver)
                        confserver=$2
                        shift 2 ;;
                -s|--osdserver)
                        osdserver=$2
                        shift 2 ;;
		-D|--diskprofile)
                        if [ $2 != "raid0" ] && [ $2 != "noraid" ]
                        then
                                echo "Error diskprofile arg! Arg of diskprofile should be [raid0|noraid] !"
                                loginfo "Error diskprofile arg! Arg of diskprofile should be [raid0|noraid] !"
                                loginfo "Deploy Error! Exit!"
                                exit 1;
                        fi
                        diskprofile=$2
                        shift 2 ;;
                --)shift;break;;
                ?)
                        echo "Args ERROR!"
                        loginfo "Args ERROR!\nDeploy Error! Exit!"
                        exit 1;;
        esac
done

rm -rf ceph.*

if [[ $osdserver == "" ]] || [[ $confserver == "" ]] || [[ $diskprofile == "" ]]
then
	loginfo "Lack of Arguments ! EXIT !"
	echo -e "Lack of Arguments !\nUsage: sh expend-osd.sh -c CONFSERVER -s OSDSERVER -D [raid0|noraid] [-N|--no-purge]"
	exit 1
fi
echo "confServerName: "$confserver" osdServerName: "$osdserver
loginfo "confServerName: "$confServerIP" osdServerName: "$osdServerIP


## Create fabric.py 
cp fabfile.org.py fabfile.py.bak
sed -i "s/#diskprofile#/#diskprofile#\ndiskprofile = \"$diskprofile\"/g" ./fabfile.py.bak
cp fabfile.py.bak fabfile.py

## Change HostName
fab updateRepoAddress -P -H $osdserver

## Add ssh auth
fab push_key -H $osdserver

##Clean OriginData
if [[ $nopurge == "false" ]]
then
        loginfo "Begin to PURGE!"
        fab PurgeCeph -P -H $osdserver
fi

## Install ceph rpm
fab InstallCeph -P -H $osdserver

## GatherKeys
ceph-deploy gatherkeys $confserver

scp root@$confserver:/etc/ceph/ceph.conf ./

## remove "osd crush update on start" config to make osd running after created
sed -i '/osd crush update on start = False/d' ceph.conf

## Install OSD
fab prepareDisks -P -H $osdserver
loginfo "Begin to deploy OSDs !"
fab DeployOSDs -P -H $osdserver

## Copy CephConf
fab CopyCephConf -P -H $osdserver

fab updatentpconfig -P -H $osdserver
fab updatefstab -P -H $osdserver
fab startdiamond -P -H $osdserver
