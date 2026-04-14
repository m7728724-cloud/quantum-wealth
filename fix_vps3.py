import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

commands = [
    'pm2 delete all || true',
    'cd /root/quantum-wealth/backend && ./venv/bin/pip install python-dotenv certifi motor fastapi uvicorn pymongo pydantic pydantic-settings',
    'cd /root/quantum-wealth/backend && pm2 start server.py --name qw-backend --interpreter ./venv/bin/python',
    'cd /root/quantum-wealth/frontend && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps --ignore-scripts',
    'cd /root/quantum-wealth/frontend && HOST=0.0.0.0 pm2 start npm --name qw-frontend -- start',
    'pm2 save'
]

for cmd in commands:
    print(f'-- {cmd[:50]} --')
    stdin, stdout, stderr = client.exec_command(cmd)
    status = stdout.channel.recv_exit_status()
    print(f'Done {status}')
    out = stdout.read().decode('utf-8', errors='ignore').encode('cp1251', errors='ignore').decode('cp1251')
    if out: print(out[:100])

client.close()
