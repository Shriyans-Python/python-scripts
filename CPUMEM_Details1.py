#!/usr/bin/python3
import os
import paramiko
import subprocess
import xlsxwriter
import argparse

## SSH FUNCTION TO OTHER SERVERS
def ssh_comm(ip,usr,passwd,cmd):
    client = paramiko.SSHClient()
    #client.load_host_keys('/home/circle/.ssh/known_hosts')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip,username=usr,password=passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.exec_command(cmd)
        output = ssh_session.recv(1024)
        Mystr = output.decode(encoding='UTF-8')
    return Mystr

### EXCEL WRITE FROM THE COMMAND OUTPUT
workbook = xlsxwriter.Workbook('CPU_MEM.xlsx')
worksheet = workbook.add_worksheet()

#FORMATTING FOR EXCEL
format_excel = workbook.add_format({'bold': True,'bg_color': 'yellow','border': 1})
format_normal = workbook.add_format({'bold': True,'bg_color': 'green','border': 1})
format_alert = workbook.add_format({'bold': True,'bg_color': 'red','border': 1})
format_hostname = workbook.add_format({'bold': True,'border': 1})
#EXCEL HEADERS 
worksheet.write('A1', 'HOSTNAME',format_excel)
worksheet.write('B1', 'CPU USAGE',format_excel)
worksheet.write('C1', 'MEMORY USAGE',format_excel)

#COMMAND REFERENCE 
cmd1 = "free -m|grep -v  total|head -1|awk -F ' ' '{ sum = ($3/$2) * 100 } END { print sum}'"
cmd2 = "vmstat |tail -1|awk -F ' ' '{ sum = (100 - $15) } END { print sum }'"


with open('servers.txt') as servers :
    hosts = servers.read().splitlines()

# Arguments to be added while executing the script
parser = argparse.ArgumentParser()
parser.add_argument("-u","--user",required = True,help = "Enter the user id with which the script will be executed ")
parser.add_argument("-p","--passwd",required = True,help = "Enter the user password")
parser_out = vars(parser.parse_args())
usr = parser_out['user']
passwd = parser_out['passwd']

# This loop will be fetching the data and writing to excel file 
row = 1
column = 0

for host in hosts:
  CPU = float(ssh_comm(host,usr,passwd,cmd2))
  MEM = float(ssh_comm(host,usr,passwd,cmd1))
  
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

