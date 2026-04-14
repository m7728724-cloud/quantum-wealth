import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

commands = [
    'cd /root/quantum-wealth && git pull',
    'cd /root/quantum-wealth/backend && ./venv/bin/pip install -r requirements.txt python-dotenv certifi',
    'pm2 stop qw-backend || true',
    'pm2 delete qw-backend || true',
    'cd /root/quantum-wealth/backend && pm2 start ./venv/bin/python --name qw-backend -- server.py',
    'pm2 restart qw-frontend',
    'pm2 save'
]

for cmd in commands:
    print(f'-- {cmd} --')
    stdin, stdout, stderr = client.exec_command(cmd)
    res = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='ignore').encode('cp1251', errors='ignore').decode('cp1251')
    if out: print(out[:500])

client.close()
