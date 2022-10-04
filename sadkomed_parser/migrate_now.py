#!/usr/bin/env python3

#Before run
#apt install python3-pip
#pip install pyyaml
#pip install paramiko

import argparse
import yaml
import subprocess
import paramiko
import re


hv_username = 'root'


# Принимаем аргументы коммандной строки ip адрес гипервизора
# и id виртуальной машины.
def cli():
    description_cli = "Proxmox zfs migration tools. Use on destination hypervisor. \
    Required arguments source hypervisor and virtual machine id."
    options = argparse.ArgumentParser(description=description_cli)
    options.add_argument('hv_ip', help="ip address of source hypervisor")
    options.add_argument('vm_id', help="virtual machine ID")
    return options.parse_args()


# Проверка статуса Виртуальной машины
def check_stat_vm(hv_ip, vm_id):
    vm_name = ""
    vm_status = False
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=hv_ip, username=hv_username)
    stdin, stdout, stderr = client.exec_command('qm list')
    out = bytes.decode(stdout.read(), encoding='utf-8')
    err = bytes.decode(stderr.read(), encoding='utf-8')
    if err != "":
        print(err)
        client.close()
        return vm_name, vm_status
    vm_data = re.search(r"( {} ).*".format(vm_id), out)
    if vm_data == None:
        print("There is no virtual machine with this id")
        vm_status = False
        return vm_name, vm_status
    vm_data = vm_data.group(0)
    vm_name = re.search(r"(?<=( {} ))\S*( )".format(vm_id), vm_data).group(0)
    vm_status = re.search(r"stopped", vm_data)
    if vm_status == None:
        print("The virtual machine is not in stopped status")
        vm_status = False
        client.close()
        return vm_name, vm_status
    vm_status = True
    client.close()
    return vm_name, vm_status


# Получение дисков для миграции
def list_storage(hv_ip, vm_id):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=hv_ip, username=hv_username)
    stdin, stdout, stderr = client.exec_command('cat /etc/pve/storage.cfg')
    out = bytes.decode(stdout.read(), encoding='utf-8')
    err = bytes.decode(stderr.read(), encoding='utf-8')
    if err != "":
        print(err)
        client.close()
        return 0
    stor_arr = re.split(r'\n\n', out)
    zpool_list = {}
    for i in stor_arr:
        name = re.search(r"(?<=(zfspool: )).*", i)
        path = re.search(r"(?<=(pool )).*", i)
        if name == None and path == None:
             continue
        else:
            zpool_list[name.group(0)] = path.group(0)
    stdin, stdout, stderr = client.exec_command('cat /etc/pve/qemu-server/{}.conf'.format(vm_id))
    out = bytes.decode(stdout.read(), encoding='utf-8')
    err = bytes.decode(stderr.read(), encoding='utf-8')
    if err != "":
        print(err)
        client.close()
        return 0
    dataset_list = []
    out = yaml.load(out, Loader=yaml.FullLoader)
    for key in out:
        if bool(re.match(r'(scsi|sata|virtio|ide)\d+' , key)):
            for i in zpool_list:
                if bool(re.match(r'{}'.format(i) , out[key])):
                    dataset = re.search(r'^[^,]*' ,out[key]).group(0)
                    dataset_list.append(re.sub(r'{}:'.format(i) , "{}/".format(zpool_list[i]) , dataset))
    return dataset_list


# Создание снепшотов
def snap_create(hv_ip, dataset_list):
    snap_done = []
    for i in dataset_list:
        result = subprocess.run(["ssh", "{}@{}".format(hv_username, hv_ip),  "zfs snapshot {}@automigrate".format(i)])
        if result.returncode != 0:
            for n in snap_done:
                subprocess.run(["ssh", "{}@{}".format(hv_username, hv_ip),  "zfs destroy {}@automigrate".format(n)])
            print("snapshot {}@automigrate ERROR".format(i))
            break
        snap_done.append(i)
        print("snapshot {}@automigrate CREATED".format(i))


# Отправка снапшотов
def snap_send(hv_ip, dataset_list, vm_name):
    for i in dataset_list:
        size_human = subprocess.run(["ssh", "{}@{}".format(hv_username, hv_ip), "zfs", "send", "{}@automigrate".format(i), "-nv"], stdout=subprocess.PIPE)
        size_human = bytes.decode(size_human.stdout, encoding='utf-8')
        size_human = re.search(r'(?<=(total estimated size is )).*', size_human).group(0)
        size_machine = subprocess.run(["ssh", "{}@{}".format(hv_username, hv_ip), "zfs", "send", "{}@automigrate".format(i), "-nP"], stdout=subprocess.PIPE)
        size_machine = bytes.decode(size_machine.stdout, encoding='utf-8')
        size_machine = re.search(r'(?<=(size)).*', size_machine).group(0)
        size_machine = re.search(r'\d+', size_machine).group(0)
        file = open('./send.sh'.format(i), 'w')
        file.write("#!/bin/bash\n")
        file.write("ssh {}@{} 'zfs send -R {}@automigrate | lz4c -z' | lz4c -d | pv --size {} --name '{} {}' | zfs receive {}".format(hv_username, hv_ip, i, size_machine, vm_name, size_human, i))
        file.close()
        subprocess.run(['chmod', '+x', './send.sh'])
        subprocess.run(['./send.sh'])
        subprocess.run(['rm', './send.sh'])


# Отправка конфига
def config_send(hv_ip, vm_id, vm_name):
    status = subprocess.run(["scp", "{}@{}:/etc/pve/qemu-server/{}.conf".format(hv_username, hv_ip, vm_id), "/etc/pve/qemu-server/{}.conf".format(vm_id)], stdout=subprocess.PIPE)
    if status.returncode != 0:
        print("Config vm {} {} not send".format(vm_id, vm_name))
    print("Config vm {} {} sended".format(vm_id, vm_name))


# Сценарий
def start_migrate():
    options = cli()
    hv_ip, vm_id = options.hv_ip, options.vm_id
    vm_name, vm_status = check_stat_vm(hv_ip, vm_id)
    if vm_status != True:
        return 1
    dataset_list = list_storage(hv_ip, vm_id)
    snap_create(hv_ip, dataset_list)
    snap_send(hv_ip, dataset_list, vm_name)
    config_send(hv_ip, vm_id, vm_name)


if __name__ == '__main__':
    start_migrate()
