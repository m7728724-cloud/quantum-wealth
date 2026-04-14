import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

commands = [
    'cd /root/quantum-wealth && git pull',
    'cd /root/quantum-wealth/frontend && npm run build',
    'pm2 restart qw-frontend'
]

for cmd in commands:
    print(f'-- {cmd[:70]} --')
    stdin, stdout, stderr = client.exec_command(cmd)
    status = stdout.channel.recv_exit_status()
    print(f'Done {status}')

client.close()
