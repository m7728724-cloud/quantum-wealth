import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

# First login to get token
login_cmd = "curl -s -X POST -H 'Content-Type: application/json' -d '{\"username\": \"Vika-net1\", \"password\": \"Dd19840622\"}' http://127.0.0.1:8001/api/auth/login"
stdin, stdout, stderr = client.exec_command(login_cmd)
import json
login_resp = json.loads(stdout.read().decode('utf-8'))
token = login_resp['access_token']
print(f'Token: {token[:30]}...')

# Test signal scan
scan_cmd = f"curl -s -H 'Authorization: Bearer {token}' http://127.0.0.1:8001/api/signals/scan"
stdin, stdout, stderr = client.exec_command(scan_cmd, timeout=60)
scan_resp = stdout.read().decode('utf-8', errors='ignore')
print(f'\nScan response ({len(scan_resp)} bytes):')
print(scan_resp[:1000])

# Test Tinkoff status
tink_cmd = f"curl -s -H 'Authorization: Bearer {token}' http://127.0.0.1:8001/api/tinkoff/status"
stdin, stdout, stderr = client.exec_command(tink_cmd)
print(f'\nTinkoff status: {stdout.read().decode("utf-8", errors="ignore")}')

client.close()
