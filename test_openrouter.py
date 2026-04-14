import paramiko
import json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

# Direct test of OpenRouter API
test_cmd = """cd /root/quantum-wealth/backend && ./venv/bin/python -c "
import httpx, os, json
from dotenv import load_dotenv
load_dotenv()
key = os.environ.get('OPENROUTER_API_KEY', '')
print(f'Key: {key[:20]}...')

resp = httpx.post(
    'https://openrouter.ai/api/v1/chat/completions',
    headers={
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
    },
    json={
        'model': 'anthropic/claude-sonnet-4-20250514',
        'messages': [{'role': 'user', 'content': 'Say hello in 5 words'}],
        'max_tokens': 50
    },
    timeout=30
)
print(f'Status: {resp.status_code}')
print(f'Body: {resp.text[:500]}')
"
"""
stdin, stdout, stderr = client.exec_command(test_cmd, timeout=30)
print(stdout.read().decode('utf-8', errors='ignore'))
err = stderr.read().decode('utf-8', errors='ignore')
if err: print(f'Stderr: {err[-300:]}')

client.close()
