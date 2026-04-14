import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

commands = [
    'cd /root/quantum-wealth/backend && ./venv/bin/pip install requests aiohttp openai litellm google-genai pandas numpy pyyaml pydantic-settings python-multipart email-validator passlib bcrypt',
    'pm2 restart qw-backend',
    'pm2 logs qw-backend --lines 30 --nostream'
]

for cmd in commands:
    print(f'-- {cmd[:70]} --')
    stdin, stdout, stderr = client.exec_command(cmd)
    status = stdout.channel.recv_exit_status()
    print(f'Done {status}')
    out = stdout.read().decode('utf-8', errors='ignore').encode('cp1251', errors='ignore').decode('cp1251')
    if out: print(out[-1500:])

client.close()
