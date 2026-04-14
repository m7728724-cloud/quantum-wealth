import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

cmd_backend = "curl -s -X POST -H 'Content-Type: application/json' -d '{\"username\": \"Vika-net1\", \"password\": \"Dd19840622\"}' http://127.0.0.1:8001/api/auth/login"
stdin, stdout, stderr = client.exec_command(cmd_backend)
print("Backend Response: ", stdout.read().decode('utf-8'))

cmd_frontend = "curl -s -X POST -H 'Content-Type: application/json' -d '{\"username\": \"Vika-net1\", \"password\": \"Dd19840622\"}' http://127.0.0.1:3000/api/auth/login"
stdin, stdout, stderr = client.exec_command(cmd_frontend)
print("Frontend Proxy Response: ", stdout.read().decode('utf-8'))

client.close()
