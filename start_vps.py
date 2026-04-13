import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

commands = [
    'npm install -g pm2',
    'cd /root/quantum-wealth && git pull',
    'pm2 stop all || true',
    'pm2 delete all || true',
    "HOST=0.0.0.0 pm2 start '/root/quantum-wealth/backend/venv/bin/python server.py' --name 'qw-backend' --cwd /root/quantum-wealth/backend",
    "HOST=0.0.0.0 pm2 start npm --name 'qw-frontend' --cwd /root/quantum-wealth/frontend -- start",
    'pm2 save',
    'ufw allow 3000/tcp',
    'ufw allow 8001/tcp',
    'iptables -I INPUT -p tcp --dport 3000 -j ACCEPT',
    'iptables -I INPUT -p tcp --dport 8001 -j ACCEPT'
]

for cmd in commands:
    print(f'Executing: {cmd}')
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode().strip()
    if out: print(out[:200])

client.close()
