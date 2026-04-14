import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

commands = [
    # Pull latest code
    'cd /root/quantum-wealth && git pull',

    # Write .env with all keys
    """cat > /root/quantum-wealth/backend/.env << 'ENVEOF'
MONGO_URL=mongodb+srv://m7728724_db_user:zQLZ2jpZc3XmNanU@cluster0.vkakcoh.mongodb.net/?appName=Cluster0
DB_NAME=quantum_wealth
OPENROUTER_API_KEY=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
TINKOFF_TOKEN=t.HiRCmSCwYb1zRYWpXoTHhSUoY8Gm9ZIcyjv-YI729ON-d3nrdcAKEs--hUHpXBRTWZn5j6G4dYj2g1CUUME6eQ
ENVEOF""",

    # Install new Python dependencies
    'cd /root/quantum-wealth/backend && ./venv/bin/pip install yfinance ta tinkoff-investments httpx',

    # Restart backend
    'pm2 restart qw-backend',
]

for i, cmd in enumerate(commands):
    label = cmd.split('\n')[0][:70]
    print(f'[{i+1}/{len(commands)}] {label}')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    status = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    print(f'  Status: {status}')
    if out:
        # Print last 300 chars
        print(f'  Output: ...{out[-300:]}')
    if err and status != 0:
        print(f'  Error: {err[-300:]}')

print('\n-- Waiting 8s for backend to start --')
time.sleep(8)

stdin, stdout, stderr = client.exec_command('pm2 logs qw-backend --lines 15 --nostream')
out = stdout.read().decode('utf-8', errors='ignore')
for line in out.splitlines():
    try:
        print(line.encode('cp1251', errors='replace').decode('cp1251'))
    except:
        pass

client.close()
print('\n=== DEPLOY COMPLETE ===')
