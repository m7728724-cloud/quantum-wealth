import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

commands = [
    'cd /root/quantum-wealth/frontend && npm install -g serve && npm run build',
    'pm2 delete qw-frontend || true',
    'cd /root/quantum-wealth/frontend && pm2 start serve --name qw-frontend -- -s build -l 3000',
    'pm2 save'
]

for cmd in commands:
    print(f'-- {cmd[:70]} --')
    stdin, stdout, stderr = client.exec_command(cmd)
    status = stdout.channel.recv_exit_status()
    print(f'Done {status}')
    out = stdout.read().decode('utf-8', errors='ignore').encode('cp1251', errors='ignore').decode('cp1251')
    if out: print(out[-1000:])

client.close()
