# python-zabbix-mongodb

This application ships mongodb metrics through zabbix sender. The motivation for this tool was to use most of the preinstalled linux distribution features and don't install much packages to reduce server load by zabbix check. As a template we used [these scripts](https://www.zabbix.com/forum/showthread.php?t=52945). Thanks to sturi.    

This script works as a Zabbix Trapper and collect all MongoDB metrics with one call.    

These scripts were tested with the following linux distributions, packages and versions:
- Ubuntu 16.04 LTS
- CentOS 7
- MongoDB 3.2.4
- Python 2.7
- Zabbix 3.2 (it works also with zabbix-agent 3.0 and 2.2, the server version is important)

## Requirements

- zabbix-sender
- python-pymongo
- zabbix-agent

## Installation

### Requirements

It is recommended to use the current stable zabbix version. That is why we recommend to use the current zabbix-agent if you start from stack

RedHat/CentOS
```bash
yum -y install http://repo.zabbix.com/zabbix/3.2/rhel/7/x86_64/zabbix-release-3.2-1.el7.noarch.rpm
```

Ubuntu/Debian
```bash
wget http://repo.zabbix.com/zabbix/3.2/debian/pool/main/z/zabbix-release/zabbix-release_3.2-1+wheezy_all.deb
dpkg -i zabbix-release_3.2-1+wheezy_all.deb
apt-get update
```
    

After you can install the requirements

RedHat/CentOS
```bash
yum -y install zabbix-agent
```

Debian/Ubuntu
```bash
apt-get install zabbix-agent
```
    

If you have already installed the previous packages you can start from here

RedHat/CentOS
```bash
yum -y install zabbix-sender python-pymongo
```

Debian/Ubuntu
```bash
apt-get install zabbix-sender python-pymongo
```

### Installation of the check itself

Please note that the instructions are different, if you are using zabbix agent 2.2. The structure of configuration is different.

```bash
cd /tmp
git clone git@github.com:teaminternet/python-zabbix-mongodb.git
cd python-zabbix-mongodb
mkdir -p /etc/zabbix/scripts
cp -av scripts/* /etc/zabbix/scripts
cp -av zabbix_agentd.d/* /etc/zabbix/zabbix_agentd.d
```
    

Please make sure that you use the following setting in your zabbix_agend.conf
```
Include=/etc/zabbix/zabbix_agentd.d
```
    

Now restart your zabbix agent
```bash
systemctl zabbix-agent restart
```

### Importing the Templates

You need to start with the template `Template_App_MongoDB_Base.xml`. This Template is the basement for the others. The Template `Template_App_MongoDB_Config.xml` is used for MongoDB Config Server. For MongoS and MongoD Server please use the Template `Template_App_MongoDB_ReplicaSet.xml`

## Additional informations

All main metrics which should be sent to Zabbix are stored in file `zbx_vars.txt`. You can add or remove if you need. You should always check available metrics by using the following command in the MongoDB client
```
rs.status()
```
    

All Replication informations are handled by the script itself.

## TODO

- Check `db.runCommand({"collstats": "oplog.rs"})` for broken oplog

## Contribute

Please feel free to open pull requests. Any ideas for improvements are welcome.

## License

Apache 2.0
