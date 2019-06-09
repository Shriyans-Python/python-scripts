#!/usr/bin/python3
#THIS SCRIPT IS USED TO FETCH THE CPU AND MEMORY DETAILS IN THE LIST OF SERVERS#
#THIS HAS BEEN WRITTEN AND MODIFIED BY SHRIYANS CHOUDHURI#
import os
import paramiko
import subprocess
import xlsxwriter
import argparse
import datetime

## SSH FUNCTION TO CONNECT TO OTHER SERVERS
def ssh_comm(ip,usr,passwd,cmd):
    try:
        client = paramiko.SSHClient()
        #client.load_host_keys('/home/circle/.ssh/known_hosts')
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip,username=usr,password=passwd,timeout=5)
        ssh_session = client.get_transport().open_session()
        if ssh_session.active:
            ssh_session.exec_command(cmd)
            output = ssh_session.recv(1024)
            Mystr = output.decode(encoding='UTF-8')
        return Mystr
    except :
        print(ip + "Unable to connect to server check userid , password or server status")

### EXCEL WRITE FROM THE COMMAND OUTPUT
todays_date = str(datetime.datetime.now().strftime("%Y-%m-%d_%H_%M") )+ '.xlsx'
workbook = xlsxwriter.Workbook('CPU_MEM_UTILIZATION_REPORT_' + todays_date )
worksheet_cpu_mem = workbook.add_worksheet('CPU_MEM')
worksheet_fs = workbook.add_worksheet('Filesystem Usage')

#FORMATTING FOR EXCEL
format_excel = workbook.add_format({'bold': True,'bg_color': 'yellow','border': 1})
format_normal = workbook.add_format({'bold': True,'bg_color': 'green','border': 1})
format_alert = workbook.add_format({'bold': True,'bg_color': 'red','border': 1})
format_hostname = workbook.add_format({'bold': True,'border': 1})

#EXCEL HEADERS 
worksheet_cpu_mem.set_column(0,2,15)
worksheet_cpu_mem.write('A1', 'HOSTNAME',format_excel)
worksheet_cpu_mem.write('B1', 'CPU USAGE',format_excel)
worksheet_cpu_mem.write('C1', 'MEMORY USAGE',format_excel)

worksheet_fs.set_column(0,2,55)



#COMMAND REFERENCE 
Linux_mem = "free -m|grep -v  total|head -1|awk -F ' ' '{ sum = ($3/$2) * 100 } END { print sum}'"
Linux_cpu = "vmstat |tail -1|awk -F ' ' '{ sum = (100 - $15) } END { print sum }'"
AIX_mem = "svmon -G -O unit=GB|grep memory|awk '{ sum = ($3/$2) * 100 } END {print sum}'"
AIX_cpu = "sar -u |grep Average|awk '{ sum = ( 100 - $5 )} END { print sum }'"
Solaris_mem = "a=$(/usr/sbin/prtconf | /usr/bin/awk '/Memory/ {print $3*1024}'); vmstat 1 1 | tail -1 | awk \"{print 100-(\$5/$a)*100}\""
Solaris_cpu = "sar -u |grep Average|awk '{ sum = ( 100 - $5 )} END { print sum }'"  
uname_cmd = "uname"
FS_cmd = "df -k|awk '0+$5 >= 0 {print $6}'|grep -v Mounted"
FS_usage = "df -k|grep -v Mounted|awk '0+$5 >= 0 {print $5}'"

#List of Servers to connect .
with open('servers.txt') as servers :
    hosts = servers.read().splitlines()

# Arguments to be added while executing the script
parser = argparse.ArgumentParser()
parser.add_argument("-u","--user",required = True,help = "User id with which the script will be executed ")
parser.add_argument("-p","--passwd",required = True,help = "Password of the user")
parser_out = vars(parser.parse_args())
usr = parser_out['user']
passwd = parser_out['passwd']

#This loop will be fetching the data and writing to excel file 
row = 1
column = 0

for host in hosts:
    try:
        UNAME_OUT =  ssh_comm(host,usr,passwd,uname_cmd)
        UNAME = UNAME_OUT.rstrip('\n')
    except:
        continue
    try:
    	if UNAME == "Linux":
        	CPU = float(ssh_comm(host,usr,passwd,Linux_cpu))
        	MEM = float(ssh_comm(host,usr,passwd,Linux_mem))
    	elif UNAME == "AIX":
        	CPU = float(ssh_comm(host,usr,passwd,AIX_cpu))
        	MEM = float(ssh_comm(host,usr,passwd,AIX_mem))
    	elif UNAME == "SunOS":
        	CPU = float(ssh_comm(host,usr,passwd,Solaris_cpu))
        	MEM = float(ssh_comm(host,usr,passwd,Solaris_mem))
    except:
        CPU = "No Output"
        MEM = "No Output"
        worksheet_cpu_mem.write(row , column , host,format_hostname)
        worksheet_cpu_mem.write(row , column + 1, CPU,format_alert)
        worksheet_cpu_mem.write(row , column + 2, MEM,format_alert)
        continue 

    worksheet_cpu_mem.write(row , column , host,format_hostname)
    if CPU >= 90.00 :
       	worksheet_cpu_mem.write(row , column + 1, CPU,format_alert)
    else:
       	worksheet_cpu_mem.write(row , column + 1,CPU,format_normal)
    if MEM >= 90.00 :
       	worksheet_cpu_mem.write(row , column + 2, MEM,format_alert)
    else:
       	worksheet_cpu_mem.write(row , column + 2,MEM,format_normal)
    row += 1

#The below loop will write the output of filesystem utilization in the servers.

row = 0
column = 0

for host in hosts:
    worksheet_fs.write(row , column , 'HOSTNAME = '+ host ,format_excel)
    worksheet_fs.write(row , column + 1,'FILESYSTEM UTILIZATION',format_excel)
    
    FS_NAME = ssh_comm(host,usr,passwd,FS_cmd)
    FS_USAGE = ssh_comm(host,usr,passwd,FS_usage)
    
    print(FS_NAME)
     
    FS_NAME_OUT = FS_NAME.split()
    FS_USAGE_OUT = FS_USAGE.split()
    
    print (FS_NAME_OUT)
    print (FS_USAGE_OUT)
    
    DIC = dict(zip(FS_NAME_OUT,FS_USAGE_OUT))

    print(DIC) 
    for KEY,VALUE in DIC.items():
        worksheet_fs.write(row + 1,column ,KEY ,format_hostname)
        worksheet_fs.write(row + 1, column + 1 , VALUE ,format_alert)
        row += 1
    row += 1 
    print("SECOND")
    
workbook.close()

#SEND MAIL WITH THE OUTPUT FILE
#mail = 'echo "CPU MEMORY UTILIZATION REPORT"| mail -s "CPU MEMORY UTILIZATION REPORT" -a CPU_MEM_UTILIZATION_REPORT_*.xlsx email@id'
#mail_exitcode = os.system(mail)

#if mail_exitcode == 0:
#    print("Output Send to mail id ")
#else:
#    print("Mail has not been sent , please check server for error")




    

