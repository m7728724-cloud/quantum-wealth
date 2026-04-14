import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

check = """cd /root/quantum-wealth/backend && ./venv/bin/python -c "
import importlib
for m in ['tinvest', 'tinkoff_invest', 'tinkoff.invest']:
    try:
        mod = importlib.import_module(m.split('.')[0])
        print(f'OK: {m}')
    except ImportError as e:
        print(f'FAIL: {m} -> {e}')
# check pip list
import subprocess
r = subprocess.run(['./venv/bin/pip', 'list'], capture_output=True, text=True)
for line in r.stdout.splitlines():
    if 'tink' in line.lower() or 'invest' in line.lower():
        print(f'PIP: {line}')
"
"""
stdin, stdout, stderr = client.exec_command(check, timeout=15)
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
