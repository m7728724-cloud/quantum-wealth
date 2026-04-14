import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

commands = [
    'pm2 logs qw-backend --lines 50 --nostream',
    'pm2 logs qw-frontend --lines 50 --nostream'
]

for cmd in commands:
    print(f'\n--- {cmd} ---')
    stdin, stdout, stderr = client.exec_command(cmd)
    print(stdout.read().decode('utf-8', errors='ignore').encode('cp1251', errors='ignore').decode('cp1251')[:2000])

client.close()
