import os
import sys
import requests
import json
import datetime
from crontab import CronTab

def updateAll():
    """
    更新所有A记录.
    """
    print('-----%s-----' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    for domain in domains:
        to_update_id.clear()
        getArecord(domain)
        if len(to_update_id) == 0:
            print("[%s] Record up to date." % domain)
        for record in to_update_id:
            modifyArecord(domain, record)


def getPublicIP():
    """
    通过访问一个网页获取公网IP.
    """
    url = 'http://myip.ipip.net'
    try:
        r = requests.get(url)
        r.raise_for_status()
    except:
        print(
            "\033[1;31m[Error]\033[0m Unable to get public IP address, please check network connectivity.\n")
        sys.exit()
    for i in range(0, len(r.text)):
        if r.text[i] == ' ' and r.text[i + 1] == ' ':
            ip = r.text[6:i - 1].strip()
            break
    return ip


def checkAPI():
    """
    检测LoginToken.
    """
    url = api + "/Info.Version"
    param = public_params
    try:
        r = requests.post(url, data=param, headers=header)
        r.raise_for_status()
    except:
        print("\033[1;31m[Error]\033[0m Please check network connectivity.\n")
        sys.exit()
    r.encoding = r.apparent_encoding
    result = json.loads(r.text)
    if result['status']['code'] != '1':
        print(
            "\n\033[1;31m\033[1;31m[Error]\033[0m\033[0m " + result["status"]["message"] + "\nExiting...")
        sys.exit()


def checkDomains():
    """
    检查域名所有权.
    """
    url = api + '/Record.List'
    param = public_params.copy()
    cnt = 0
    for domain in domains:
        domain_split = domain.split('.')
        if len(domain_split) > 3:
            print(
                "\033[1;31m[Error]\033[0m Only support Third/Second Level Domain.\nExiting...")
            sys.exit()
        param["domain"] = domain_split[-2] + '.' + domain_split[-1]
        try:
            r = requests.post(url, data=param, headers=header)
            r.raise_for_status()
        except:
            print("\033[1;31m[Error]\033[0m Please check network connectivity.\n")
            sys.exit()
        r.encoding = r.apparent_encoding
        result = json.loads(r.text)
        if result["status"]["code"] != '1':
            print('\033[1;31m[Error]\033[0m [' + domain + '] ' +
                  result["status"]["message"] + '.')
        else:
            cnt += 1
            print("\033[1;32m[SUCCESS]\033[0m " + domain)
    if cnt != len(domains):
        print("Please check config.json!\nExiting...")
        sys.exit()


def getArecord(domain):
    """
    获得当前域名的A记录.
    """
    url = api + '/Record.List'
    param = public_params.copy()
    domain_split = domain.split('.')
    param["domain"] = domain_split[-2] + '.' + domain_split[-1]
    param["record_type"] = 'A'
    if len(domain_split) == 3:
        param["sub_domain"] = domain_split[0]  # 只支持3级域名 a.b.com（即常说的二级域名）
    try:
        r = requests.post(url, data=param, headers=header)
        r.raise_for_status()
    except:
        print("\033[1;31m[Error]\033[0m Please check network connectivity.\n")
        sys.exit()
    r.encoding = r.apparent_encoding
    result = json.loads(r.text)
    for record in result["records"]:
        if record["enabled"] != '1':  # 只更改已生效的记录
            continue
        if len(domain_split) == 3 or (len(domain_split) == 2 and (record["name"] == '*' or record["name"] == '@')):
            if record["value"] != IP:  # 只有IP地址不同时才会提交更改
                to_update_id.append(record["id"])


def modifyArecord(domain, record):
    """
    修改当前A记录的值.
    """
    url = api + '/Record.Ddns'
    param = public_params.copy()
    domain_split = domain.split('.')
    param["domain"] = domain_split[-2] + '.' + domain_split[-1]
    param["record_id"] = record
    param["record_line"] = "默认"
    param["value"] = IP
    if len(domain_split) == 3:
        param["sub_domain"] = domain_split[0]
    try:
        r = requests.post(url, data=param, headers=header)
        r.raise_for_status()
    except:
        print("\033[1;31m[Error]\033[0m Please check network connectivity.\n")
        sys.exit()
    r.encoding = r.apparent_encoding
    result = json.loads(r.text)
    print("[%s]" % domain, end=result["status"]["message"] + '\n')
    print(r.text)


def setup():
    """
    生成默认配置文件.
    """
    print("\nIt seems that you're running this for the first time.")
    while True:
        print("Install? (Y/N)", end=' ')
        op = input()
        if op == 'Y' or op == 'y':
            print("Installing...", end='  ')
            default_json = '{\n\t"ID": "type_your_TokenID_here",\n\t"Token": "type_your_Token_here",\n\t"Domains": [\n\t\t"Example1.com",\n\t\t"Example2.com"\n\t]\n}'
            os.mknod(path + 'config.json')
            with open(path + 'config.json', mode='w') as fi:
                fi.write(default_json)
            print('\033[1;32m[SUCCESS]\033[0m')
            print("Files in path:")
            os.system("ls " + path)
            print('Please fill "config.json" with your Token.\nExiting...')
            sys.exit()
        elif op == 'N' or op == 'n':
            print("Exiting...")
            sys.exit()


def uninstall():
    """
    卸载，删除本程序及配置文件，删除定时任务.
    """
    print("Uninstalling...")
    delCrontab()
    os.remove(path + 'config.json')
    os.remove(path + 'DDNS.log')
    os.remove(path + 'DDNS.py')
    os.remove(__file__)
    print("\033[1;32m[SUCCESS]\033[0m All files removed.\nExiting...")
    sys.exit()


def setCrontab():
    """
    设置定时任务.
    """
    delCrontab()
    t = int(input("Enter updating frequence(min): "))
    job = user_cron.new(command='/bin/python3 ' + path + 'DDNS.py >> ' + path + 'DDNS.log', comment='DDNS for DNSPOD')
    job.minute.every(t)
    job.enable()
    user_cron.write()
    print("\033[1;32m[SUCCESS]\033[0m A record(s) will be automatically updated every %d minute(s)." % t)


def delCrontab():
    """
    删除定时任务.
    """
    user_cron.remove_all(comment='DDNS for DNSPOD')
    user_cron.write()
    print("\033[1;32m[SUCCESS]\033[0m All automatic tasks have been deleted.")


def selecOps():
    """
    打印菜单，选择功能.
    """
    print("1. Update A record(s) of domain(s) in config.json.")
    print("2. Enable automatic update of A record(s).")
    print("3. Disable automatic update of A record(s).")
    print("4. Uninstall")
    print("5. Exit")
    while True:
        print("Selection:", end=' ')
        op = input()
        if op == '1':
            updateAll()
        elif op == '2':
            setCrontab()
        elif op == '3':
            delCrontab()
        elif op == '4':
            uninstall()
        elif op == '5':
            print("Exiting...")
            sys.exit()


api = 'https://dnsapi.cn'
path = ''
for i in __file__.split('/')[0:-1]:
    path = path + i + '/'
header = {"User-Agent": "N_tivus DDNS/0.1Alpha(sdtalyk@gmail.com)"}
to_update_id = []


if __name__ == '__main__':
    # 安装
    print("************************************************")
    print("*DDNS for DNSPOD [Version:0.1 Alpha] By N_tivus*")
    print("************************************************")
    print("Checking the configuration...")
    if not os.path.exists(path + 'config.json'):
        setup()

# 读取config.json并合成公共参数
try:
    with open(path + 'config.json', mode='r') as fo:
        cfg = json.load(fo)
    public_params = {'login_token': cfg["ID"].strip(
    ) + ',' + cfg["Token"].strip(), 'format': 'json'}
    domains = cfg["Domains"]
except:
    print('\n\033[1;31m\033[1;31m[Error]\033[0m\033[0m "config.json" is invalid.\nPlease delete it and reopen the program.\nExiting...')
    sys.exit()

# 每次运行都查询API和Token可用性
checkAPI()

if __name__ == '__main__':
    # 检测域名合法性, 仅在安装/手动运行时需要
    checkDomains()
    print("\033[1;32m[SUCCESS]\033[0m Configuration verified.")

# 获取公网IP
IP = getPublicIP()

if __name__ == '__main__':
    # 定时任务
    user_cron = CronTab(user=True)
    # 功能选择, 仅在安装/手动运行/卸载时需要
    print("Your Public IP is %s." % IP)
    print('Type in the following numbers to select the action to be operated:')
    selecOps()
