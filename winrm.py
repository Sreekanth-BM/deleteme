import subprocess
import pandas as pd
import concurrent.futures
from getpass import getpass
import winrm
import os

class DoWinrm:
  def __init__(self):
    'username, passwd, command'
    self.username = input("Enter username: ")
    self.passwd = getpass()
    self.command_to_run = input("Enter command to run: ")

  def get_hosts(self):
    'Takes input form user'
    self.hostnames = input("Enter either file of servers or server: ")
    if os.path.isfile(self.hostnames):
      hosts=[]
      for i in open(self.hostnames):
        hosts.append(i.strip())
      return hosts
    else:
      hosts = []
      hosts.append(self.hostnames.strip())
      return hosts

  def winrming(self,host):
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    try:
      prot = winrm.protocol.Protocol(endpoint = "http://%s:5986/wsman"%(host.strip()),transport = 'ntlm',username = self.username.strip(),password = self.passwd,server_cert_validation = 'ignore')
      shell = prot.open_shell()
    except:
      output = '-'
      status = 'SSH Failed'
    else:
      try:
        command = prot.run_command(shell,self.command_to_run)
        output,error,status = prot.get_command_output(shell,command)
        output = str(output,'utf-8').strip()
        error = str(error,'utf-8').strip()
        # Error occured
        if len(output) == 0:
          output = error
          status = 'Error'
        else:
          status = 'Success'
      except:
        status = 'Unable to run command'
        output = '-'
    finally:
      host = host.strip()
      output = pd.Series({host:output})
      status = pd.Series({host:status})
      dataframe = pd.DataFrame({'Output':output,'Status':status})
      return dataframe

session = DoWinrm()
hosts = session.get_hosts()
if input('want to save output (y/n) ') == 'y':
  saved_as = input("Save As: ")+".xlsx"

output = []
with concurrent.futures.ThreadPoolExecutor() as e:
   for i in e.map(session.winrming,hosts):
     output.append(i)
full = pd.concat(output)

try:
  saved_as
except:
  print(full)
else:
  full.to_excel(saved_as,engine='xlsxwriter')
