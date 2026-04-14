import paramiko
import time
import sys

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

stdin, stdout, stderr = client.exec_command('pm2 logs qw-backend --lines 30 --nostream')
out = stdout.read().decode('utf-8', errors='ignore')
for line in out.splitlines():
    try:
        print(line.encode('cp1251', errors='replace').decode('cp1251'))
    except:
        pass

client.close()
