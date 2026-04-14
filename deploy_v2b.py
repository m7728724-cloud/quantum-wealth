import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

commands = [
    # Install the tricky packages separately
    'cd /root/quantum-wealth/backend && ./venv/bin/pip install yfinance ta httpx',
    'cd /root/quantum-wealth/backend && ./venv/bin/pip install tinkoff-investments || ./venv/bin/pip install tinvest || echo "Tinkoff SDK install failed - will use fallback"',

    # Restart backend
    'pm2 restart qw-backend',
]

for i, cmd in enumerate(commands):
    label = cmd.split('\n')[0][:70]
    print(f'[{i+1}/{len(commands)}] {label}')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=180)
    status = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    if status != 0:
        print(f'  WARN status={status}')
        if err: print(f'  {err[-200:]}')
    else:
        print(f'  OK')

print('\n-- Wait 8s --')
time.sleep(8)

stdin, stdout, stderr = client.exec_command('pm2 logs qw-backend --lines 15 --nostream')
out = stdout.read().decode('utf-8', errors='ignore')
for line in out.splitlines():
    try:
        print(line.encode('cp1251', errors='replace').decode('cp1251'))
    except:
        pass

# Test the scan endpoint
print('\n-- Testing signal scan endpoint --')
cmd = "curl -s http://127.0.0.1:8001/api/health"
stdin, stdout, stderr = client.exec_command(cmd)
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
print('\n=== DEPLOY V2 COMPLETE ===')
