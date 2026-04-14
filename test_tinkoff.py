import paramiko
import time
import json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

# Pull + restart
for cmd in ['cd /root/quantum-wealth && git pull', 'pm2 restart qw-backend']:
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    stdout.channel.recv_exit_status()

time.sleep(6)

# Login
login_cmd = "curl -s -X POST -H 'Content-Type: application/json' -d '{\"username\": \"Vika-net1\", \"password\": \"Dd19840622\"}' http://127.0.0.1:8001/api/auth/login"
stdin, stdout, stderr = client.exec_command(login_cmd)
login_resp = json.loads(stdout.read().decode('utf-8'))
token = login_resp['access_token']

# Test Tinkoff status
cmd = f"curl -s -H 'Authorization: Bearer {token}' http://127.0.0.1:8001/api/tinkoff/status"
stdin, stdout, stderr = client.exec_command(cmd)
tink_status = stdout.read().decode('utf-8', errors='ignore')
print(f'Tinkoff Status: {tink_status}')

# Test Tinkoff sync
cmd = f"curl -s -X POST -H 'Authorization: Bearer {token}' http://127.0.0.1:8001/api/tinkoff/sync"
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
tink_sync = stdout.read().decode('utf-8', errors='ignore')
print(f'\nTinkoff Sync: {tink_sync[:500]}')

client.close()
