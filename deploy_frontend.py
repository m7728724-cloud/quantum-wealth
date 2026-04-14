import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

commands = [
    ('Pull', 'cd /root/quantum-wealth && git pull'),
    ('Build frontend', 'cd /root/quantum-wealth/frontend && REACT_APP_BACKEND_URL=http://212.52.1.3:8001 npx react-scripts build 2>&1 | tail -5'),
    ('Restart frontend', 'pm2 restart qw-frontend'),
    ('Restart backend', 'pm2 restart qw-backend'),
]

for label, cmd in commands:
    print(f'[{label}]...')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=180)
    status = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='ignore')
    print(f'  Status: {status}')
    if out:
        print(f'  {out[-200:].strip()}')

time.sleep(5)

# Quick health check
stdin, stdout, stderr = client.exec_command('curl -s http://127.0.0.1:8001/api/health')
print(f'\nHealth: {stdout.read().decode("utf-8", errors="ignore")}')

client.close()
print('\n=== FRONTEND DEPLOY DONE ===')
