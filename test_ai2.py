import paramiko
import json
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

# Pull + restart
for cmd in ['cd /root/quantum-wealth && git pull', 'pm2 restart qw-backend']:
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    stdout.channel.recv_exit_status()

time.sleep(5)

# Login
login_cmd = "curl -s -X POST -H 'Content-Type: application/json' -d '{\"username\": \"Vika-net1\", \"password\": \"Dd19840622\"}' http://127.0.0.1:8001/api/auth/login"
stdin, stdout, stderr = client.exec_command(login_cmd)
token = json.loads(stdout.read().decode('utf-8'))['access_token']

# Trigger AI analysis
print('Triggering AI Portfolio Analysis via Claude (OpenRouter)...')
print('This may take 10-20 seconds...\n')
cmd = f"curl -s -X POST -H 'Authorization: Bearer {token}' -H 'Content-Type: application/json' -d '{{}}' http://127.0.0.1:8001/api/ai/portfolio-insight"
stdin, stdout, stderr = client.exec_command(cmd, timeout=90)
result = stdout.read().decode('utf-8', errors='ignore')

try:
    data = json.loads(result)
    print(json.dumps(data, indent=2, ensure_ascii=False))
except:
    print(f'Raw: {result[:2000]}')

client.close()
