import paramiko
import time
import sys

# Fix encoding for Windows terminal
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

commands = [
    ('Build frontend with craco', 'cd /root/quantum-wealth/frontend && REACT_APP_BACKEND_URL=http://212.52.1.3:8001 npx craco build 2>&1 | tail -10'),
    ('Restart frontend', 'pm2 restart qw-frontend'),
]

for label, cmd in commands:
    print(f'[{label}]...')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    status = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(f'  Status: {status}')
    if out:
        print(f'  {out[-300:].strip()}')
    if status != 0 and err:
        print(f'  Error: {err[-200:].strip()}')

time.sleep(3)

# Quick check
stdin, stdout, stderr = client.exec_command('curl -s http://127.0.0.1:3000 | head -5')
out = stdout.read().decode('utf-8', errors='replace')
print(f'\nFrontend response: {out[:200]}')

client.close()
print('\n=== FRONTEND DEPLOY DONE ===')
