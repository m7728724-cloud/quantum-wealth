import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

env_cmd = "echo 'REACT_APP_BACKEND_URL=http://212.52.1.3:8001' > /root/quantum-wealth/frontend/.env"
client.exec_command(env_cmd)

stdin, stdout, stderr = client.exec_command('pm2 restart qw-frontend')
print(stdout.read().decode('utf-8'))

client.close()
