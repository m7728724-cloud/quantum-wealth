import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

steps = [
    ('Git pull', 'cd /root/quantum-wealth && git pull'),
    ('Restart backend', 'cd /root/quantum-wealth && pm2 restart qw-backend && sleep 3'),
    ('Build frontend', 'cd /root/quantum-wealth/frontend && REACT_APP_BACKEND_URL=http://212.52.1.3:8001 npx craco build 2>&1 | tail -5'),
    ('Restart frontend', 'pm2 restart qw-frontend'),
]

for label, cmd in steps:
    print(f'\n[{label}]...')
    _, stdout, stderr = client.exec_command(cmd, timeout=300)
    status = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(f'  Exit: {status}')
    if out.strip(): print(f'  {out[-300:].strip()}')
    if status != 0 and err.strip(): print(f'  ERR: {err[-200:].strip()}')

time.sleep(3)

# Check backend health
_, stdout, _ = client.exec_command('curl -s http://127.0.0.1:8001/api/health')
print(f'\nHealth: {stdout.read().decode("utf-8", errors="replace")}')

# Test login + check role
_, stdout, _ = client.exec_command('''curl -s -X POST http://127.0.0.1:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"Vika-net1","password":"Dd19840622"}' | python3 -c "
import sys,json
d=json.load(sys.stdin)
token=d.get('access_token','')
print('Token:', token[:30]+'...' if token else 'FAILED')
"''')
print('Auth:', stdout.read().decode('utf-8', errors='replace').strip())

# Test admin users endpoint
_, stdout, _ = client.exec_command('''TOKEN=$(curl -s -X POST http://127.0.0.1:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"Vika-net1","password":"Dd19840622"}' | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))")
curl -s http://127.0.0.1:8001/api/users -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys,json
d=json.load(sys.stdin)
if isinstance(d,list): print(f'Users endpoint OK: {len(d)} users')
else: print('Response:', str(d)[:200])
"''')
print('Admin users:', stdout.read().decode('utf-8', errors='replace').strip())

client.close()
print('\n=== DEPLOY COMPLETE ===')
