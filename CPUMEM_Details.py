#!/usr/bin/python3
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
        print("Unable to connect to server check userid , password or server status")

### EXCEL WRITE FROM THE COMMAND OUTPUT
todays_date = str(datetime.datetime.now().strftime("%Y-%m-%d_%H_%M") )+ '.xlsx'
workbook = xlsxwriter.Workbook('CPU_MEM_UTILIZATION_REPORT_' + todays_date )
worksheet = workbook.add_worksheet()

#FORMATTING FOR EXCEL
format_excel = workbook.add_format({'bold': True,'bg_color': 'yellow','border': 1})
format_normal = workbook.add_format({'bold': True,'bg_color': 'green','border': 1})
format_alert = workbook.add_format({'bold': True,'bg_color': 'red','border': 1})
format_hostname = workbook.add_format({'bold': True,'border': 1})

#EXCEL HEADERS 
worksheet.set_column(0,2,15)
worksheet.write('A1', 'HOSTNAME',format_excel)
worksheet.write('B1', 'CPU USAGE',format_excel)
worksheet.write('C1', 'MEMORY USAGE',format_excel)


#COMMAND REFERENCE 
Linux_mem = "free -m|grep -v  total|head -1|awk -F ' ' '{ sum = ($3/$2) * 100 } END { print sum}'"
Linux_cpu = "vmstat |tail -1|awk -F ' ' '{ sum = (100 - $15) } END { print sum }'"
AIX_mem = "svmon -G -O unit=GB|grep memory|awk '{ sum = ($3/$2) * 100 } END {print sum}'"
AIX_cpu = "sar -u |grep Average|awk '{ sum = ( 100 - $5 )} END { print sum }'"
Solaris_mem = "a=$(/usr/sbin/prtconf | /usr/bin/awk '/Memory/ {print $3*1024}'); vmstat 1 1 | tail -1 | awk \"{print 100-(\$5/$a)*100}\""
Solaris_cpu = "sar -u |grep Average|awk '{ sum = ( 100 - $5 )} END { print sum }'"  
uname_cmd = "uname"

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
  UNAME =  ssh_comm(host,usr,passwd,uname_cmd)
   
  if UNAME == Linux:
   
      print(UNAME)
          
  
  #    CPU = float(ssh_comm(host,usr,passwd,Linux_cpu))
  #    MEM = float(ssh_comm(host,usr,passwd,Linux_mem))
  #elif UNAME == "AIX":
   #   CPU = float(ssh_comm(host,usr,passwd,cmd2))    
   #   MEM = float(ssh_comm(host,usr,passwd,cmd1))
  #elif UNAME == "SunOS":
   #   CPU = float(ssh_comm(host,usr,passwd,cmd2))
   #   MEM = float(ssh_comm(host,usr,passwd,cmd1))

  worksheet.write(row , column , host,format_hostname)
  if CPU >= 90.00 :
      worksheet.write(row , column + 1, CPU,format_alert)
  else:
      worksheet.write(row , column + 1,CPU,format_normal)
  if MEM >= 90.00 :
      worksheet.write(row , column + 2, MEM,format_alert)
  else:
      worksheet.write(row , column + 2,MEM,format_normal)
  row += 1

workbook.close()

#SEND MAIL WITH THE OUTPUT FILE
mail = 'echo "CPU MEMORY UTILIZATION REPORT"| mail -s "CPU MEMORY UTILIZATION REPORT" -a CPU_MEM_UTILIZATION_REPORT_*.xlsx email@id'
mail_exitcode = os.system(mail)

if mail_exitcode == 0:
    print("Output Send to mail id ")
else:
    print("Mail has not been sent , please check server for error")




    

