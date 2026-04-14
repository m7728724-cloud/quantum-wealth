import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

test_cmd = """cd /root/quantum-wealth/backend && ./venv/bin/python -c "
import httpx, os, json
from dotenv import load_dotenv
load_dotenv()
key = os.environ.get('OPENROUTER_API_KEY', '')

resp = httpx.get('https://openrouter.ai/api/v1/models', headers={'Authorization': f'Bearer {key}'}, timeout=15)
models = resp.json().get('data', [])
claude_models = [m['id'] for m in models if 'claude' in m['id'].lower()]
print('Available Claude models:')
for m in sorted(claude_models):
    print(f'  {m}')
"
"""
stdin, stdout, stderr = client.exec_command(test_cmd, timeout=20)
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
