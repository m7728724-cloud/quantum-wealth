import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

commands = [
    'cd /root/quantum-wealth/backend && ./venv/bin/pip install -r requirements.txt && ./venv/bin/pip install python-dotenv certifi',
    'cd /root/quantum-wealth/frontend && npm install ajv@latest ajv-keywords@latest --save-dev --legacy-peer-deps',
    'pm2 restart qw-backend',
    'pm2 restart qw-frontend'
]

for cmd in commands:
    print(f'\n--- {cmd} ---')
    stdin, stdout, stderr = client.exec_command(cmd)
    status = stdout.channel.recv_exit_status()
    print(f'Exit status: {status}')
    print(stdout.read().decode('utf-8', errors='ignore').encode('cp1251', errors='ignore').decode('cp1251')[:500])

client.close()
