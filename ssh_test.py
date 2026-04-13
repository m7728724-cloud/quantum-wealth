import paramiko
try:
    print("Connecting...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')
    stdin, stdout, stderr = client.exec_command('uname -a && cat /etc/os-release && ss -tulpn')
    print("STDOUT:", stdout.read().decode())
    client.close()
except Exception as e:
    print("ERROR:", str(e))
