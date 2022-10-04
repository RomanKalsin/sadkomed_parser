#!/bin/bash

HV=$1
VM=$2
echo \# $HV / $VM > file
if [[ -z $HV || -z $VM ]] ; then
echo "Source hypervisor ip address not set or virtual machine id ./command {hv_ip} {vm_id}"
exit
fi 

ssh root@$HV "cat /etc/pve/storage.cfg" | grep -E "^zfspool:" -A 1 | grep "pool "| while read line
do

set -- $line
echo $2 >> file 
done




#STORAGE[zfs-hdd]="zfs-hdd/local/proxmox"
#echo ${STORAGE[zfs-hdd]}
#ssh root@192.168.0.34 "zfs list -H -o name -t volume" 


