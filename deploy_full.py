import paramiko
import time
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

steps = [
    ('Git pull', 'cd /root/quantum-wealth && git pull'),
    ('Restart backend', 'cd /root/quantum-wealth && pm2 restart qw-backend'),
    ('Build frontend', 'cd /root/quantum-wealth/frontend && REACT_APP_BACKEND_URL=http://212.52.1.3:8001 npx craco build 2>&1 | tail -8'),
    ('Restart frontend', 'pm2 restart qw-frontend'),
]

for label, cmd in steps:
    print(f'[{label}]...')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    status = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(f'  Exit: {status}')
    if out:
        # Filter out pm2 table characters
        clean = out.replace('\u2502', '|').replace('\u250c', '+').replace('\u2510', '+').replace('\u2514', '+').replace('\u2518', '+').replace('\u2500', '-').replace('\u251c', '+').replace('\u2524', '+').replace('\u253c', '+').replace('\u252c', '+').replace('\u2534', '+')
        print(f'  {clean[-400:].strip()}')
    if status != 0 and err:
        print(f'  ERR: {err[-200:].strip()}')

time.sleep(3)
# Health check
stdin, stdout, stderr = client.exec_command('curl -s http://127.0.0.1:8001/api/health')
print(f'\nBackend health: {stdout.read().decode("utf-8", errors="replace")}')

# Test enriched endpoint
stdin, stdout, stderr = client.exec_command('''curl -s -X POST http://127.0.0.1:8001/api/auth/login -H "Content-Type: application/json" -d '{"username":"Vika-net1","password":"Dd19840622"}' | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token','NO_TOKEN')[:30])"''')
token = stdout.read().decode('utf-8', errors='replace').strip()
print(f'Token: {token}...')

if token and token != 'NO_TOKEN':
    stdin, stdout, stderr = client.exec_command(f'curl -s http://127.0.0.1:8001/api/portfolio/holdings-enriched -H "Authorization: Bearer {token}" | python3 -c "import sys,json; d=json.load(sys.stdin); s=d.get(\'summary\',{{}}); print(f\'Positions: {{s.get(\\\"positions_count\\\",0)}}, Invested: {{s.get(\\\"total_invested\\\",0)}}, Current: {{s.get(\\\"total_current\\\",0)}}, P/L: {{s.get(\\\"total_pl\\\",0)}}\")"')
    print(f'Enriched: {stdout.read().decode("utf-8", errors="replace").strip()}')

client.close()
print('\n=== FULL DEPLOY COMPLETE ===')
