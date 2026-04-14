import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

# Update the key in .env
new_key = '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'
cmd = f"cd /root/quantum-wealth/backend && sed -i 's|^OPENROUTER_API_KEY=.*|OPENROUTER_API_KEY={new_key}|' .env && grep OPENROUTER .env"
_, stdout, _ = client.exec_command(cmd)
print('ENV:', stdout.read().decode('utf-8', errors='replace').strip())

# Restart backend
_, stdout, _ = client.exec_command('pm2 restart qw-backend')
stdout.channel.recv_exit_status()
print('Backend restarted')

# Test AI
import time; time.sleep(3)
_, stdout, _ = client.exec_command('''curl -s -X POST http://127.0.0.1:8001/api/auth/login -H "Content-Type: application/json" -d '{"username":"Vika-net1","password":"Dd19840622"}' | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))"''')
token = stdout.read().decode('utf-8', errors='replace').strip()

if token:
    _, stdout, _ = client.exec_command(f'curl -s -m 30 -X POST http://127.0.0.1:8001/api/ai/portfolio-insight -H "Authorization: Bearer {token}" -H "Content-Type: application/json" -d \'{{}}\' | python3 -c "import sys,json; d=json.load(sys.stdin); print(\'OK:\' if \'portfolio_summary\' in d else \'ERROR:\', str(d)[:200])"')
    print('AI test:', stdout.read().decode('utf-8', errors='replace').strip())

client.close()
print('DONE')
