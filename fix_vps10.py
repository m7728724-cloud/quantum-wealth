import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

commands = [
    'cd /root/quantum-wealth/backend && ./venv/bin/pip install PyJWT',
    'pm2 restart qw-backend'
]

for cmd in commands:
    print(f'-- {cmd[:70]} --')
    stdin, stdout, stderr = client.exec_command(cmd)
    status = stdout.channel.recv_exit_status()
    print(f'Done {status}')
    out = stdout.read().decode('utf-8', errors='ignore').encode('cp1251', errors='ignore').decode('cp1251')
    if out: print(out[-500:])

print('-- wait 5s --')
time.sleep(5)
stdin, stdout, stderr = client.exec_command('pm2 logs qw-backend --lines 40 --nostream')
out = stdout.read().decode('utf-8', errors='ignore').encode('cp1251', errors='ignore').decode('cp1251')
print(out[-1500:])

client.close()
