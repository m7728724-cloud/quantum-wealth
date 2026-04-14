import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

# Try alternative tinkoff package names
commands = [
    'cd /root/quantum-wealth/backend && ./venv/bin/pip install tinkoff',
    'cd /root/quantum-wealth/backend && ./venv/bin/pip install "tinkoff[invest]"',
    'cd /root/quantum-wealth/backend && ./venv/bin/pip install tinkoff-invest',
]

for cmd in commands:
    print(f'Trying: {cmd.split("install ")[1]}')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    status = stdout.channel.recv_exit_status()
    if status == 0:
        print(f'  SUCCESS!')
        break
    else:
        err = stderr.read().decode('utf-8', errors='ignore')[-200:]
        print(f'  Failed: {err[:100]}')

# Search for available packages
print('\n-- Searching PyPI --')
stdin, stdout, stderr = client.exec_command("cd /root/quantum-wealth/backend && ./venv/bin/pip search tinkoff 2>&1 || ./venv/bin/pip index versions tinkoff-investments 2>&1 || echo 'search unavailable'")
print(stdout.read().decode('utf-8', errors='ignore')[:300])

# Check what tinkoff packages are available
stdin, stdout, stderr = client.exec_command("cd /root/quantum-wealth/backend && ./venv/bin/python -c \"import tinkoff; print(dir(tinkoff))\" 2>&1")
print(f'\nTinkoff module check: {stdout.read().decode("utf-8", errors="ignore")}')

client.close()
