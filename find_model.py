import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

# List available Claude models on OpenRouter
test_cmd = """cd /root/quantum-wealth/backend && ./venv/bin/python -c "
import httpx, os, json
from dotenv import load_dotenv
load_dotenv()
key = os.environ.get('OPENROUTER_API_KEY', '')

# Try different model names
models = [
    'anthropic/claude-3.5-sonnet',
    'anthropic/claude-3.5-sonnet:beta',
    'anthropic/claude-sonnet-4-20250514',
    'anthropic/claude-3-5-sonnet-20241022',
    'anthropic/claude-3.5-sonnet-20241022',
]

for model in models:
    resp = httpx.post(
        'https://openrouter.ai/api/v1/chat/completions',
        headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
        json={'model': model, 'messages': [{'role': 'user', 'content': 'hi'}], 'max_tokens': 5},
        timeout=15
    )
    status = 'OK' if resp.status_code == 200 else f'ERR {resp.status_code}'
    print(f'{model}: {status}')
    if resp.status_code == 200:
        break
"
"""
stdin, stdout, stderr = client.exec_command(test_cmd, timeout=60)
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
