import time as t
import pandas as pd
from time import time as todiff
import concurrent.futures
import os
import paramiko
from getpass import getpass
import socket
import subprocess

count_auth = input('How many users are into war..? ')
user,passwd = [],[]
for i in range(int(count_auth)):
  user.append(input("Enter user%s: "%(i+1)))
  passwd.append(getpass())
list_auth = list(zip(user,passwd)) #Credentials for connecting nodes

#Command to run by time
command = input("What's your desired cmd :) ")

time = input('Timer [Default 30sec]: ')
timer = 30 if time is "" else int(time)
hostnames = input('Enter either a server or list of servers as a file: ')
if input('want to save output (y/n) ') == 'y':
  saved_as = input("Save As: ")+".xlsx"

def get_hosts():
  'Takes input form user'
  if os.path.isfile(hostnames):
    hosts=[]
    for i in open(hostnames):
      hosts.append(i.strip())
    return hosts
  else:
    hosts = []
    hosts.append(hostnames.strip())
    return hosts

def sshing(host):
  pd.set_option('display.max_rows', None)
  pd.set_option('display.max_columns', None)
  pd.set_option('display.width', None)
  pd.set_option('display.max_colwidth', None)

  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  h = host.strip()
  for user,passwd in list_auth:
    user,passwd = user.strip(),passwd.strip()
    try: #SSH Connection to client
      print('Executing on %s from %s user'%(h,user))
      status = "Failed"
      #ping check
      try:
        ping_status = subprocess.check_output("ping -c 2 %s"%(h),shell=True,universal_newlines=True)
      except subprocess.CalledProcessError as e:
        print("Ping Failed on %s"%(h))
        status = 'Ping Failed'
        subprocess.call("echo %s >> pingfailed_%s.txt"%(h,hostnames),shell=True)
        break
      #ssh check
      try:
        ssh.connect(hostname=h,username=user,password=passwd,timeout=9)
      except socket.timeout:
        print("SSH Failed on %s"%(h))
        status = 'SSH Failed'
        subprocess.call("echo %s >> ssh_failed_%s.txt"%(h,hostnames),shell=True)
        break
      stdin,stdout,stderr = ssh.exec_command("%s"%(command),timeout=timer)
      stdin.write("%s\n"%(passwd))
      stdin.write("%s\n"%(passwd))
      stdin.flush()
      output,error=stdout.readlines(),stderr.readlines()
      subprocess.call("echo %s >> loggedin_%s.txt"%(h,hostnames),shell=True)
      status = 'Success'
      if len(output) == 0:
        output = 'Error'
      ssh.close()
      break
    except paramiko.ssh_exception.AuthenticationException: #Wrong passwords
      print('%s password not accepted on %s'%(user,h))
      status = 'Authentication Issue'
      subprocess.call("echo %s >> authentication-issues_%s.txt"%(h,hostnames),shell=True)
      continue
    except paramiko.ssh_exception.NoValidConnectionsError: #ConnectionRefused
      print('Connection refused on %s'%(h))
      status = 'Connection Refused'
      subprocess.call('echo %s >> connection-refused_%s'%(h,hostnames),shell=True)
      break
    except socket.gaierror: #Not in SISM
      print("%s wrong hostname"%(h))
      status = 'Not Valid'
      subprocess.call("echo %s >> check_sims_%s.txt"%(h,hostnames),shell=True)
      break # No need to check with another user authentication
    except socket.timeout: #timeout either at connect or exec_command
      print("Timeout to execute command on %s"%(h))
      status = 'Timeout'
      subprocess.call("echo %s >> timeout_%s.txt"%(h,hostnames),shell=True)
      break
    except paramiko.ssh_exception.SSHException: #Others ssh issues
      subprocess.call('echo %s >> connection-refused_%s'%(h,hostnames),shell=True)
      status = 'Connection Issue'
      break
    except socket.error:
      status = 'OS Error'
      print('os eror')
      break
    except:
      status = 'Something Unknown'
      print('something unknown')
    finally:
      if ssh:
        ssh.close()
      
  if status == 'Success':
    output = ''.join([x.strip() for x in output])
    result = pd.Series({h:output.strip()})
  else:
    result = pd.Series({h:'-'})
  dataframe = pd.DataFrame({'Output':result,'Status':status})
  return dataframe

#connect_ssh()
hosts = get_hosts()
output = []
with concurrent.futures.ThreadPoolExecutor() as e:
   for i in e.map(sshing,hosts):
     output.append(i)
full = pd.concat(output)

try:
  saved_as
except:
  print(full)
else:
#DataFrame into excel
  full.to_excel(saved_as,engine='xlsxwriter') #Ensure openpyxl pacaage is installed
