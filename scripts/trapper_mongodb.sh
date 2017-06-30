#!/bin/sh
date
cd /etc/zabbix/scripts
python /etc/zabbix/scripts/trapper_mongodb.py out=/tmp/mongodb_trapper.out vars=/etc/zabbix/scripts/zbx_vars.txt >> /var/log/zabbix/trapper_mongodb.log 2>&1 &
