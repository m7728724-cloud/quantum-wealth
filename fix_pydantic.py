import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

commands = [
    # Fix pydantic version conflict
    'cd /root/quantum-wealth/backend && ./venv/bin/pip install "pydantic>=2.0,<2.13" "fastapi==0.110.1"',
    
    # Restart backend
    'pm2 restart qw-backend',
]

for i, cmd in enumerate(commands):
    label = cmd[:70]
    print(f'[{i+1}/{len(commands)}] {label}')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    status = stdout.channel.recv_exit_status()
    print(f'  Status: {status}')

print('\n-- Wait 6s --')
time.sleep(6)

stdin, stdout, stderr = client.exec_command('pm2 logs qw-backend --lines 10 --nostream')
out = stdout.read().decode('utf-8', errors='ignore')
for line in out.splitlines():
    try:
        print(line.encode('cp1251', errors='replace').decode('cp1251'))
    except:
        pass

# Quick health test
stdin, stdout, stderr = client.exec_command('curl -s http://127.0.0.1:8001/api/health')
print('\nHealth:', stdout.read().decode('utf-8', errors='ignore'))

client.close()
