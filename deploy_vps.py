import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.52.1.3', username='root', password='fCnv3M78p4ge')

commands = [
    "git clone https://Vika-net1:Dd19840622@github.com/m7728724-cloud/quantum-wealth.git /root/quantum-wealth || echo 'Repo already cloned'",
    "cd /root/quantum-wealth/backend && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt",
    "cd /root/quantum-wealth/frontend && npm install --legacy-peer-deps",
    f"echo 'MONGO_URL=mongodb+srv://m7728724_db_user:zQLZ2jpZc3XmNanU@cluster0.vkakcoh.mongodb.net/?appName=Cluster0\\nDB_NAME=quantum_wealth' > /root/quantum-wealth/backend/.env"
]

for cmd in commands:
    print(f"Executing: {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print("OUT:", out)
    if err: print("ERR:", err)

client.close()
