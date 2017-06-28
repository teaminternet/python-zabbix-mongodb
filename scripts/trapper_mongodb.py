#!/usr/bin/python

import os
import subprocess
import socket
import re
import time

from pymongo import MongoClient, errors
from sys import argv
from pprint import pprint
from datetime import datetime
#vars for Mongo
USER = ''
PASSWORD = ''
hostname = socket.getfqdn()
mongoconfig = '/etc/mongod.conf'

f = open(mongoconfig, 'r')
for line in f:
    line = line.strip()
    if re.match('port:', line):
	configname, port = line.split(" ")

HOST = 'mongodb://localhost:' + port + '/admin'

def mongo_connect(HOST,USER,PASSWORD):
    client,db = 0,0
    try:
        client = MongoClient(host = HOST)
        db = client.data
	db = client.admin
        db.authenticate(USER,PASSWORD)
        client.close()
    except:
        test = 0
    return(db)

def get_server_status(db):
    if db!=0:
        try:
            data = db.command({"serverStatus":1})
	    repl_data = []
	    try:
	        rs_members = db.command({"replSetGetStatus": 1})["members"]

	        count = 1
	        for member in rs_members:
	            if "self" in member:
	                repl_data = member

	            if member["state"] == 1:
	        	    master_optime = member["optimeDate"]

	            if member["_id"]:
	                count += 1
            except errors.OperationFailure, e:
                print "OK - Not running with replSet"
                repl_data = {'Empty': 'Null'}
	        master_optime = 0
	        count = 0

            db.logout()
            try:
                master_optime
            except NameError:
                master_optime = -1
            return(data, repl_data, master_optime, count)

        except:
            return('<Not successful command>')
    else:
        return('<Not successful connect to DataBase>')

def get_val(data,val):
    keys = []
    if type(data) == str:
        return(data)
    elif type(data) == dict:
        val = val.split('.')
        for i in val:
            i = i.rstrip().lstrip()
            if i !='' and i in data:
                data = data[i]
            else:
                return('<{i} - invalid key>'.format(i=i))
        return(data)
    else:
        return(data)

def check_vars_file(file):
    vals = []
    if os.path.exists(file):
        if os.path.isfile(file):
            try:
                f = open(file,'r')
                lines = f.readlines()
            except:
                return(0,'<Unreadable file: {file}>'.format(file=file))
            for i in lines:
                if i!='':
                    temp = i.split('\t')
                    if len(temp)==1:
                        vals.append(temp[0].rstrip().lstrip())
                    else:
                        return(0,'<Incorrect data in file: {file} value {temp}>'.format(file=file,temp=temp))
    if len(vals) == 0:
        return(0,'<Incorrect data in file: {file} file is empty>'.format(file=file))
    else:
        return(1,vals)



def chk_args(argv):
    key = ['out=','vars=','command=','names=']
    keys = {'out':str(argv[0])+'.out','command':''}

    for i in range(1,len(argv)):
        if argv[i] == '/?':
            print('''use the next command to get static:
python <script name> [out=<output file>] vars=<file name> command="<command>" names = <text>\n
where:
out= - path to output file (default if <script name>.out
vars= - file with field of database you wont to get
names= - rpefix to output fields name maby any text
command= - command to execute aftef collecting data (it's empty as default)''')
            exit()
        for j in key:
            if argv[i].find(j)!=-1:
                keys[j.replace('=','')]=argv[i].replace(j,'')

    if not keys['command']:
        keys['command'] = '/usr/bin/zabbix_sender -vv -s ' + hostname + ' -c /etc/zabbix/zabbix_agentd.conf  -i ' + keys['out']

    if 'names' not in keys:
	keys['names'] = 'mongodb'

    if 'vars' not in keys:
        print('<No Value File\nscript will be exit>')
        exit()
    else:
        print('params is OK')
        err, vals = check_vars_file(keys['vars'])
        if err == 0:
            print(vals)
            exit()
        else:
            print('Vars file is ok')
            #for i in keys:
            #    print('{key} {value}'.format(key = i,value=keys[i]))
            return(vals,keys)

def main():
    if len(argv)<2:
        print('<Check arguments>')
    else:
        text = {}
        vals,keys = chk_args(argv)
        db = mongo_connect(HOST,USER,PASSWORD)
        data, repl_data, master_optime, count = get_server_status(db)
        for i in vals:
            text[i] =get_val(data,i)
        f = open(keys['out'],'w')
        for i in text:
	    # Avoid Division by zero and false postives
	    if i == "metrics.repl.buffer.sizeBytes" and text[i] == 0:
		text[i] = 1

            f.write('{host} {word}.{key} {value}\n'.format(host = hostname, word = keys['names'],key=i,value=text[i]))
	for key, value in repl_data.iteritems():
	    if key == "optimeDate":
	        key = "slaveLag"
                if master_optime == -1:
                    lag = master_optime
                else:
                    lag = abs(master_optime - value).seconds
		value = lag
	    # Print Debug output
	    # print("Key %s Value %s" % (key, value))
	    f.write('{host} mongodb_repl.self.{key} {value}\n'.format(host = hostname, key = key, value=value))
        f.write('{host} mongodb.repl.hosts._length {value}\n'.format(host = hostname, value = count))
        f.close()
        #pprint(keys['command'])
        if keys['command']!='' and keys['command']!=None:
            try:
                p = subprocess.Popen(keys['command'], shell = True, stdout = subprocess.PIPE)
                s = ' '
                while s:
                    s = p.stdout.readline()
                    print(s)
                os.unlink(keys['out'])
            except:
                print('Error in running CMD')
        exit()

if __name__ == "__main__":
    main()
    #chk_args(argv)
