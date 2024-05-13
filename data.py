import json
import subprocess

def check_usr(data, usr):
    if usr not in data:
        data[usr] = {
            "balance" : 1000
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

def log(command, user, data):
    num_lines = int(subprocess.run(['wc', '-l', 'log.txt'], shell=False, check=True, capture_output=True, text=True).stdout.split(' ')[0])
    if num_lines > 250:
        subprocess.run(['sed', '-i', '1,/------/d', 'log.txt'], shell=False, check=True)
    with open('log.txt', 'a') as f:
        f.write(f'{command} was used by {user} with resulting data {json.dumps(data, indent=2)}\n')