import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

for label, cmd in [
    ('Pull', 'cd /root/quantum-wealth && git pull'),
    ('Build', 'cd /root/quantum-wealth/frontend && REACT_APP_BACKEND_URL=http://212.52.1.3:8001 npx craco build 2>&1 | tail -3'),
    ('Restart', 'pm2 restart qw-frontend'),
]:
    print(f'[{label}]...')
    _, stdout, _ = client.exec_command(cmd, timeout=300)
    status = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace')
    print(f'  {status} | {out[-150:].strip()}')

client.close()
print('DONE')
