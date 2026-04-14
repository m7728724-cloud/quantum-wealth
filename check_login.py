import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

cmd = "curl -s -X POST -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=Vika-net1&password=Dd19840622' http://127.0.0.1:8001/api/auth/login"
stdin, stdout, stderr = client.exec_command(cmd)
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
