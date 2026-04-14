import paramiko
import time
import json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

# Update .env with new Tinkoff token
env_cmd = """cat > /root/quantum-wealth/backend/.env << 'ENVEOF'
MONGO_URL=mongodb+srv://m7728724_db_user:zQLZ2jpZc3XmNanU@cluster0.vkakcoh.mongodb.net/?appName=Cluster0
DB_NAME=quantum_wealth
OPENROUTER_API_KEY=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
TINKOFF_TOKEN=t.iCXTp3CQjxnPHbb8p8HAaQmfErPXyAnBF_hMtefiBxc2p6EN_ptm_uiai6Mopd2YrH4hJfoSGjKKr9ETlq6uAQ
ENVEOF"""
stdin, stdout, stderr = client.exec_command(env_cmd)
stdout.channel.recv_exit_status()

# Restart backend
stdin, stdout, stderr = client.exec_command('pm2 restart qw-backend')
stdout.channel.recv_exit_status()
time.sleep(5)

# Login
login_cmd = "curl -s -X POST -H 'Content-Type: application/json' -d '{\"username\": \"Vika-net1\", \"password\": \"Dd19840622\"}' http://127.0.0.1:8001/api/auth/login"
stdin, stdout, stderr = client.exec_command(login_cmd)
token = json.loads(stdout.read().decode('utf-8'))['access_token']

# Test Tinkoff status
cmd = f"curl -s -H 'Authorization: Bearer {token}' http://127.0.0.1:8001/api/tinkoff/status"
stdin, stdout, stderr = client.exec_command(cmd)
print(f'Tinkoff Status: {stdout.read().decode("utf-8", errors="ignore")}')

# Sync portfolio
cmd = f"curl -s -X POST -H 'Authorization: Bearer {token}' http://127.0.0.1:8001/api/tinkoff/sync"
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
sync_result = stdout.read().decode('utf-8', errors='ignore')
print(f'\nTinkoff Sync ({len(sync_result)} bytes):')
print(sync_result[:800])

client.close()
