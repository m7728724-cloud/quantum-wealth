import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

# Check what import name the tinkoff-invest package uses
check = """cd /root/quantum-wealth/backend && ./venv/bin/python -c "
import pkg_resources
for p in pkg_resources.working_set:
    if 'tinkoff' in p.project_name.lower() or 'tinvest' in p.project_name.lower() or 'invest' in p.project_name.lower():
        print(f'{p.project_name} == {p.version}')
print('---')
try:
    import tinvest
    print('tinvest module found')
except ImportError:
    print('tinvest NOT found')
try:
    from tinkoff.invest import Client
    print('tinkoff.invest.Client found')
except ImportError as e:
    print(f'tinkoff.invest.Client NOT found: {e}')
try:
    import tinkoff_invest
    print('tinkoff_invest module found')
except ImportError:
    print('tinkoff_invest NOT found')
"
"""
stdin, stdout, stderr = client.exec_command(check, timeout=15)
print(stdout.read().decode('utf-8', errors='ignore'))
print(stderr.read().decode('utf-8', errors='ignore')[-300:])

client.close()
