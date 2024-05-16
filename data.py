import json
import subprocess
import gzip
import base64

def check_usr(data, ctx):
    id = str(ctx.author.id)
    if id not in data["users"]:
        data["users"][id] = {
            "balance" : 1000,
            "name" : ctx.author.global_name or ctx.author.name
        }
    save(data)

def save(data):
    json_string = json.dumps(data, indent=2)
    with open('data.json', 'w') as f:
        f.write(json_string)

def load():
    with open('data.json', 'r') as f:
        try:
            data = json.loads(f.read())
            return data
        except json.JSONDecodeError:
            return {}

def log(message, data):
    num_lines = int(subprocess.run(['wc', '-l', 'log.txt'], shell=False, check=True, capture_output=True, text=True).stdout.split(' ')[0])
    if num_lines > 1000:
        subprocess.run(['sed', '-i', '1,/------/d', 'log.txt'], shell=False, check=True)
    json_str = json.dumps(data, indent=2)
    compressed_bytes = gzip.compress(json_str.encode('utf-8'))
    compressed_base64 = base64.b64encode(compressed_bytes).decode('utf-8')
    with open('log.txt', 'a') as f:
        f.write(f'{message} - {compressed_base64}\n')